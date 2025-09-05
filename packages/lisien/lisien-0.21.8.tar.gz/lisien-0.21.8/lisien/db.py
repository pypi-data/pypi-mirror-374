# This file is part of Lisien, a framework for life simulation games.
# Copyright (c) Zachary Spector, public@zacharyspector.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import inspect
import os
import sys
from abc import ABC, abstractmethod
from collections import UserDict, defaultdict
from contextlib import contextmanager
from functools import cached_property, partial, partialmethod, wraps
from itertools import starmap
from operator import itemgetter
from queue import Queue
from sqlite3 import IntegrityError as LiteIntegrityError
from sqlite3 import OperationalError as LiteOperationalError
from threading import Lock, Thread
from types import MethodType
from typing import Any, Iterator, Literal, Optional

from sqlalchemy import (
	BLOB,
	BOOLEAN,
	FLOAT,
	INT,
	TEXT,
	MetaData,
	Select,
	create_engine,
)
from sqlalchemy.exc import IntegrityError as AlchemyIntegrityError
from sqlalchemy.exc import OperationalError as AlchemyOperationalError

from .alchemy import gather_sql, meta
from .exc import KeyframeError
from .types import (
	ActionFuncName,
	Branch,
	CharName,
	EdgeKeyframe,
	EdgeRowType,
	EdgeValRowType,
	GraphValKeyframe,
	GraphValRowType,
	Key,
	NodeKeyframe,
	NodeName,
	NodeRowType,
	NodeValRowType,
	Plan,
	PrereqFuncName,
	RuleBig,
	RulebookKeyframe,
	RulebookName,
	RulebookPriority,
	RulebookTypeStr,
	RuleKeyframe,
	RuleName,
	RuleNeighborhood,
	Tick,
	Time,
	TimeWindow,
	TriggerFuncName,
	Turn,
	UniversalKeyframe,
	Value,
)
from .util import ELLIPSIS, EMPTY, garbage
from .wrap import DictWrapper, ListWrapper, SetWrapper

IntegrityError = (LiteIntegrityError, AlchemyIntegrityError)
OperationalError = (LiteOperationalError, AlchemyOperationalError)


SCHEMAVER_B = b"\xb6_lisien_schema_version"
SCHEMA_VERSION = b"\x01"


class GlobalKeyValueStore(UserDict):
	"""A dict-like object that keeps its contents in a table.

	Mostly this is for holding the current branch and revision.

	"""

	def __init__(self, qe: AbstractQueryEngine, data: dict):
		self.qe = qe
		super().__init__()
		self.data = data

	def __getitem__(self, k: Key) -> Value:
		ret = super().__getitem__(k)
		if ret is ...:
			raise KeyError(k)
		if isinstance(ret, dict):
			return DictWrapper(
				lambda: super().__getitem__(k),
				lambda v: self.__setitem__(k, v),
				self,
				k,
			)
		elif isinstance(ret, list):
			return ListWrapper(
				lambda: super().__getitem__(k),
				lambda v: self.__setitem__(k, v),
				self,
				k,
			)
		elif isinstance(ret, set):
			return SetWrapper(
				lambda: super().__getitem__(k),
				lambda v: self.__setitem__(k, v),
				self,
				k,
			)
		return ret

	def __setitem__(self, k: Key, v: Value):
		if hasattr(v, "unwrap"):
			v = v.unwrap()
		self.qe.global_set(k, v)
		super().__setitem__(k, v)

	def __delitem__(self, k: Key):
		super().__delitem__(k)
		self.qe.global_del(k)


class ConnectionHolder:
	strings: dict
	lock: Lock
	existence_lock = Lock()
	_inq: Queue
	_outq: Queue

	@cached_property
	def logger(self):
		if "kivy" in sys.modules:
			from kivy.logger import Logger

			return Logger
		else:
			from logging import getLogger

			return getLogger(self.__class__.__name__)

	@abstractmethod
	def run(self):
		pass

	@abstractmethod
	def initdb(self):
		pass

	@abstractmethod
	def commit(self):
		pass

	@abstractmethod
	def close(self):
		pass


class ParquetDBHolder(ConnectionHolder):
	@cached_property
	def schema(self):
		import pyarrow as pa

		sql2parquetdb_type = {
			BLOB: pa.binary,
			FLOAT: pa.float64,
			TEXT: pa.string,
			INT: pa.int64,
			BOOLEAN: pa.bool_,
		}

		return {
			name: [
				(column.name, sql2parquetdb_type[type(column.type)]())
				for column in table.columns
			]
			for (name, table) in meta.tables.items()
		}

	initial = {
		"global": [
			{
				"key": b"\xb6_lisien_schema_version",
				"value": b"\x01",
			},
			{"key": b"\xabmain_branch", "value": b"\xa5trunk"},
			{"key": b"\xa6branch", "value": b"\xa5trunk"},
			{"key": b"\xa4turn", "value": b"\x00"},
			{"key": b"\xa4tick", "value": b"\x00"},
			{"key": b"\xa8language", "value": b"\xa3eng"},
		],
		"branches": [
			{
				"branch": "trunk",
				"parent": None,
				"parent_turn": 0,
				"parent_tick": 0,
				"end_turn": 0,
				"end_tick": 0,
			}
		],
	}
	_inq: Queue
	_outq: Queue

	def __init__(self, path: str | os.PathLike, inq: Queue, outq: Queue):
		self._inq = inq
		self._outq = outq
		self._schema = {}
		self._path = path
		self.lock = Lock()
		self.existence_lock.acquire(timeout=1)

	@staticmethod
	def echo(*args, **_):
		return args

	def commit(self):
		pass

	def close(self):
		if not self._outq.empty():
			self._outq.join()
		self.existence_lock.release()

	def initdb(self):
		initial = self.initial
		for table, schema in self.schema.items():
			schema = self._get_schema(table)
			db = self._get_db(table)
			if db.dataset_exists():
				continue
			if table in initial:
				db.create(
					initial[table],
					schema=schema,
				)
		glob_d = {d["key"]: d["value"] for d in self.dump("global")}
		if SCHEMAVER_B not in glob_d:
			glob_d[SCHEMAVER_B] = SCHEMA_VERSION
			self.set_global(SCHEMAVER_B, SCHEMA_VERSION)
		elif glob_d[SCHEMAVER_B] != b"\x01":
			return ValueError(
				f"Unsupported database schema version", glob_d[SCHEMAVER_B]
			)
		return glob_d

	def _get_db(self, table: str):
		from parquetdb import ParquetDB

		return ParquetDB(os.path.join(self._path, table))

	def insert(self, table: str, data: list) -> None:
		self._get_db(table).create(data, schema=self._schema[table])

	def keyframes_graphs_delete(self, data: list[dict]):
		import pyarrow as pa
		from pyarrow import compute as pc

		db = self._get_db("keyframes")
		todel = []
		for d in data:
			found: pa.Table = db.read(
				columns=["id"],
				filters=[
					pc.field("graph") == d["graph"],
					pc.field("branch") == d["branch"],
					pc.field("turn") == d["turn"],
					pc.field("tick") == d["tick"],
				],
			)
			if found.num_rows > 0:
				todel.extend(id_.as_py() for id_ in found["id"])
		if todel:
			db.delete(todel)

	def delete_keyframe(self, branch: Branch, turn: Turn, tick: Tick):
		from pyarrow import compute as pc

		filters = [
			pc.field("branch") == branch,
			pc.field("turn") == turn,
			pc.field("tick") == tick,
		]

		self._get_db("keyframes").delete(filters=filters)
		self._get_db("keyframes_graphs").delete(filters=filters)
		self._get_db("keyframe_extensions").delete(filters=filters)

	def all_keyframe_times(self):
		return {
			(d["branch"], d["turn"], d["tick"])
			for d in self._get_db("keyframes")
			.read(columns=["branch", "turn", "tick"])
			.to_pylist()
		}

	def truncate_all(self):
		for table in self.schema:
			db = self._get_db(table)
			if db.dataset_exists():
				db.drop_dataset()

	def del_units_after(self, many):
		from pyarrow import compute as pc

		db = self._get_db("units")
		ids = []
		for character, graph, node, branch, turn, tick in many:
			for d in db.read(
				filters=[
					pc.field("character_graph") == character,
					pc.field("unit_graph") == graph,
					pc.field("unit_node") == node,
					pc.field("branch") == branch,
					pc.field("turn") >= turn,
				],
				columns=["id", "turn", "tick"],
			).to_pylist():
				if d["turn"] == turn:
					if d["tick"] >= tick:
						ids.append(d["id"])
				else:
					ids.append(d["id"])
		if ids:
			db.delete(ids)

	def del_things_after(self, many):
		from pyarrow import compute as pc

		db = self._get_db("things")
		ids = []
		for character, thing, branch, turn, tick in many:
			for d in db.read(
				filters=[
					pc.field("character") == character,
					pc.field("thing") == thing,
					pc.field("branch") == branch,
					pc.field("turn") >= turn,
				],
				columns=["id", "turn", "tick"],
			).to_pylist():
				if d["turn"] == turn:
					if d["tick"] >= tick:
						ids.append(d["id"])
				else:
					ids.append(d["id"])
		if ids:
			db.delete(ids)

	def dump(self, table: str) -> list:
		return [
			d
			for d in self._get_db(table).read().to_pylist()
			if d.keys() - {"id"}
		]

	def rowcount(self, table: str) -> int:
		return self._get_db(table).read().num_rows

	def bookmark_items(self) -> list[tuple[Key, Time]]:
		return [
			(d["name"], (d["branch"], d["turn"], d["tick"]))
			for d in self.dump("bookmarks")
		]

	def set_bookmark(self, key: bytes, branch: Branch, turn: Turn, tick: Tick):
		import pyarrow.compute as pc

		db = self._get_db("bookmarks")
		schema = self._get_schema("bookmarks")
		try:
			id_ = db.read(
				filters=[pc.field("key") == pc.scalar(key)], columns=["id"]
			)["id"][0]
		except IndexError:
			db.create(
				[{"key": key, "branch": branch, "turn": turn, "tick": tick}],
				schema=schema,
			)
			return
		db.update(
			[
				{
					"id": id_,
					"key": key,
					"branch": branch,
					"turn": turn,
					"tick": tick,
				}
			],
			schema=schema,
		)

	def del_bookmark(self, key: bytes):
		import pyarrow.compute as pc

		self._get_db("bookmarks").delete(
			filters=[pc.field("key") == pc.scalar(key)]
		)

	def rulebooks(self) -> set[RulebookName]:
		return set(
			self._get_db("rulebooks").read(columns=["rulebook"])["rulebook"]
		)

	def graphs(self) -> set[CharName]:
		return set(
			name.as_py()
			for name in self._get_db("graphs").read(columns=["graph"])["graph"]
		)

	def list_graphs_to_end(self, branch: Branch, turn: Turn, tick: Tick):
		from pyarrow import compute as pc

		data = (
			self._get_db("graphs").read(
				filters=[
					pc.field("branch") == branch,
					pc.field("turn") >= turn,
				],
			)
		).to_pylist()
		return [
			d
			for d in data
			if d["turn"] > turn or (d["turn"] == turn and d["tick"] >= tick)
		]

	def list_graphs_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	):
		from pyarrow import compute as pc

		data = (
			self._get_db("graphs").read(
				filters=[
					pc.field("branch") == branch,
					pc.field("turn") >= turn_from,
					pc.field("turn") <= turn_to,
				]
			)
		).to_pylist()
		return [
			d
			for d in data
			if (
				d["turn"] > turn_from
				or (d["turn"] == turn_from and d["tick"] >= tick_from)
			)
			and (
				d["turn"] < turn_to
				or (d["turn"] == turn_to and d["tick"] <= tick_to)
			)
		]

	def list_keyframes(self) -> list:
		return (
			self._get_db("keyframes")
			.read(
				columns=["graph", "branch", "turn", "tick"],
			)
			.to_pylist()
		)

	def get_keyframe(
		self, graph: bytes, branch: Branch, turn: Turn, tick: Tick
	) -> tuple[bytes, bytes, bytes] | None:
		from pyarrow import compute as pc

		rec = self._get_db("keyframes_graphs").read(
			filters=[
				pc.field("graph") == pc.scalar(graph),
				pc.field("branch") == pc.scalar(branch),
				pc.field("turn") == pc.scalar(turn),
				pc.field("tick") == pc.scalar(tick),
			],
			columns=["nodes", "edges", "graph_val"],
		)
		if not rec.num_rows:
			return None
		if rec.num_rows > 1:
			raise ValueError("Ambiguous keyframe, probably corrupt table")
		return (
			rec["nodes"][0].as_py(),
			rec["edges"][0].as_py(),
			rec["graph_val"][0].as_py(),
		)

	class InsertException(ValueError):
		pass

	def insert1(self, table: str, data: dict):
		try:
			return self.insert(table, [data])
		except Exception as ex:
			return ex

	def set_rulebook_on_character(
		self,
		rbtyp: RulebookTypeStr,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		self.insert1(
			f"{rbtyp}_rulebook",
			{
				"character": char,
				"branch": branch,
				"turn": turn,
				"tick": tick,
				"rulebook": rb,
			},
		)

	def graph_exists(self, graph: bytes) -> bool:
		from pyarrow import compute as pc

		return bool(
			self._get_db("graphs")
			.read(
				filters=[pc.field("graph") == pc.scalar(graph)], columns=["id"]
			)
			.num_rows
		)

	def get_global(self, key: bytes) -> bytes:
		from pyarrow import compute as pc

		ret = self._get_db("global").read(
			filters=[pc.field("key") == key],
		)
		if ret:
			return ret["value"][0].as_py()
		return ELLIPSIS

	def _get_schema(self, table):
		import pyarrow as pa

		if table in self._schema:
			return self._schema[table]
		ret = self._schema[table] = pa.schema(self.schema[table])
		return ret

	def set_global(self, key: bytes, value: bytes):
		id_ = self.field_get_id("global", "key", key)
		schema = self._get_schema("global")
		db = self._get_db("global")
		if id_ is None:
			return db.create(
				[{"key": key, "value": value}],
				schema=schema,
			)
		return db.update([{"id": id_, "value": value}])

	def del_global(self, key: bytes):
		from pyarrow import compute as pc

		self._get_db("global").delete(filters=[pc.field("key") == key])

	def global_keys(self):
		return [
			d["key"]
			for d in self._get_db("global")
			.read("global", columns=["key"])
			.to_pylist()
		]

	def field_get_id(self, table, keyfield, value):
		from pyarrow import compute as pc

		return self.filter_get_id(table, filters=[pc.field(keyfield) == value])

	def filter_get_id(self, table, filters):
		ret = self._get_db(table).read(filters=filters, columns=["id"])
		if ret:
			return ret["id"][0].as_py()

	def update_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
		end_turn: Turn,
		end_tick: Tick,
	) -> None:
		id_ = self.field_get_id("branches", "branch", branch)
		if id_ is None:
			raise KeyError(f"No branch: {branch}")
		self._get_db("branches").update(
			[
				{
					"id": id_,
					"parent": parent,
					"parent_turn": parent_turn,
					"parent_tick": parent_tick,
					"end_turn": end_turn,
					"end_tick": end_tick,
				}
			],
		)

	def set_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
		end_turn: Turn,
		end_tick: Tick,
	) -> None:
		try:
			self.update_branch(
				branch, parent, parent_turn, parent_tick, end_turn, end_tick
			)
		except KeyError:
			self.insert1(
				"branches",
				{
					"branch": branch,
					"parent": parent,
					"parent_turn": parent_turn,
					"parent_tick": parent_tick,
					"end_turn": end_turn,
					"end_tick": end_tick,
				},
			)

	def have_branch(self, branch: Branch) -> bool:
		from pyarrow import compute as pc

		return bool(
			self._get_db("branches")
			.read("branches", filters=[pc.field("branch") == branch])
			.rowcount
		)

	def update_turn(
		self, branch: Branch, turn: Turn, end_tick: Tick, plan_end_tick: Tick
	):
		from pyarrow import compute as pc

		id_ = self.filter_get_id(
			"turns", [pc.field("branch") == branch, pc.field("turn") == turn]
		)
		if id_ is None:
			return self._get_db("turns").create(
				[
					{
						"branch": branch,
						"turn": turn,
						"end_tick": end_tick,
						"plan_end_tick": plan_end_tick,
					}
				],
			)
		return self._get_db("turns").update(
			[
				{
					"id": id_,
					"end_tick": end_tick,
					"plan_end_tick": plan_end_tick,
				}
			]
		)

	def set_turn(
		self, branch: Branch, turn: Turn, end_tick: Tick, plan_end_tick: Tick
	) -> None:
		from pyarrow import ArrowInvalid

		try:
			self.update_turn(branch, turn, end_tick, plan_end_tick)
		except (ArrowInvalid, IndexError):
			self._get_db("turns").create(
				{
					"branch": branch,
					"turn": turn,
					"end_tick": end_tick,
					"plan_end_tick": plan_end_tick,
				}
			)

	def load_universals_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_universals_tick_to_end(branch, turn_from, tick_from)
		)

	def _table_columns(self, table: str) -> list[str]:
		return ["id"] + list(map(itemgetter(0), self.schema[table]))

	def _iter_part_tick_to_end(
		self, table: str, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[dict]:
		from pyarrow import compute as pc

		db = self._get_db(table)
		for d in db.read(
			filters=[
				pc.field("branch") == branch,
				pc.field("turn") >= turn_from,
			],
			columns=self._table_columns(table),
		).to_pylist():
			if d["turn"] == turn_from:
				if d["tick"] >= tick_from:
					yield d
			else:
				yield d

	def _iter_universals_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_end(
			"universals", branch, turn_from, tick_from
		):
			try:
				yield d["key"], d["turn"], d["tick"], d["value"]
			except KeyError:
				continue

	def _iter_part_tick_to_tick(
		self,
		table: str,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[dict]:
		from pyarrow import compute as pc

		db = self._get_db(table)
		if turn_from == turn_to:
			return iter(
				db.read(
					filters=[
						pc.field("branch") == branch,
						pc.field("turn") == turn_from,
						pc.field("tick") >= tick_from,
						pc.field("tick") < tick_from,
					],
					columns=self._table_columns(table),
				).to_pylist()
			)
		else:
			for d in db.read(
				filters=[
					pc.field("branch") == branch,
					pc.field("turn") >= turn_from,
					pc.field("turn") <= turn_to,
				],
				columns=self._table_columns(table),
			).to_pylist():
				if d["turn"] == turn_from:
					if d["tick"] >= tick_from:
						yield d
				elif d["turn"] == turn_to:
					if d["tick"] < tick_to:
						yield d
				else:
					yield d

	def load_universals_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, Turn, Tick, bytes]]:
		return [
			(d["key"], d["turn"], d["tick"], d["value"])
			for d in self._iter_part_tick_to_tick(
				"universals", branch, turn_from, tick_from, turn_to, tick_to
			)
		]

	def load_things_tick_to_end(self, *args, **kwargs):
		if len(args) + len(kwargs) == 4:
			return self._load_things_tick_to_end_character(*args, **kwargs)
		else:
			return self._load_things_tick_to_end_all(*args, **kwargs)

	def _load_things_tick_to_end_all(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_things_tick_to_end_all(branch, turn_from, tick_from)
		)

	def _iter_things_tick_to_end_all(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_end(
			"things", branch, turn_from, tick_from
		):
			yield (
				d["character"],
				d["thing"],
				d["turn"],
				d["tick"],
				d["location"],
			)

	def _load_things_tick_to_end_character(
		self,
		character: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
	) -> list[tuple[bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_things_tick_to_end_character(
				character, branch, turn_from, tick_from
			)
		)

	def _iter_things_tick_to_end_character(
		self,
		character: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
	) -> Iterator[tuple[bytes, Turn, Tick, bytes]]:
		from pyarrow import compute as pc

		for d in (
			self._get_db("things")
			.read(
				filters=[
					pc.field("character") == character,
					pc.field("branch") == branch,
					pc.field("turn") >= turn_from,
				],
			)
			.to_pylist()
		):
			if d["turn"] == turn_from:
				if d["tick"] >= tick_from:
					yield d["thing"], d["turn"], d["tick"], d["location"]
			else:
				yield d["thing"], d["turn"], d["tick"], d["location"]

	def load_things_tick_to_tick(self, *args, **kwargs):
		if len(args) + len(kwargs) == 6:
			return self._load_things_tick_to_tick_character(*args, **kwargs)
		else:
			return self._load_things_tick_to_tick_all(*args, **kwargs)

	def _load_things_tick_to_tick_all(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_things_tick_to_tick_all(
				branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_things_tick_to_tick_all(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_tick(
			"things", branch, turn_from, tick_from, turn_to, tick_to
		):
			yield (
				d["character"],
				d["thing"],
				d["turn"],
				d["tick"],
				d["location"],
			)

	def _load_things_tick_to_tick_character(
		self,
		character: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_things_tick_to_tick_character(
				character, branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_things_tick_to_tick_character(
		self,
		character: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	):
		from pyarrow import compute as pc

		db = self._get_db("things")
		if turn_from == turn_to:
			for d in db.read(
				filters=[
					pc.field("character") == character,
					pc.field("branch") == branch,
					pc.field("turn") == turn_from,
					pc.field("tick") >= tick_from,
					pc.field("tick") <= tick_to,
				],
			).to_pylist():
				yield d["thing"], d["turn"], d["tick"], d["location"]
		else:
			for d in db.read(
				filters=[
					pc.field("character") == character,
					pc.field("branch") == branch,
					pc.field("turn_from") >= turn_from,
					pc.field("turn_to") <= turn_to,
				],
			).to_pylist():
				if d["turn"] == turn_from:
					if d["tick"] >= tick_from:
						yield d["thing"], d["turn"], d["tick"], d["location"]
				elif d["turn"] == turn_to:
					if d["tick"] <= tick_to:
						yield d["thing"], d["turn"], d["tick"], d["location"]
				else:
					yield d["thing"], d["turn"], d["tick"], d["location"]

	def load_graph_val_tick_to_end(self, *args, **kwargs):
		if len(args) + len(kwargs) == 4:
			return self._load_graph_val_tick_to_end_graph(*args, **kwargs)
		else:
			return self._load_graph_val_tick_to_end_all(*args, **kwargs)

	def _load_graph_val_tick_to_end_all(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_graph_val_tick_to_end_all(branch, turn_from, tick_from)
		)

	def _iter_graph_val_tick_to_end_all(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_end(
			"graph_val", branch, turn_from, tick_from
		):
			yield (
				d["graph"],
				d["key"],
				d["turn"],
				d["tick"],
				d["value"],
			)

	def _load_graph_val_tick_to_end_graph(
		self, graph: bytes, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_graph_val_tick_to_end_graph(
				graph, branch, turn_from, tick_from
			)
		)

	def _iter_graph_val_tick_to_end_graph(
		self, graph: bytes, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, Turn, Tick, bytes]]:
		from pyarrow import compute as pc

		for d in (
			self._get_db("graph_val")
			.read(
				filters=[
					pc.field("graph") == graph,
					pc.field("branch") == branch,
					pc.field("turn") >= turn_from,
				],
			)
			.to_pylist()
		):
			if d["turn"] == turn_from:
				if d["tick"] >= tick_from:
					yield d["key"], d["turn"], d["tick"], d["value"]
			else:
				yield d["key"], d["turn"], d["tick"], d["value"]

	def load_graph_val_tick_to_tick(self, *args, **kwargs):
		if len(args) + len(kwargs) == 6:
			return self._load_graph_val_tick_to_tick_graph(*args, **kwargs)
		else:
			return self._load_graph_val_tick_to_tick_all(*args, **kwargs)

	def _load_graph_val_tick_to_tick_all(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_graph_val_tick_to_tick_all(
				branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_graph_val_tick_to_tick_all(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_tick(
			"graph_val", branch, turn_from, tick_from, turn_to, tick_to
		):
			yield d["graph"], d["key"], d["turn"], d["tick"], d["value"]

	def _load_graph_val_tick_to_tick_graph(
		self,
		graph: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_graph_val_tick_to_tick(
				graph, branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_graph_val_tick_to_tick(
		self,
		graph: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_tick(
			"graph_val", branch, turn_from, tick_from, turn_to, tick_to
		):
			yield d["key"], d["turn"], d["tick"], d["value"]

	def _load_nodes_tick_to_end_graph(
		self, graph: bytes, branch: Branch, turn_from: Turn, tick_from: Tick
	):
		return list(
			self._iter_nodes_tick_to_end_graph(
				graph, branch, turn_from, tick_from
			)
		)

	def _load_nodes_tick_to_end_all(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	):
		return list(
			self._iter_nodes_tick_to_end_all(branch, turn_from, tick_from)
		)

	def load_nodes_tick_to_end(self, *args, **kwargs):
		if len(args) + len(kwargs) == 4:
			return self._load_nodes_tick_to_end_graph(*args, **kwargs)
		else:
			return self._load_nodes_tick_to_end_all(*args, **kwargs)

	def _iter_nodes_tick_to_end_graph(
		self, graph: bytes, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, Turn, Tick, bool]]:
		from pyarrow import compute as pc

		for d in (
			self._get_db("nodes")
			.read(
				filters=[
					pc.field("graph") == graph,
					pc.field("branch") == branch,
					pc.field("turn") >= turn_from,
				],
			)
			.to_pylist()
		):
			if d["turn"] == turn_from:
				if d["tick"] >= tick_from:
					yield (
						d["node"],
						d["turn"],
						d["tick"],
						d["extant"],
					)
			else:
				yield (
					d["node"],
					d["turn"],
					d["tick"],
					d["extant"],
				)

	def _iter_nodes_tick_to_end_all(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, bytes, Turn, Tick, bool]]:
		for d in self._iter_part_tick_to_end(
			"nodes", branch, turn_from, tick_from
		):
			yield (
				d["graph"],
				d["node"],
				d["turn"],
				d["tick"],
				d["extant"],
			)

	def load_nodes_tick_to_tick(self, *args, **kwargs):
		if len(args) + len(kwargs) == 6:
			return self.load_nodes_tick_to_tick_graph(*args, **kwargs)
		else:
			return self.load_nodes_tick_to_tick_all(*args, **kwargs)

	def load_nodes_tick_to_tick_all(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, Turn, Tick, bool]]:
		return list(
			self._iter_nodes_tick_to_tick_all(
				branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def load_nodes_tick_to_tick_graph(
		self,
		graph: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, Turn, Tick, bool]]:
		return list(
			self._iter_nodes_tick_to_tick_graph(
				graph, branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_nodes_tick_to_tick_all(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, bytes, Turn, Tick, bool]]:
		for d in self._iter_part_tick_to_tick(
			"nodes", branch, turn_from, tick_from, turn_to, tick_to
		):
			yield d["graph"], d["node"], d["turn"], d["tick"], d["extant"]

	def _iter_nodes_tick_to_tick_graph(
		self,
		graph: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, Turn, Tick, bool]]:
		from pyarrow import compute as pc

		db = self._get_db("nodes")
		if turn_from == turn_to:
			for d in db.read(
				filters=[
					pc.field("graph") == graph,
					pc.field("branch") == branch,
					pc.field("turn") == turn_from,
					pc.field("tick") >= tick_from,
					pc.field("tick") <= tick_to,
				],
			).to_pylist():
				yield (
					d["node"],
					d["turn"],
					d["tick"],
					d["extant"],
				)
		else:
			for d in db.read(
				filters=[
					pc.field("graph") == graph,
					pc.field("branch") == branch,
					pc.field("turn") >= turn_from,
					pc.field("turn") <= turn_to,
				],
			).to_pylist():
				if d["turn"] == turn_from:
					if d["tick"] >= tick_from:
						yield (
							d["node"],
							d["turn"],
							d["tick"],
							d["extant"],
						)
				elif d["turn"] == turn_to:
					if d["tick"] <= tick_to:
						yield (
							d["node"],
							d["turn"],
							d["tick"],
							d["extant"],
						)
				else:
					yield (
						d["node"],
						d["turn"],
						d["tick"],
						d["extant"],
					)

	def load_node_val_tick_to_end(self, *args, **kwargs):
		if len(args) + len(kwargs) == 4:
			return self._load_node_val_tick_to_end_graph(*args, **kwargs)
		else:
			return self._load_node_val_tick_to_end_all(*args, **kwargs)

	def _load_node_val_tick_to_end_graph(
		self, graph: bytes, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, int, int, bytes]]:
		return list(
			self._iter_node_val_tick_to_end_graph(
				graph, branch, turn_from, tick_from
			)
		)

	def _load_node_val_tick_to_end_all(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_node_val_tick_to_end_all(branch, turn_from, tick_from)
		)

	def _iter_node_val_tick_to_end_all(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, bytes, bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_end(
			"node_val", branch, turn_from, tick_from
		):
			yield (
				d["graph"],
				d["node"],
				d["key"],
				d["turn"],
				d["tick"],
				d["value"],
			)

	def _iter_node_val_tick_to_end_graph(
		self, graph: bytes, branch: str, turn_from: int, tick_from: int
	) -> Iterator[tuple[bytes, bytes, int, int, bytes]]:
		from pyarrow import compute as pc

		for d in (
			self._get_db("node_val")
			.read(
				filters=[
					pc.field("graph") == graph,
					pc.field("branch") == branch,
					pc.field("turn") >= turn_from,
				],
			)
			.to_pylist()
		):
			if d["turn"] == turn_from:
				if d["tick"] >= tick_from:
					yield (
						d["node"],
						d["key"],
						d["turn"],
						d["tick"],
						d["value"],
					)
			else:
				yield d["node"], d["key"], d["turn"], d["tick"], d["value"]

	def load_node_val_tick_to_tick(self, *args, **kwargs):
		if len(args) + len(kwargs) == 6:
			return self._load_node_val_tick_to_tick_graph(*args, **kwargs)
		else:
			return self._load_node_val_tick_to_tick_all(*args, **kwargs)

	def _load_node_val_tick_to_tick_all(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_node_val_tick_to_tick_all(
				branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_node_val_tick_to_tick_all(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, bytes, bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_tick(
			"node_val", branch, turn_from, tick_from, turn_to, tick_to
		):
			yield (
				d["graph"],
				d["node"],
				d["key"],
				d["turn"],
				d["tick"],
				d["value"],
			)

	def _load_node_val_tick_to_tick_graph(
		self,
		graph: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_node_val_tick_to_tick_graph(
				graph, branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_node_val_tick_to_tick_graph(
		self,
		graph: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, bytes, Turn, Tick, bytes]]:
		from pyarrow import compute as pc

		db = self._get_db("node_val")
		if turn_from == turn_to:
			for d in db.read(
				filters=[
					pc.field("graph") == graph,
					pc.field("branch") == branch,
					pc.field("turn") == turn_from,
					pc.field("tick") >= tick_from,
					pc.field("tick") <= tick_to,
				],
			).to_pylist():
				yield (
					d["node"],
					d["key"],
					d["turn"],
					d["tick"],
					d["value"],
				)
		else:
			for d in db.read(
				filters=[
					pc.field("graph") == graph,
					pc.field("branch") == branch,
					pc.field("turn") >= turn_from,
					pc.field("turn") <= turn_to,
				],
			).to_pylist():
				if d["turn"] == turn_from:
					if d["tick"] >= tick_from:
						yield (
							d["node"],
							d["key"],
							d["turn"],
							d["tick"],
							d["value"],
						)
				elif d["turn"] == turn_to:
					if d["tick"] <= tick_to:
						yield (
							d["node"],
							d["key"],
							d["turn"],
							d["tick"],
							d["value"],
						)
				else:
					yield (
						d["node"],
						d["key"],
						d["turn"],
						d["tick"],
						d["value"],
					)

	def load_edges_tick_to_end(self, *args, **kwargs):
		if len(args) + len(kwargs) == 4:
			return self._load_edges_tick_to_end_graph(*args, **kwargs)
		else:
			return self._load_edges_tick_to_end_all(*args, **kwargs)

	def _load_edges_tick_to_end_all(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, bytes, int, Turn, Tick, bool]]:
		return list(
			self._iter_edges_tick_to_end_all(branch, turn_from, tick_from)
		)

	def _iter_edges_tick_to_end_all(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, bytes, bytes, int, Turn, Tick, bool]]:
		for d in self._iter_part_tick_to_end(
			"edges", branch, turn_from, tick_from
		):
			yield (
				d["graph"],
				d["orig"],
				d["dest"],
				d["turn"],
				d["tick"],
				d["extant"],
			)

	def _load_edges_tick_to_end_graph(
		self, graph: bytes, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, int, Turn, Tick, bool]]:
		return list(
			self._iter_edges_tick_to_end_graph(
				graph, branch, turn_from, tick_from
			)
		)

	def _iter_edges_tick_to_end_graph(
		self, graph: bytes, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, bytes, int, Turn, Tick, bool]]:
		from pyarrow import compute as pc

		for d in (
			self._get_db("edges")
			.read(
				filters=[
					pc.field("graph") == graph,
					pc.field("branch") == branch,
					pc.field("turn") >= turn_from,
				],
			)
			.to_pylist()
		):
			if d["turn"] == turn_from:
				if d["tick"] >= tick_from:
					yield (
						d["orig"],
						d["dest"],
						d["turn"],
						d["tick"],
						d["extant"],
					)
			else:
				yield (
					d["orig"],
					d["dest"],
					d["turn"],
					d["tick"],
					d["extant"],
				)

	def load_edges_tick_to_tick(self, *args, **kwargs):
		if len(args) + len(kwargs) == 6:
			return self._load_edges_tick_to_tick_graph(*args, **kwargs)
		else:
			return self._load_edges_tick_to_tick_all(*args, **kwargs)

	def _load_edges_tick_to_tick_all(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, bytes, bytes, int, Turn, Tick, bytes]]:
		return list(
			self._iter_edges_tick_to_tick_all(
				branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_edges_tick_to_tick_all(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, bytes, bytes, bytes, int, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_tick(
			"edges", branch, turn_from, tick_from, turn_to, tick_to
		):
			yield (
				d["graph"],
				d["orig"],
				d["dest"],
				d["turn"],
				d["tick"],
				d["extant"],
			)

	def _load_edges_tick_to_tick_graph(
		self,
		graph: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, bytes, int, Turn, Tick, bytes]]:
		return list(
			self._iter_edges_tick_to_tick_graph(
				graph, branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_edges_tick_to_tick_graph(
		self,
		graph: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, bytes, bytes, int, Turn, Tick, bytes]]:
		from pyarrow import compute as pc

		db = self._get_db("edges")
		if turn_from == turn_to:
			for d in db.read(
				filters=[
					pc.field("graph") == graph,
					pc.field("branch") == branch,
					pc.field("turn") == turn_from,
					pc.field("tick") >= tick_from,
					pc.field("tick") <= tick_to,
				],
			).to_pylist():
				yield (
					d["orig"],
					d["dest"],
					d["turn"],
					d["tick"],
					d["extant"],
				)
		else:
			for d in db.read(
				filters=[
					pc.field("graph") == graph,
					pc.field("branch") == branch,
					pc.field("turn") >= turn_from,
					pc.field("turn") <= turn_to,
				],
			).to_pylist():
				if d["turn"] == turn_from:
					if d["tick"] >= tick_from:
						yield (
							d["orig"],
							d["dest"],
							d["turn"],
							d["tick"],
							d["extant"],
						)
				elif d["turn"] == turn_to:
					if d["tick"] <= tick_to:
						yield (
							d["orig"],
							d["dest"],
							d["turn"],
							d["tick"],
							d["extant"],
						)
				else:
					yield (
						d["orig"],
						d["dest"],
						d["turn"],
						d["tick"],
						d["extant"],
					)

	def load_edge_val_tick_to_end(self, *args, **kwargs):
		if len(args) + len(kwargs) == 6:
			return self._load_edge_val_tick_to_end_graph(*args, **kwargs)
		else:
			return self._load_edge_val_tick_to_end_all(*args, **kwargs)

	def _load_edge_val_tick_to_end_all(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, bytes, int, Turn, Tick, bytes]]:
		return list(
			self._iter_edge_val_tick_to_end_all(branch, turn_from, tick_from)
		)

	def _iter_edge_val_tick_to_end_all(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, bytes, bytes, int, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_end(
			"edge_val", branch, turn_from, tick_from
		):
			yield (
				d["graph"],
				d["orig"],
				d["dest"],
				d["key"],
				d["turn"],
				d["tick"],
				d["value"],
			)

	def _load_edge_val_tick_to_end_graph(
		self, graph: bytes, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, int, Turn, Tick, bytes]]:
		return list(
			self._iter_edge_val_tick_to_end_graph(
				graph, branch, turn_from, tick_from
			)
		)

	def _iter_edge_val_tick_to_end_graph(
		self, graph: bytes, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, bytes, int, Turn, Tick, bytes]]:
		from pyarrow import compute as pc

		for d in (
			self._get_db("edge_val")
			.read(
				filters=[
					pc.field("graph") == graph,
					pc.field("branch") == branch,
					pc.field("turn") >= turn_from,
				],
			)
			.to_pylist()
		):
			if d["turn"] == turn_from:
				if d["tick"] >= tick_from:
					yield (
						d["orig"],
						d["dest"],
						d["key"],
						d["turn"],
						d["tick"],
						d["value"],
					)
			else:
				yield (
					d["orig"],
					d["dest"],
					d["key"],
					d["turn"],
					d["tick"],
					d["value"],
				)

	def load_edge_val_tick_to_tick(self, *args, **kwargs):
		if len(args) + len(kwargs) == 6:
			return self._load_edge_val_tick_to_tick_graph(*args, **kwargs)
		else:
			return self._load_edge_val_tick_to_tick_all(*args, **kwargs)

	def _load_edge_val_tick_to_tick_all(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, bytes, bytes, int, Turn, Tick, bytes]]:
		return list(
			self._iter_edge_val_tick_to_tick_all(
				branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_edge_val_tick_to_tick_all(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, bytes, bytes, bytes, int, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_tick(
			"edge_val", branch, turn_from, tick_from, turn_to, tick_to
		):
			yield (
				d["graph"],
				d["orig"],
				d["dest"],
				d["key"],
				d["turn"],
				d["tick"],
				d["value"],
			)

	def _load_edge_val_tick_to_tick_graph(
		self,
		graph: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, bytes, int, Turn, Tick, bytes]]:
		return list(
			self._iter_edge_val_tick_to_tick_graph(
				graph, branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_edge_val_tick_to_tick_graph(
		self,
		graph: bytes,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, bytes, bytes, int, Turn, Tick, bytes]]:
		from pyarrow import compute as pc

		db = self._get_db("edge_val")
		if turn_from == turn_to:
			for d in db.read(
				filters=[
					pc.field("graph") == graph,
					pc.field("branch") == branch,
					pc.field("turn") == turn_from,
					pc.field("tick") >= tick_from,
					pc.field("tick") <= tick_to,
				],
			).to_pylist():
				yield (
					d["orig"],
					d["dest"],
					d["key"],
					d["turn"],
					d["tick"],
					d["value"],
				)
		else:
			for d in db.read(
				filters=[
					pc.field("graph") == graph,
					pc.field("branch") == branch,
					pc.field("turn") >= turn_from,
					pc.field("turn") <= turn_to,
				],
			).to_pylist():
				if d["turn"] == turn_from:
					if d["tick"] >= tick_from:
						yield (
							d["orig"],
							d["dest"],
							d["key"],
							d["turn"],
							d["tick"],
							d["value"],
						)
				elif d["turn"] == turn_to:
					if d["tick"] <= tick_to:
						yield (
							d["orig"],
							d["dest"],
							d["key"],
							d["turn"],
							d["tick"],
							d["value"],
						)
				else:
					yield (
						d["orig"],
						d["dest"],
						d["key"],
						d["turn"],
						d["tick"],
						d["value"],
					)

	def load_character_rulebook_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_character_rulebook_tick_to_end_part(
				"character", branch, turn_from, tick_from
			)
		)

	def _iter_character_rulebook_tick_to_end_part(
		self, part: str, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_end(
			f"{part}_rulebook", branch, turn_from, tick_from
		):
			yield d["character"], d["turn"], d["tick"], d["rulebook"]

	def load_character_rulebook_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_character_rulebook_tick_to_tick_part(
				"character", branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_character_rulebook_tick_to_tick_part(
		self,
		part: str,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_tick(
			f"{part}_rulebook", branch, turn_from, tick_from, turn_to, tick_to
		):
			yield d["character"], d["turn"], d["tick"], d["rulebook"]

	def load_unit_rulebook_tick_to_end(
		self, branch: str, turn_from: int, tick_from: int
	) -> list[tuple[bytes, int, int, bytes]]:
		return list(
			self._iter_character_rulebook_tick_to_end_part(
				"unit", branch, turn_from, tick_from
			)
		)

	def load_unit_rulebook_tick_to_tick(
		self,
		branch: str,
		turn_from: int,
		tick_from: int,
		turn_to: int,
		tick_to: int,
	) -> list[tuple[bytes, int, int, bytes]]:
		return list(
			self._iter_character_rulebook_tick_to_tick_part(
				"unit", branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def load_character_thing_rulebook_tick_to_end(
		self, branch: str, turn_from: int, tick_from: int
	) -> list[tuple[bytes, int, int, bytes]]:
		return list(
			self._iter_character_rulebook_tick_to_end_part(
				"character_thing", branch, turn_from, tick_from
			)
		)

	def load_character_thing_rulebook_tick_to_tick(
		self,
		branch: str,
		turn_from: int,
		tick_from: int,
		turn_to: int,
		tick_to: int,
	) -> list[tuple[bytes, int, int, bytes]]:
		return list(
			self._iter_character_rulebook_tick_to_tick_part(
				"character_thing",
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		)

	def load_character_place_rulebook_tick_to_end(
		self, branch: str, turn_from: int, tick_from: int
	) -> list[tuple[bytes, int, int, bytes]]:
		return list(
			self._iter_character_rulebook_tick_to_end_part(
				"character_place", branch, turn_from, tick_from
			)
		)

	def load_character_place_rulebook_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_character_rulebook_tick_to_tick_part(
				"character_place",
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		)

	def load_character_portal_rulebook_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_character_rulebook_tick_to_end_part(
				"character_portal", branch, turn_from, tick_from
			)
		)

	def load_character_portal_rulebook_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_character_rulebook_tick_to_tick_part(
				"character_portal",
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		)

	def load_node_rulebook_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, int, int, bytes]]:
		return list(
			self._iter_node_rulebook_tick_to_end(branch, turn_from, tick_from)
		)

	def _iter_node_rulebook_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_end(
			"node_rulebook", branch, turn_from, tick_from
		):
			yield (
				d["character"],
				d["node"],
				d["turn"],
				d["tick"],
				d["rulebook"],
			)

	def load_node_rulebook_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_node_rulebook_tick_to_tick(
				branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_node_rulebook_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_tick(
			"node_rulebook", branch, turn_from, tick_from, turn_to, tick_to
		):
			yield (
				d["character"],
				d["node"],
				d["turn"],
				d["tick"],
				d["rulebook"],
			)

	def load_portal_rulebook_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_portal_rulebook_tick_to_end(
				branch, turn_from, tick_from
			)
		)

	def _iter_portal_rulebook_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, bytes, bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_end(
			"portal_rulebook", branch, turn_from, tick_from
		):
			yield (
				d["character"],
				d["orig"],
				d["dest"],
				d["turn"],
				d["tick"],
				d["rulebook"],
			)

	def load_portal_rulebook_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, bytes, Turn, Tick, bytes]]:
		return list(
			self._iter_portal_rulebook_tick_to_tick(
				branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_portal_rulebook_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, bytes, bytes, Turn, Tick, bytes]]:
		for d in self._iter_part_tick_to_tick(
			"portal_rulebook", branch, turn_from, tick_from, turn_to, tick_to
		):
			yield (
				d["character"],
				d["orig"],
				d["dest"],
				d["turn"],
				d["tick"],
				d["rulebook"],
			)

	def _del_time(self, table: str, branch: Branch, turn: Turn, tick: Tick):
		from pyarrow import compute as pc

		id_ = self.filter_get_id(
			table,
			filters=[
				pc.field("branch") == branch,
				pc.field("turn") == turn,
				pc.field("tick") == tick,
			],
		)
		if id_ is None:
			return
		self._get_db(table).delete([id_])

	def nodes_del_time(self, branch: Branch, turn: Turn, tick: Tick):
		self._del_time("nodes", branch, turn, tick)

	def edges_del_time(self, branch: Branch, turn: Turn, tick: Tick):
		self._del_time("edges", branch, turn, tick)

	def graph_val_del_time(self, branch: Branch, turn: Turn, tick: Tick):
		self._del_time("graph_val", branch, turn, tick)

	def node_val_del_time(self, branch: Branch, turn: Turn, tick: Tick):
		self._del_time("node_val", branch, turn, tick)

	def edge_val_del_time(self, branch: Branch, turn: Turn, tick: Tick):
		self._del_time("edge_val", branch, turn, tick)

	def load_rulebooks_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, Turn, Tick, bytes, RulebookPriority]]:
		return list(
			self._iter_rulebooks_tick_to_end(branch, turn_from, tick_from)
		)

	def _iter_rulebooks_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, Turn, Tick, bytes, RulebookPriority]]:
		for d in self._iter_part_tick_to_end(
			"rulebooks", branch, turn_from, tick_from
		):
			yield (
				d["rulebook"],
				d["turn"],
				d["tick"],
				d["rules"],
				d["priority"],
			)

	def load_rulebooks_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, Turn, Tick, bytes, RulebookPriority]]:
		return list(
			self._iter_rulebooks_tick_to_tick(
				branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_rulebooks_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, Turn, Tick, bytes, RulebookPriority]]:
		for d in self._iter_part_tick_to_tick(
			"rulebooks", branch, turn_from, tick_from, turn_to, tick_to
		):
			yield (
				d["rulebook"],
				d["turn"],
				d["tick"],
				d["rules"],
				d["priority"],
			)

	def _load_rule_part_tick_to_end(
		self, part, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[RuleName, Turn, Tick, bytes | RuleBig]]:
		return list(
			self._iter_rule_part_tick_to_end(
				part, branch, turn_from, tick_from
			)
		)

	def _iter_rule_part_tick_to_end(
		self, part, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[RuleName, Turn, Tick, bytes | RuleBig]]:
		for d in self._iter_part_tick_to_end(
			f"rule_{part}", branch, turn_from, tick_from
		):
			yield d["rule"], d["turn"], d["tick"], d[part]

	def _load_rule_part_tick_to_tick(
		self,
		part: str,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[str, int, int, bytes | RuleBig]]:
		return list(
			self._iter_rule_part_tick_to_tick(
				part, branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_rule_part_tick_to_tick(
		self,
		part,
		branch: str,
		turn_from: int,
		tick_from: int,
		turn_to: int,
		tick_to: int,
	) -> Iterator[tuple[str, int, int, bytes]]:
		for d in self._iter_part_tick_to_tick(
			f"rule_{part}", branch, turn_from, tick_from, turn_to, tick_to
		):
			yield d["rule"], d["turn"], d["tick"], d[part]

	def load_rule_triggers_tick_to_end(
		self, branch, turn_from, tick_from
	) -> list[tuple[str, int, int, bytes]]:
		return self._load_rule_part_tick_to_end(
			"triggers", branch, turn_from, tick_from
		)

	def load_rule_triggers_tick_to_tick(
		self,
		branch: str,
		turn_from: int,
		tick_from: int,
		turn_to: int,
		tick_to: int,
	) -> list[tuple[str, int, int, bytes]]:
		return self._load_rule_part_tick_to_tick(
			"triggers", branch, turn_from, tick_from, turn_to, tick_to
		)

	def load_rule_prereqs_tick_to_end(
		self, branch: str, turn_from: int, tick_from: int
	) -> list[tuple[str, int, int, bytes]]:
		return self._load_rule_part_tick_to_end(
			"prereqs", branch, turn_from, tick_from
		)

	def load_rule_prereqs_tick_to_tick(
		self,
		branch: str,
		turn_from: int,
		tick_from: int,
		turn_to: int,
		tick_to: int,
	) -> list[tuple[str, int, int, bytes]]:
		return self._load_rule_part_tick_to_tick(
			"prereqs", branch, turn_from, tick_from, turn_to, tick_to
		)

	def load_rule_actions_tick_to_end(
		self, branch: str, turn_from: int, tick_from: int
	) -> list[tuple[str, int, int, bytes]]:
		return self._load_rule_part_tick_to_end(
			"actions", branch, turn_from, tick_from
		)

	def load_rule_actions_tick_to_tick(
		self,
		branch: str,
		turn_from: int,
		tick_from: int,
		turn_to: int,
		tick_to: int,
	) -> list[tuple[str, int, int, bytes]]:
		return self._load_rule_part_tick_to_tick(
			"actions", branch, turn_from, tick_from, turn_to, tick_to
		)

	def load_rule_neighborhoods_tick_to_end(
		self, branch: str, turn_from: int, tick_from: int
	) -> list[tuple[str, int, int, bytes]]:
		return self._load_rule_part_tick_to_end(
			"neighborhood", branch, turn_from, tick_from
		)

	def load_rule_neighborhoods_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[RuleName, Turn, Tick, bytes]]:
		return self._load_rule_part_tick_to_tick(
			"neighborhood", branch, turn_from, tick_from, turn_to, tick_to
		)

	def load_rule_big_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[RuleName, Turn, Tick, RuleBig]]:
		return self._load_rule_part_tick_to_end(
			"big", branch, turn_from, tick_from
		)

	def load_rule_big_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[RuleName, Turn, Tick, RuleBig]]:
		return self._load_rule_part_tick_to_tick(
			"big", branch, turn_from, tick_from, turn_to, tick_to
		)

	def load_character_rules_handled_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, RuleName, Turn, Tick]]:
		return list(
			self._iter_character_rules_handled_tick_to_end(
				branch, turn_from, tick_from
			)
		)

	def _iter_character_rules_handled_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> Iterator[tuple[bytes, bytes, RuleName, Turn, Tick]]:
		for d in self._iter_part_tick_to_end(
			"character_rules_handled", branch, turn_from, tick_from
		):
			yield (
				d["character"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)

	def load_character_rules_handled_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, RuleName, Turn, Tick]]:
		return list(
			self._iter_character_rules_handled_tick_to_tick(
				branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _iter_character_rules_handled_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> Iterator[tuple[bytes, bytes, RuleName, Turn, Tick]]:
		for d in self._iter_part_tick_to_tick(
			"character_rules_handled",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			yield (
				d["character"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)

	def load_unit_rules_handled_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, bytes, bytes, RuleName, Turn, Tick]]:
		return [
			(
				d["character"],
				d["graph"],
				d["unit"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)
			for d in self._iter_part_tick_to_end(
				"unit_rules_handled", branch, turn_from, tick_from
			)
		]

	def load_unit_rules_handled_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, bytes, bytes, RuleName, Turn, Tick]]:
		return [
			(
				d["character"],
				d["graph"],
				d["unit"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)
			for d in self._iter_part_tick_to_tick(
				"unit_rules_handled",
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		]

	def load_character_thing_rules_handled_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, bytes, CharName, Turn, Tick]]:
		return [
			(
				d["character"],
				d["thing"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)
			for d in self._iter_part_tick_to_end(
				"character_thing_rules_handled", branch, turn_from, tick_from
			)
		]

	def load_character_thing_rules_handled_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, bytes, RuleName, Turn, Tick]]:
		return [
			(
				d["character"],
				d["thing"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)
			for d in self._iter_part_tick_to_tick(
				"character_thing_rules_handled",
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		]

	def load_character_place_rules_handled_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, bytes, RuleName, Turn, Tick]]:
		return [
			(
				d["character"],
				d["place"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)
			for d in self._iter_part_tick_to_end(
				"character_place_rules_handled", branch, turn_from, tick_from
			)
		]

	def load_character_place_rules_handled_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, bytes, RuleName, Turn, Tick]]:
		return [
			(
				d["character"],
				d["place"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)
			for d in self._iter_part_tick_to_tick(
				"character_place_rules_handled",
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		]

	def load_character_portal_rules_handled_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, bytes, bytes, RuleName, Turn, Tick]]:
		return [
			(
				d["character"],
				d["orig"],
				d["dest"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)
			for d in self._iter_part_tick_to_end(
				"character_portal_rules_handled", branch, turn_from, tick_from
			)
		]

	def load_character_portal_rules_handled_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, bytes, bytes, RuleName, Turn, Tick]]:
		return [
			(
				d["character"],
				d["orig"],
				d["dest"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)
			for d in self._iter_part_tick_to_tick(
				"character_portal_rules_handled",
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		]

	def load_node_rules_handled_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, bytes, RuleName, Turn, Tick]]:
		return [
			(
				d["character"],
				d["node"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)
			for d in self._iter_part_tick_to_end(
				"node_rules_handled", branch, turn_from, tick_from
			)
		]

	def load_node_rules_handled_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, bytes, RuleName, Turn, Tick]]:
		return [
			(
				d["character"],
				d["node"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)
			for d in self._iter_part_tick_to_tick(
				"node_rules_handled",
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		]

	def load_portal_rules_handled_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, bytes, bytes, RuleName, Turn, Tick]]:
		return [
			(
				d["character"],
				d["orig"],
				d["dest"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)
			for d in self._iter_part_tick_to_end(
				"portal_rules_handled", branch, turn_from, tick_from
			)
		]

	def load_portal_rules_handled_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	) -> list[tuple[bytes, bytes, bytes, bytes, RuleName, Turn, Tick]]:
		return [
			(
				d["character"],
				d["orig"],
				d["dest"],
				d["rulebook"],
				d["rule"],
				d["turn"],
				d["tick"],
			)
			for d in self._iter_part_tick_to_tick(
				"portal_rules_handled",
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		]

	def load_units_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	) -> list[tuple[bytes, bytes, bytes, int, int, bool]]:
		return [
			(
				d["character_graph"],
				d["unit_graph"],
				d["unit_node"],
				d["turn"],
				d["tick"],
				d["is_unit"],
			)
			for d in self._iter_part_tick_to_end(
				"units", branch, turn_from, tick_from
			)
		]

	def load_units_tick_to_tick(
		self,
		branch: str,
		turn_from: int,
		tick_from: int,
		turn_to: int,
		tick_to: int,
	) -> list[tuple[bytes, bytes, bytes, int, int, bool]]:
		return [
			(
				d["character_graph"],
				d["unit_graph"],
				d["unit_node"],
				d["turn"],
				d["tick"],
				d["is_unit"],
			)
			for d in self._iter_part_tick_to_tick(
				"units", branch, turn_from, tick_from, turn_to, tick_to
			)
		]

	def get_keyframe_extensions(
		self, branch: str, turn: int, tick: int
	) -> tuple[bytes, bytes, bytes] | None:
		from pyarrow import compute as pc

		db = self._get_db("keyframe_extensions")
		data = db.read(
			filters=[
				pc.field("branch") == branch,
				pc.field("turn") == turn,
				pc.field("tick") == tick,
			]
		)
		if not data:
			return EMPTY, EMPTY, EMPTY
		return (
			data["universal"][0].as_py(),
			data["rule"][0].as_py(),
			data["rulebook"][0].as_py(),
		)

	def all_keyframe_graphs(self, branch: str, turn: int, tick: int):
		from pyarrow import compute as pc

		db = self._get_db("keyframes_graphs")
		data = db.read(
			filters=[
				pc.field("branch") == branch,
				pc.field("turn") == turn,
				pc.field("tick") == tick,
			]
		)
		return [
			(d["graph"], d["nodes"], d["edges"], d["graph_val"])
			for d in data.to_pylist()
		]

	def run(self):
		def loud_exit(inst, ex):
			try:
				msg = (
					f"While calling {inst[0]}"
					f"({', '.join(map(repr, inst[1]))}{', ' if inst[2] else ''}"
					f"{', '.join('='.join(pair) for pair in inst[2].items())})"
					f"silenced, ParquetDBHolder got the exception: {ex}"
				)
			except:
				msg = f"called {inst}; got exception {ex}"
			print(msg, file=sys.stderr)
			sys.exit(msg)

		inq = self._inq
		outq = self._outq

		def call_method(name, *args, silent=False, **kwargs):
			try:
				res = getattr(self, name)(*args, **kwargs)
			except Exception as ex:
				if silent:
					loud_exit(inst, ex)
				res = ex
			if not silent:
				outq.put(res)
			inq.task_done()

		while True:
			inst = inq.get()
			if inst == "close":
				self.close()
				inq.task_done()
				return
			if inst == "commit":
				inq.task_done()
				continue
			if not isinstance(inst, (str, tuple)):
				raise TypeError("Can't use SQLAlchemy with ParquetDB")
			silent = False
			if inst[0] == "silent":
				silent = True
				inst = inst[1:]
			match inst:
				case ("echo", msg):
					outq.put(msg)
					inq.task_done()
				case ("echo", args, _):
					outq.put(args)
					inq.task_done()
				case ("one", cmd):
					call_method(cmd, silent=silent)
				case ("one", cmd, args):
					call_method(cmd, *args, silent=silent)
				case ("one", cmd, args, kwargs):
					call_method(cmd, *args, silent=silent, **kwargs)
				case ("many", cmd, several):
					for args, kwargs in several:
						try:
							res = getattr(self, cmd)(*args, **kwargs)
						except Exception as ex:
							if silent:
								loud_exit(("many", cmd, several), ex)
							res = ex
						if not silent:
							outq.put(res)
						if isinstance(res, Exception):
							break
					inq.task_done()
				case (cmd, args):
					call_method(cmd, *args, silent=silent)
				case (cmd, args, kwargs):
					call_method(cmd, *args, silent=silent, **kwargs)
				case cmd:
					call_method(cmd)


def mutexed(func):
	"""Decorator for when an entire method's body holds a mutex lock"""

	@wraps(func)
	def mutexy(self, *args, **kwargs):
		with self.mutex():
			return func(self, *args, **kwargs)

	return mutexy


class AbstractQueryEngine(ABC):
	pack: callable
	unpack: callable
	holder_cls: type[ConnectionHolder]
	_inq: Queue
	_outq: Queue
	_holder: holder_cls

	@cached_property
	def logger(self):
		try:
			from kivy.logger import Logger

			return Logger
		except ImportError:
			from logging import getLogger

			return getLogger(self.__class__.__name__)

	def log(self, level, msg, *args):
		self.logger.log(level, msg, *args)

	def debug(self, msg, *args):
		self.logger.debug(msg, *args)

	def info(self, msg, *args):
		self.logger.info(msg, *args)

	def warning(self, msg, *args):
		self.logger.warning(msg, *args)

	def error(self, msg, *args):
		self.logger.error(msg, *args)

	def critical(self, msg, *args):
		self.logger.critical(msg, *args)

	def echo(self, string: str) -> str:
		with self.mutex():
			self._inq.put(("echo", string))
			ret = self._outq.get()
			self._outq.task_done()
			return ret

	@abstractmethod
	def get_keyframe_extensions(
		self, branch: Branch, turn: Turn, tick: Tick
	) -> tuple[UniversalKeyframe, RuleKeyframe, RulebookKeyframe]:
		pass

	@abstractmethod
	def keyframes_dump(self) -> Iterator[tuple[Branch, Turn, Tick]]:
		pass

	@abstractmethod
	def delete_keyframe(self, branch: Branch, turn: Turn, tick: Tick) -> None:
		pass

	@abstractmethod
	def new_graph(
		self, graph: CharName, branch: Branch, turn: Turn, tick: Tick, typ: str
	) -> None:
		pass

	@abstractmethod
	def keyframes_graphs(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick]]:
		pass

	@abstractmethod
	def keyframe_insert(self, branch: Branch, turn: Turn, tick: Tick): ...

	@abstractmethod
	def keyframe_extension_insert(
		self,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		universal: UniversalKeyframe,
		rule: RuleKeyframe,
		rulebook: RulebookKeyframe,
	) -> None:
		pass

	@abstractmethod
	def keyframe_graph_insert(
		self,
		graph: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		nodes: NodeKeyframe,
		edges: EdgeKeyframe,
		graph_val: GraphValKeyframe,
	) -> None:
		pass

	@abstractmethod
	def graphs_insert(
		self, graph: CharName, branch: Branch, turn: Turn, tick: Tick, typ: str
	) -> None:
		pass

	@abstractmethod
	def have_branch(self, branch: Branch) -> bool:
		pass

	@abstractmethod
	def all_branches(
		self,
	) -> Iterator[tuple[Branch, Branch, Turn, Tick, Turn, Tick]]:
		pass

	@abstractmethod
	def global_get(self, key: Key) -> Value:
		pass

	@abstractmethod
	def global_items(self) -> Iterator[tuple[Key, Value]]:
		pass

	@abstractmethod
	def get_branch(self) -> Branch:
		pass

	@abstractmethod
	def get_turn(self) -> Turn:
		pass

	@abstractmethod
	def get_tick(self) -> Tick:
		pass

	@abstractmethod
	def global_set(self, key: Key, value: Value):
		pass

	@abstractmethod
	def global_del(self, key: Key) -> None:
		pass

	@abstractmethod
	def new_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
	) -> None:
		pass

	@abstractmethod
	def update_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
		end_turn: Turn,
		end_tick: Tick,
	) -> None:
		pass

	@abstractmethod
	def set_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
		end_turn: Turn,
		end_tick: Tick,
	) -> None:
		pass

	@abstractmethod
	def new_turn(
		self,
		branch: Branch,
		turn: Turn,
		end_tick: Tick = 0,
		plan_end_tick: Tick = 0,
	) -> None:
		pass

	@abstractmethod
	def update_turn(
		self, branch: Branch, turn: Turn, end_tick: Tick, plan_end_tick: Tick
	) -> None:
		pass

	@abstractmethod
	def set_turn(
		self, branch: Branch, turn: Turn, end_tick: Tick, plan_end_tick: Tick
	) -> None:
		pass

	@abstractmethod
	def turns_dump(self) -> Iterator[tuple[Branch, Turn, Tick, Tick]]:
		pass

	@abstractmethod
	def graph_val_dump(self) -> Iterator[GraphValRowType]:
		pass

	@abstractmethod
	def load_graph_val(
		self,
		graph: CharName,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[GraphValRowType]:
		pass

	@abstractmethod
	def graph_val_set(
		self,
		graph: CharName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		val: Value,
	) -> None:
		pass

	@abstractmethod
	def graph_val_del_time(
		self, branch: Branch, turn: Turn, tick: Tick
	) -> None:
		pass

	@abstractmethod
	def graphs_types(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, str]]:
		pass

	@abstractmethod
	def characters(self) -> Iterator[tuple[CharName, Branch, Turn, Tick, str]]:
		pass

	@abstractmethod
	def exist_node(
		self,
		graph: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		extant: bool,
	) -> None:
		pass

	@abstractmethod
	def nodes_del_time(self, branch: Branch, turn: Turn, tick: Tick) -> None:
		pass

	@abstractmethod
	def nodes_dump(self) -> Iterator[NodeRowType]:
		pass

	@abstractmethod
	def load_nodes(
		self,
		graph: CharName,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[NodeRowType]:
		pass

	@abstractmethod
	def node_val_dump(self) -> Iterator[NodeValRowType]:
		pass

	@abstractmethod
	def load_node_val(
		self,
		graph: CharName,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[NodeValRowType]:
		pass

	@abstractmethod
	def node_val_set(
		self,
		graph: CharName,
		node: NodeName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		value: Value,
	):
		pass

	@abstractmethod
	def node_val_del_time(
		self, branch: Branch, turn: Turn, tick: Tick
	) -> None:
		pass

	@abstractmethod
	def edges_dump(self) -> Iterator[EdgeRowType]:
		pass

	@abstractmethod
	def load_edges(
		self,
		graph: CharName,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[EdgeRowType]:
		pass

	@abstractmethod
	def exist_edge(
		self,
		graph: CharName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		extant: bool,
	) -> None:
		pass

	@abstractmethod
	def edge_val_dump(self) -> Iterator[EdgeValRowType]:
		pass

	@abstractmethod
	def load_edge_val(
		self,
		graph: CharName,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[EdgeValRowType]:
		pass

	@abstractmethod
	def edge_val_set(
		self,
		graph: CharName,
		orig: NodeName,
		dest: NodeName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		value: Value,
	):
		pass

	@abstractmethod
	def edge_val_del_time(
		self, branch: Branch, turn: Turn, tick: Tick
	) -> None:
		pass

	@abstractmethod
	def plans_dump(self) -> Iterator[tuple[Plan, Branch, Turn, Tick]]:
		pass

	@abstractmethod
	def plans_insert(
		self, plan_id: Plan, branch: Branch, turn: Turn, tick: Tick
	) -> None:
		pass

	@abstractmethod
	def plans_insert_many(
		self, many: list[tuple[Plan, Branch, Turn, Tick]]
	) -> None:
		pass

	@abstractmethod
	def plan_ticks_insert(self, plan_id: Plan, turn: Turn, tick: Tick) -> None:
		pass

	@abstractmethod
	def plan_ticks_dump(self) -> Iterator[tuple[Plan, Turn, Tick]]:
		pass

	@abstractmethod
	def flush(self) -> None:
		pass

	@abstractmethod
	def commit(self) -> None:
		pass

	@abstractmethod
	def close(self) -> None:
		pass

	@abstractmethod
	def initdb(self) -> None:
		pass

	@abstractmethod
	def truncate_all(self) -> None:
		pass

	_infixes2load = [
		"nodes",
		"edges",
		"graph_val",
		"node_val",
		"edge_val",
		"things",
		"character_rulebook",
		"unit_rulebook",
		"character_thing_rulebook",
		"character_place_rulebook",
		"character_portal_rulebook",
		"node_rulebook",
		"portal_rulebook",
		"universals",
		"rulebooks",
		"rule_triggers",
		"rule_prereqs",
		"rule_actions",
		"rule_neighborhoods",
		"rule_big",
	]

	def _put_window_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	):
		putkwargs = {
			"branch": branch,
			"turn_from": turn_from,
			"tick_from": tick_from,
		}
		for i, infix in enumerate(self._infixes2load):
			self._inq.put(
				(
					"echo",
					(
						"begin",
						infix,
						branch,
						turn_from,
						tick_from,
						None,
						None,
					),
					{},
				)
			)
			self._inq.put(("one", f"load_{infix}_tick_to_end", (), putkwargs))
			self._inq.put(
				(
					"echo",
					("end", infix, branch, turn_from, tick_from, None, None),
					{},
				)
			)

	def _put_window_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	):
		putkwargs = {
			"branch": branch,
			"turn_from": turn_from,
			"tick_from": tick_from,
			"turn_to": turn_to,
			"tick_to": tick_to,
		}
		for i, infix in enumerate(self._infixes2load):
			self._inq.put(
				(
					"echo",
					(
						"begin",
						infix,
						branch,
						turn_from,
						tick_from,
						turn_to,
						tick_to,
					),
					{},
				)
			)
			self._inq.put(("one", f"load_{infix}_tick_to_tick", (), putkwargs))
			self._inq.put(
				(
					"echo",
					(
						"end",
						infix,
						branch,
						turn_from,
						tick_from,
						turn_to,
						tick_to,
					),
					{},
				)
			)

	@contextmanager
	def mutex(self):
		with self._holder.lock:
			yield
			if self._outq.qsize() != 0:
				raise RuntimeError("Unhandled items in output queue")

	@mutexed
	def _load_windows_into(self, ret: dict, windows: list[TimeWindow]) -> None:
		for branch, turn_from, tick_from, turn_to, tick_to in windows:
			if turn_to is None:
				self._put_window_tick_to_end(branch, turn_from, tick_from)
			else:
				self._put_window_tick_to_tick(
					branch, turn_from, tick_from, turn_to, tick_to
				)
		self._inq.join()
		for window in windows:
			self._get_one_window(ret, *window)

	_records: int
	kf_interval_override: callable
	keyframe_interval: int | None
	snap_keyframe: callable

	def _increc(self):
		"""Snap a keyframe, if the keyframe interval has passed.

		But the engine can override this behavior when it'd be impractical,
		such as during a rule's execution. This defers the keyframe snap
		until next we get a falsy result from the override function.

		"""
		self._records += 1
		override: bool | None = self.kf_interval_override()
		if override:
			self._kf_interval_overridden = True
			return
		elif getattr(self, "_kf_interval_overridden", False) or (
			self.keyframe_interval is not None
			and self._records % self.keyframe_interval == 0
		):
			self.snap_keyframe()
			self._kf_interval_overridden = False

	def _get_one_window(
		self,
		ret,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	):
		self.debug(
			f"_get_one_window({branch}, {turn_from}, {tick_from}, {turn_to}, {tick_to})"
		)
		unpack = self.unpack
		outq = self._outq
		got = outq.get()
		if got != (
			"begin",
			"nodes",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError("Expected beginning of nodes", got)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for graph, node, turn, tick, ex in got:
				(graph, node) = map(unpack, (graph, node))
				ret[graph]["nodes"].append(
					(graph, node, branch, turn, tick, ex or None)
				)
			outq.task_done()
		if got != (
			"end",
			"nodes",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				f"Expected {('end', 'nodes', branch, turn_from, tick_from, turn_to, tick_to)}",
				got,
			)
		outq.task_done()
		got = outq.get()
		if got != (
			"begin",
			"edges",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError("Expected beginning of edges", got)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for graph, orig, dest, turn, tick, ex in got:
				(graph, orig, dest) = map(unpack, (graph, orig, dest))
				ret[graph]["edges"].append(
					(
						graph,
						orig,
						dest,
						branch,
						turn,
						tick,
						ex or None,
					)
				)
			outq.task_done()
		if got != (
			"end",
			"edges",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError("Expected end of edges", got)

		outq.task_done()
		got = outq.get()
		if got != (
			"begin",
			"graph_val",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError("Expected beginning of graph_val", got)

		outq.task_done()
		while isinstance(got := outq.get(), list):
			for graph, key, turn, tick, val in got:
				(graph, key, val) = map(unpack, (graph, key, val))
				ret[graph]["graph_val"].append(
					(graph, key, branch, turn, tick, val)
				)
			outq.task_done()
		if got != (
			"end",
			"graph_val",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of graph_val",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"node_val",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of node_val",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for graph, node, key, turn, tick, val in got:
				(graph, node, key, val) = map(unpack, (graph, node, key, val))
				ret[graph]["node_val"].append(
					(graph, node, key, branch, turn, tick, val)
				)
			outq.task_done()
		if got != (
			"end",
			"node_val",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of node_val",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"edge_val",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of edge_val",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for graph, orig, dest, key, turn, tick, val in got:
				(graph, orig, dest, key, val) = map(
					unpack, (graph, orig, dest, key, val)
				)
				ret[graph]["edge_val"].append(
					(
						graph,
						orig,
						dest,
						key,
						branch,
						turn,
						tick,
						val,
					)
				)
			outq.task_done()
		if got != (
			"end",
			"edge_val",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of edge_val",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"things",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of things",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for graph, node, turn, tick, loc in got:
				(graph, node, loc) = map(unpack, (graph, node, loc))
				ret[graph]["things"].append(
					(graph, node, branch, turn, tick, loc)
				)
			outq.task_done()
		if got != (
			"end",
			"things",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of things",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"character_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of character_rulebook",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for graph, turn, tick, rb in got:
				(graph, rb) = map(unpack, (graph, rb))
				ret[graph]["character_rulebook"].append(
					(graph, branch, turn, tick, rb)
				)
			outq.task_done()
		if got != (
			"end",
			"character_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of character_rulebook",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"unit_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of unit_rulebook",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for graph, turn, tick, rb in got:
				(graph, rb) = map(unpack, (graph, rb))
				ret[graph]["unit_rulebook"].append(
					(graph, branch, turn, tick, rb)
				)
			outq.task_done()
		if got != (
			"end",
			"unit_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of unit_rulebook",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"character_thing_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of character_thing_rulebook",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for graph, turn, tick, rb in got:
				(graph, rb) = map(unpack, (graph, rb))
				ret[graph]["character_thing_rulebook"].append(
					(graph, branch, turn, tick, rb)
				)
			outq.task_done()
		if got != (
			"end",
			"character_thing_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of character_thing_rulebook",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"character_place_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of character_place_rulebook",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for graph, turn, tick, rb in got:
				(graph, rb) = map(unpack, (graph, rb))
				ret[graph]["character_place_rulebook"].append(
					(graph, branch, turn, tick, rb)
				)
			outq.task_done()
		if got != (
			"end",
			"character_place_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of character_place_rulebook",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"character_portal_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of character_portal_rulebook",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for graph, turn, tick, rb in got:
				(graph, rb) = map(unpack, (graph, rb))
				ret[graph]["character_portal_rulebook"].append(
					(graph, branch, turn, tick, rb)
				)
			outq.task_done()
		if got != (
			"end",
			"character_portal_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of character_portal_rulebook",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"node_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError("Expected beginning of node_rulebook", got)

		outq.task_done()
		while isinstance(got := outq.get(), list):
			for graph, node, turn, tick, rb in got:
				(graph, node, rb) = map(unpack, (graph, node, rb))
				ret[graph]["node_rulebook"].append(
					(graph, node, branch, turn, tick, rb)
				)
			outq.task_done()
		if got != (
			"end",
			"node_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError("Expected end of node_rulebook", got)

		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"portal_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of portal_rulebook",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for graph, orig, dest, turn, tick, rb in got:
				(graph, orig, dest, rb) = map(unpack, (graph, orig, dest, rb))
				ret[graph]["portal_rulebook"].append(
					(graph, orig, dest, branch, turn, tick, rb)
				)
			outq.task_done()
		if got != (
			"end",
			"portal_rulebook",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of portal_rulebook",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"universals",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of universals",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for key, turn, tick, val in got:
				(key, val) = map(unpack, (key, val))
				if "universals" in ret:
					ret["universals"].append((key, branch, turn, tick, val))
				else:
					ret["universals"] = [(key, branch, turn, tick, val)]
			outq.task_done()
		if got != (
			"end",
			"universals",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of universals",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"rulebooks",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of rulebooks",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for rulebook, turn, tick, rules, priority in got:
				(rulebook, rules) = map(unpack, (rulebook, rules))
				if "rulebooks" in ret:
					ret["rulebooks"].append(
						(rulebook, branch, turn, tick, (rules, priority))
					)
				else:
					ret["rulebooks"] = [
						(rulebook, branch, turn, tick, (rules, priority))
					]
			outq.task_done()
		if got != (
			"end",
			"rulebooks",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of rulebooks",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"rule_triggers",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of rule_triggers",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for rule, turn, tick, triggers in got:
				triggers = unpack(triggers)
				if "rule_triggers" in ret:
					ret["rule_triggers"].append(
						(rule, branch, turn, tick, triggers)
					)
				else:
					ret["rule_triggers"] = [
						(rule, branch, turn, tick, triggers)
					]
			outq.task_done()
		if got != (
			"end",
			"rule_triggers",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of rule_triggers",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"rule_prereqs",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of rule_prereqs",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for rule, turn, tick, prereqs in got:
				prereqs = unpack(prereqs)
				if "rule_prereqs" in ret:
					ret["rule_prereqs"].append(
						(rule, branch, turn, tick, prereqs)
					)
				else:
					ret["rule_prereqs"] = [(rule, branch, turn, tick, prereqs)]
			outq.task_done()
		if got != (
			"end",
			"rule_prereqs",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of rule_prereqs",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"rule_actions",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of rule_actions",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for rule, turn, tick, actions in got:
				actions = unpack(actions)
				if "rule_actions" in ret:
					ret["rule_actions"].append(
						(rule, branch, turn, tick, actions)
					)
				else:
					ret["rule_actions"] = [(rule, branch, turn, tick, actions)]
			outq.task_done()
		if got != (
			"end",
			"rule_actions",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of rule_actions",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"rule_neighborhoods",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of rule_neighborhoods",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for rule, turn, tick, neighborhoods in got:
				neighborhoods = unpack(neighborhoods)
				if "rule_neighborhoods" in ret:
					ret["rule_neighborhoods"].append(
						(rule, branch, turn, tick, neighborhoods)
					)
				else:
					ret["rule_neighborhoods"] = [
						(rule, branch, turn, tick, neighborhoods)
					]
			outq.task_done()
		if got != (
			"end",
			"rule_neighborhoods",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of rule_neighborhoods",
				got,
			)
		outq.task_done()
		if (got := outq.get()) != (
			"begin",
			"rule_big",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected beginning of rule_big",
				got,
			)
		outq.task_done()
		while isinstance(got := outq.get(), list):
			for rule, turn, tick, big in got:
				if "rule_big" in ret:
					ret["rule_big"].append((rule, branch, turn, tick, big))
				else:
					ret["rule_big"] = [(rule, branch, turn, tick, big)]
			outq.task_done()
		if got != (
			"end",
			"rule_big",
			branch,
			turn_from,
			tick_from,
			turn_to,
			tick_to,
		):
			raise RuntimeError(
				"Expected end of rule_big",
				got,
			)
		outq.task_done()

	@abstractmethod
	def get_all_keyframe_graphs(
		self, branch: Branch, turn: Turn, tick: Tick
	) -> Iterator[
		tuple[CharName, NodeKeyframe, EdgeKeyframe, GraphValKeyframe]
	]:
		pass

	@abstractmethod
	def universals_dump(self) -> Iterator[tuple[Key, Branch, Turn, Tick, Any]]:
		pass

	@abstractmethod
	def rulebooks_dump(
		self,
	) -> Iterator[
		tuple[RulebookName, Branch, Turn, Tick, tuple[list[RuleName], float]]
	]:
		pass

	@abstractmethod
	def rules_dump(self) -> Iterator[RuleName]:
		pass

	@abstractmethod
	def rule_triggers_dump(
		self,
	) -> Iterator[tuple[RuleName, Branch, Turn, Tick, list[TriggerFuncName]]]:
		pass

	@abstractmethod
	def rule_prereqs_dump(
		self,
	) -> Iterator[tuple[RuleName, Branch, Turn, Tick, list[PrereqFuncName]]]:
		pass

	@abstractmethod
	def rule_actions_dump(
		self,
	) -> Iterator[tuple[RuleName, Branch, Turn, Tick, list[ActionFuncName]]]:
		pass

	@abstractmethod
	def rule_neighborhood_dump(
		self,
	) -> Iterator[tuple[RuleName, Branch, Turn, Tick, RuleNeighborhood]]:
		pass

	@abstractmethod
	def node_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, NodeName, Branch, Turn, Tick, RulebookName]]:
		pass

	@abstractmethod
	def portal_rulebook_dump(
		self,
	) -> Iterator[
		tuple[CharName, NodeName, NodeName, Branch, Turn, Tick, RulebookName]
	]:
		pass

	@abstractmethod
	def character_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		pass

	@abstractmethod
	def unit_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		pass

	@abstractmethod
	def character_thing_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		pass

	@abstractmethod
	def character_place_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		pass

	@abstractmethod
	def character_portal_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		pass

	@abstractmethod
	def character_rules_handled_dump(
		self,
	) -> Iterator[tuple[CharName, RulebookName, RuleName, Branch, Turn, Tick]]:
		pass

	@abstractmethod
	def unit_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[
			CharName,
			CharName,
			NodeName,
			RulebookName,
			RuleName,
			Branch,
			Turn,
			Tick,
		]
	]:
		pass

	@abstractmethod
	def character_thing_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[CharName, NodeName, RulebookName, RuleName, Branch, Turn, Tick]
	]:
		pass

	@abstractmethod
	def character_place_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[CharName, NodeName, RulebookName, RuleName, Branch, Turn, Tick]
	]:
		pass

	@abstractmethod
	def character_portal_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[
			CharName,
			NodeName,
			NodeName,
			RulebookName,
			RuleName,
			Branch,
			Turn,
			Tick,
		]
	]:
		pass

	@abstractmethod
	def node_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[CharName, NodeName, RulebookName, RuleName, Branch, Turn, Tick]
	]:
		pass

	@abstractmethod
	def portal_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[
			CharName,
			NodeName,
			NodeName,
			RulebookName,
			RuleName,
			Branch,
			Turn,
			Tick,
		]
	]:
		pass

	@abstractmethod
	def things_dump(
		self,
	) -> Iterator[tuple[CharName, NodeName, Branch, Turn, Tick, NodeName]]:
		pass

	@abstractmethod
	def units_dump(
		self,
	) -> Iterator[
		tuple[CharName, CharName, NodeName, Branch, Turn, Tick, bool]
	]:
		pass

	@abstractmethod
	def universal_set(
		self, key: Key, branch: Branch, turn: Turn, tick: Tick, val: Any
	):
		pass

	@abstractmethod
	def universal_del(self, key: Key, branch: Branch, turn: Turn, tick: Tick):
		pass

	@abstractmethod
	def count_all_table(self, tbl: str) -> int:
		pass

	@abstractmethod
	def set_rule_triggers(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		flist: list[TriggerFuncName],
	):
		pass

	@abstractmethod
	def set_rule_prereqs(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		flist: list[PrereqFuncName],
	):
		pass

	@abstractmethod
	def set_rule_actions(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		flist: list[ActionFuncName],
	):
		pass

	@abstractmethod
	def set_rule_neighborhood(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		neighborhood: RuleNeighborhood,
	):
		pass

	@abstractmethod
	def set_rule_big(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		big: RuleBig,
	) -> None:
		pass

	@abstractmethod
	def set_rule(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		triggers: list[TriggerFuncName],
		prereqs: list[PrereqFuncName],
		actions: list[ActionFuncName],
		neighborhood: RuleNeighborhood,
		big: RuleBig,
	):
		pass

	@abstractmethod
	def set_rulebook(
		self,
		name: RulebookName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rules: Optional[list[RuleName]] = None,
		prio: RulebookPriority = 0.0,
	):
		pass

	@abstractmethod
	def set_character_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		pass

	@abstractmethod
	def set_unit_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		pass

	@abstractmethod
	def set_character_thing_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		pass

	@abstractmethod
	def set_character_place_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		pass

	@abstractmethod
	def set_character_portal_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		pass

	@abstractmethod
	def rulebooks(self) -> Iterator[RulebookName]:
		pass

	@abstractmethod
	def set_node_rulebook(
		self,
		character: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rulebook: RulebookName,
	):
		pass

	@abstractmethod
	def set_portal_rulebook(
		self,
		character: CharName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rulebook: RulebookName,
	):
		pass

	@abstractmethod
	def handled_character_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	@abstractmethod
	def handled_unit_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		graph: CharName,
		unit: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	@abstractmethod
	def handled_character_thing_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		thing: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	@abstractmethod
	def handled_character_place_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		place: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	@abstractmethod
	def handled_character_portal_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	@abstractmethod
	def handled_node_rule(
		self,
		character: CharName,
		node: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	@abstractmethod
	def handled_portal_rule(
		self,
		character: CharName,
		orig: NodeName,
		dest: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	@abstractmethod
	def set_thing_loc(
		self,
		character: CharName,
		thing: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		loc: NodeName,
	):
		pass

	@abstractmethod
	def unit_set(
		self,
		character: CharName,
		graph: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		is_unit: bool,
	):
		pass

	@abstractmethod
	def rulebook_set(
		self,
		rulebook: RulebookName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rules: list[RuleName],
	):
		pass

	@abstractmethod
	def turns_completed_dump(self) -> Iterator[tuple[Branch, Turn]]:
		pass

	@abstractmethod
	def complete_turn(
		self, branch: Branch, turn: Turn, discard_rules: bool = False
	):
		pass

	@abstractmethod
	def set_rulebook_on_character(
		self,
		rbtyp: str,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		pass

	@abstractmethod
	def bookmark_items(self) -> Iterator[tuple[Key, Time]]: ...

	@abstractmethod
	def set_bookmark(self, key: Key, time: Time) -> None: ...

	@abstractmethod
	def del_bookmark(self, key: Key) -> None: ...

	def load_windows(self, windows: list[TimeWindow]) -> dict:
		def empty_char():
			return {
				"nodes": [],
				"edges": [],
				"graph_val": [],
				"node_val": [],
				"edge_val": [],
				"things": [],
				"character_rulebook": [],
				"unit_rulebook": [],
				"character_thing_rulebook": [],
				"character_place_rulebook": [],
				"character_portal_rulebook": [],
				"node_rulebook": [],
				"portal_rulebook": [],
			}

		self.debug(f"load_windows({windows})")

		ret = defaultdict(empty_char)
		self._load_windows_into(ret, windows)
		self.debug(f"finished loading windows {windows}")
		return ret


class NullQueryEngine(AbstractQueryEngine):
	"""Query engine that does nothing, connects to no database

	For tests, mainly. If you want to run Lisien in-memory,
	:class:`SQLAlchemyQueryEngine` is more appropriate, with
	``connect_str='sqlite:///:memory:'``

	"""

	@cached_property
	def globl(self) -> dict:
		return {
			"branch": "trunk",
			"turn": 0,
			"tick": 0,
			"language": "eng",
			"_lisien_schema_version": 1,
		}

	def get_keyframe_extensions(
		self, branch: Branch, turn: Turn, tick: Tick
	) -> tuple[UniversalKeyframe, RuleKeyframe, RulebookKeyframe]:
		return {}, {}, {}

	def keyframes_dump(self) -> Iterator[tuple[Branch, Turn, Tick]]:
		return iter(())

	def new_graph(
		self, graph: CharName, branch: Branch, turn: Turn, tick: Tick, typ: str
	) -> None:
		pass

	def get_all_keyframe_graphs(
		self, branch: Branch, turn: Turn, tick: Tick
	) -> Iterator[
		tuple[CharName, NodeKeyframe, EdgeKeyframe, GraphValKeyframe]
	]:
		return iter(())

	def graphs_insert(
		self, graph: CharName, branch: Branch, turn: Turn, tick: Tick, typ: str
	) -> None:
		pass

	def keyframes_graphs(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick]]:
		return iter(())

	def keyframe_extension_insert(
		self,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		universal: dict,
		rule: dict,
		rulebook: dict,
	) -> None:
		pass

	def keyframe_graph_insert(
		self,
		graph: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		nodes: dict,
		edges: dict,
		graph_val: dict,
	) -> None:
		pass

	def keyframe_insert(self, branch: Branch, turn: Turn, tick: Tick) -> None:
		pass

	def delete_keyframe(self, branch: Branch, turn: Turn, tick: Tick) -> None:
		pass

	def have_branch(self, branch: Branch) -> bool:
		pass

	def all_branches(
		self,
	) -> Iterator[tuple[Branch, Branch, Turn, Tick, Turn, Tick]]:
		return iter(())

	def global_get(self, key: Key) -> Any:
		return self.globl[key]

	def global_items(self) -> Iterator[tuple[Key, Any]]:
		return iter(self.globl.items())

	def get_branch(self) -> Branch:
		return self.globl["branch"]

	def get_turn(self) -> Turn:
		return self.globl["turn"]

	def get_tick(self) -> Tick:
		return self.globl["tick"]

	def global_set(self, key: Key, value: Any):
		self.globl[key] = value

	def global_del(self, key: Key):
		del self.globl[key]

	def new_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
	):
		pass

	def update_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
		end_turn: Turn,
		end_tick: Tick,
	):
		pass

	def set_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
		end_turn: Turn,
		end_tick: Tick,
	):
		pass

	def new_turn(
		self,
		branch: Branch,
		turn: Turn,
		end_tick: Tick = 0,
		plan_end_tick: Tick = 0,
	):
		pass

	def update_turn(
		self, branch: Branch, turn: Turn, end_tick: Tick, plan_end_tick: Tick
	):
		pass

	def set_turn(
		self, branch: Branch, turn: Turn, end_tick: Tick, plan_end_tick: Tick
	):
		pass

	def turns_dump(self):
		return iter(())

	def graph_val_dump(self) -> Iterator[GraphValRowType]:
		return iter(())

	def load_graph_val(
		self,
		graph: CharName,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	):
		pass

	def graph_val_set(
		self,
		graph: CharName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		val: Any,
	):
		pass

	def graph_val_del_time(self, branch: Branch, turn: Turn, tick: Tick):
		pass

	def graphs_types(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[tuple[Key, str, int, int, str]]:
		return iter(())

	def characters(self) -> Iterator[tuple[CharName, Branch, Turn, Tick, str]]:
		return iter(())

	def exist_node(
		self,
		graph: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		extant: bool,
	):
		pass

	def nodes_del_time(self, branch: Branch, turn: Turn, tick: Tick):
		pass

	def nodes_dump(self) -> Iterator[NodeRowType]:
		return iter(())

	def load_nodes(
		self,
		graph: CharName,
		branch: NodeName,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn = None,
		tick_to: Tick = None,
	):
		pass

	def node_val_dump(self) -> Iterator[NodeValRowType]:
		return iter(())

	def load_node_val(
		self,
		graph: CharName,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[NodeValRowType]:
		return iter(())

	def node_val_set(
		self,
		graph: CharName,
		node: NodeName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		value: Any,
	):
		pass

	def node_val_del_time(self, branch: Branch, turn: Turn, tick: Tick):
		pass

	def edges_dump(self) -> Iterator[EdgeRowType]:
		return iter(())

	def load_edges(
		self,
		graph: Key,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[EdgeRowType]:
		return iter(())

	def exist_edge(
		self,
		graph: CharName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		extant: bool,
	):
		pass

	def edges_del_time(self, branch: Branch, turn: Turn, tick: Tick):
		pass

	def edge_val_dump(self) -> Iterator[EdgeValRowType]:
		return iter(())

	def load_edge_val(
		self,
		graph: CharName,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[EdgeValRowType]:
		return iter(())

	def edge_val_set(
		self,
		graph: CharName,
		orig: NodeName,
		dest: NodeName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		value: Any,
	):
		pass

	def edge_val_del_time(self, branch: Branch, turn: Turn, tick: Tick):
		pass

	def plans_dump(self) -> Iterator:
		return iter(())

	def plans_insert(
		self, plan_id: Plan, branch: Branch, turn: Turn, tick: Tick
	):
		pass

	def plans_insert_many(self, many: list[tuple[Plan, Branch, Turn, Tick]]):
		pass

	def plan_ticks_insert(self, plan_id: Plan, turn: Turn, tick: Tick):
		pass

	def plan_ticks_dump(self) -> Iterator:
		return iter(())

	def flush(self):
		pass

	def commit(self):
		pass

	def close(self):
		pass

	def initdb(self):
		pass

	def truncate_all(self):
		pass

	def universals_dump(self) -> Iterator[tuple[Key, Branch, Turn, Tick, Any]]:
		return iter(())

	def rulebooks_dump(
		self,
	) -> Iterator[
		tuple[RulebookName, Branch, Turn, Tick, tuple[list[RuleName], float]]
	]:
		return iter(())

	def rules_dump(self) -> Iterator[str]:
		return iter(())

	def rule_triggers_dump(
		self,
	) -> Iterator[tuple[RuleName, Branch, Turn, Tick, list[TriggerFuncName]]]:
		return iter(())

	def rule_prereqs_dump(
		self,
	) -> Iterator[tuple[RuleName, Branch, Turn, Tick, list[PrereqFuncName]]]:
		return iter(())

	def rule_actions_dump(
		self,
	) -> Iterator[tuple[RuleName, Branch, Turn, Tick, list[ActionFuncName]]]:
		return iter(())

	def rule_neighborhood_dump(
		self,
	) -> Iterator[tuple[RuleName, Branch, Turn, Tick, RuleNeighborhood]]:
		return iter(())

	def node_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, NodeName, Branch, Turn, Tick, RulebookName]]:
		return iter(())

	def portal_rulebook_dump(
		self,
	) -> Iterator[
		tuple[CharName, NodeName, NodeName, Branch, Turn, Tick, RulebookName]
	]:
		return iter(())

	def character_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		return iter(())

	def unit_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		return iter(())

	def character_thing_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		return iter(())

	def character_place_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		return iter(())

	def character_portal_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		return iter(())

	def character_rules_handled_dump(
		self,
	) -> Iterator[tuple[CharName, RulebookName, RuleName, Branch, Turn, Tick]]:
		return iter(())

	def unit_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[
			CharName,
			CharName,
			NodeName,
			RulebookName,
			RuleName,
			Branch,
			Turn,
			Tick,
		]
	]:
		return iter(())

	def character_thing_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[CharName, NodeName, RulebookName, RuleName, Branch, Turn, Tick]
	]:
		return iter(())

	def character_place_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[CharName, NodeName, RulebookName, RuleName, Branch, Turn, Tick]
	]:
		return iter(())

	def character_portal_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[
			CharName,
			NodeName,
			NodeName,
			RulebookName,
			RuleName,
			Branch,
			Turn,
			Tick,
		]
	]:
		return iter(())

	def node_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[CharName, NodeName, RulebookName, RuleName, Branch, Turn, Tick]
	]:
		return iter(())

	def portal_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[
			CharName,
			NodeName,
			NodeName,
			RulebookName,
			RuleName,
			Branch,
			Turn,
			Tick,
		]
	]:
		return iter(())

	def things_dump(
		self,
	) -> Iterator[tuple[CharName, NodeName, Branch, Turn, Tick, NodeName]]:
		return iter(())

	def units_dump(
		self,
	) -> Iterator[
		tuple[CharName, CharName, NodeName, Branch, Turn, Tick, bool]
	]:
		return iter(())

	def universal_set(
		self, key: Key, branch: Branch, turn: Turn, tick: Tick, val: Any
	):
		pass

	def universal_del(self, key: Key, branch: Branch, turn: Turn, tick: Tick):
		pass

	def count_all_table(self, tbl: str) -> int:
		pass

	def set_rule_triggers(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		flist: list[TriggerFuncName],
	):
		pass

	def set_rule_prereqs(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		flist: list[PrereqFuncName],
	):
		pass

	def set_rule_actions(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		flist: list[ActionFuncName],
	):
		pass

	def set_rule_neighborhood(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		neighborhood: RuleNeighborhood,
	):
		pass

	def set_rule_big(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		big: RuleBig,
	) -> None:
		pass

	def set_rule(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		triggers: list[TriggerFuncName],
		prereqs: list[PrereqFuncName],
		actions: list[ActionFuncName],
		neighborhood: RuleNeighborhood,
		big: bool,
	):
		pass

	def set_rulebook(
		self,
		name: RulebookName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rules: Optional[list[RuleName]] = None,
		prio: RulebookPriority = 0.0,
	):
		pass

	def set_character_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		pass

	def set_unit_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		pass

	def set_character_thing_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		pass

	def set_character_place_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		pass

	def set_character_portal_rulebook(
		self,
		char: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		pass

	def rulebooks(self) -> Iterator[Key]:
		return iter(())

	def set_node_rulebook(
		self,
		character: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rulebook: RulebookName,
	):
		pass

	def set_portal_rulebook(
		self,
		character: CharName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rulebook: RulebookName,
	):
		pass

	def handled_character_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	def handled_unit_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		graph: CharName,
		unit: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	def handled_character_thing_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		thing: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	def handled_character_place_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		place: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	def handled_character_portal_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	def handled_node_rule(
		self,
		character: CharName,
		node: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	def handled_portal_rule(
		self,
		character: CharName,
		orig: NodeName,
		dest: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		pass

	def set_thing_loc(
		self,
		character: CharName,
		thing: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		loc: NodeName,
	):
		pass

	def unit_set(
		self,
		character: CharName,
		graph: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		is_unit: bool,
	):
		pass

	def rulebook_set(
		self,
		rulebook: RulebookName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rules: list[RuleName],
	):
		pass

	def turns_completed_dump(self) -> Iterator[tuple[Branch, Turn]]:
		return iter(())

	def complete_turn(
		self, branch: Branch, turn: Turn, discard_rules: bool = False
	):
		pass

	def set_rulebook_on_character(
		self,
		rbtyp: str,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		pass

	def _put_window_tick_to_end(
		self, branch: Branch, turn_from: Turn, tick_from: Tick
	):
		pass

	def _put_window_tick_to_tick(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	):
		pass

	def _load_windows_into(self, ret: dict, windows: list[TimeWindow]) -> None:
		pass

	def _increc(self):
		pass

	def _get_one_window(
		self,
		ret,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Turn,
		tick_to: Tick,
	):
		pass

	def bookmark_items(self) -> Iterator[tuple[Key, Time]]:
		return iter(())

	def set_bookmark(self, key: Key, time: Time) -> None:
		pass

	def del_bookmark(self, key: Key) -> None:
		pass

	def load_windows(self, windows: list[TimeWindow]) -> dict:
		return {}


class ParquetBatch(list):
	# Set ``silent = False`` if it hangs when called.
	# Better for performance if ``silent = True``.

	silent = True

	def __init__(
		self,
		qe: "AbstractQueryEngine",
		table: str,
		serialize_record: callable,
	):
		super().__init__()
		self._qe = qe
		self._table = table
		self._serialize_record = serialize_record
		self._argspec = inspect.getfullargspec(serialize_record)

	def __call__(self):
		if not self:
			return 0
		if self.silent:
			meth = self._qe.call_silent
		else:
			meth = self._qe.call
		meth(
			"insert",
			self._table,
			[
				dict(zip(self._argspec[0][1:], rec))
				for rec in starmap(self._serialize_record, super().__iter__())
			],
		)
		n = len(self)
		self.clear()
		return n

	def __iter__(self):
		return starmap(self._serialize_record, super().__iter__())

	def __getitem__(self, item):
		return self._serialize_record(*super().__getitem__(item))


def pqbatch(table: str, serialize_record: callable = None):
	if serialize_record is None:
		return partial(pqbatch, table)

	@cached_property
	def the_batch(self):
		return ParquetBatch(self, table, MethodType(serialize_record, self))

	return the_batch


class ParquetQueryEngine(AbstractQueryEngine):
	holder_cls = ParquetDBHolder

	def __init__(self, path, pack=None, unpack=None, logger=None):
		self._inq = Queue()
		self._outq = Queue()
		self._holder = self.holder_cls(path, self._inq, self._outq)
		self._records = 0
		self.keyframe_interval = None
		self.snap_keyframe = lambda: None
		self._new_keyframe_times = set()

		if pack is None:

			def pack(s: Any) -> bytes:
				return repr(s).encode()

		if unpack is None:
			from ast import literal_eval

			def unpack(b: bytes) -> Any:
				return literal_eval(b.decode())

		self.pack = pack
		self.unpack = unpack
		self._branches = {}
		self._btts = set()
		self._t = Thread(target=self._holder.run, daemon=True)
		self._t.start()
		self.globl = GlobalKeyValueStore(
			self, {unpack(k): unpack(v) for (k, v) in self.initdb().items()}
		)
		self._all_keyframe_times = self.call("all_keyframe_times")

	@mutexed
	def call(self, method, *args, **kwargs):
		self._inq.put((method, args, kwargs))
		ret = self._outq.get()
		if isinstance(ret, Exception):
			self._outq.task_done()
			raise ret
		self._outq.task_done()
		return ret

	def call_silent(self, method, *args, **kwargs):
		self._inq.put(("silent", method, args, kwargs))

	def global_keys(self):
		unpack = self.unpack
		for key in self.call("global_keys"):
			yield unpack(key)

	def keyframes_dump(self) -> Iterator[tuple[Branch, Turn, Tick]]:
		for d in self.call("dump", "keyframes"):
			yield d["branch"], d["turn"], d["tick"]

	def new_graph(
		self, graph: CharName, branch: Branch, turn: Turn, tick: Tick, typ: str
	) -> None:
		graph = self.pack(graph)
		self.call(
			"insert1",
			"graphs",
			{
				"graph": graph,
				"branch": branch,
				"turn": turn,
				"tick": tick,
				"type": typ,
			},
		)

	new_character = graphs_insert = new_graph

	def set_rulebook_on_character(
		self,
		rbtyp: str,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	):
		pack = self.pack
		self.call(
			"set_rulebook_on_character",
			rbtyp,
			pack(char),
			branch,
			turn,
			tick,
			pack(rb),
		)

	def get_keyframe_extensions(
		self, branch: Branch, turn: Turn, tick: Tick
	) -> tuple[UniversalKeyframe, RuleKeyframe, RulebookKeyframe]:
		unpack = self.unpack
		univ, rule, rulebook = self.call(
			"get_keyframe_extensions", branch, turn, tick
		)
		return unpack(univ), unpack(rule), unpack(rulebook)

	def keyframes_graphs(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick]]:
		unpack = self.unpack
		for d in self.call("list_keyframes"):
			yield unpack(d["graph"]), d["branch"], d["turn"], d["tick"]

	def delete_keyframe(self, branch: Branch, turn: Turn, tick: Tick) -> None:
		self.call("delete_keyframe", branch, turn, tick)

	def graphs_types(
		self,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, str]]:
		unpack = self.unpack
		if turn_to is None:
			if tick_to is not None:
				raise TypeError("Need both or neither of turn_to, tick_to")
			data = self.call(
				"list_graphs_to_end", branch, turn_from, tick_from
			)
		else:
			if tick_to is None:
				raise TypeError("Need both or neither of turn_to, tick_to")
			data = self.call(
				"list_graphs_to_tick",
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		for d in data:
			yield (
				unpack(d["graph"]),
				d["branch"],
				d["turn"],
				d["tick"],
				d["type"],
			)

	def have_branch(self, branch: Branch) -> bool:
		return self.call("have_branch", branch)

	def all_branches(
		self,
	) -> Iterator[tuple[Branch, Branch, Turn, Tick, Turn, Tick]]:
		for d in self.call("dump", "branches"):
			yield (
				d["branch"],
				d["parent"],
				d["parent_turn"],
				d["parent_tick"],
				d["end_turn"],
				d["end_tick"],
			)

	def global_get(self, key: Key) -> Any:
		try:
			return self.unpack(self.call("get_global", self.pack(key)))
		except KeyError:
			return ...

	def global_set(self, key: Key, value: Any) -> None:
		pack = self.pack
		return self.call("set_global", pack(key), pack(value))

	def global_del(self, key: Key) -> None:
		return self.call("del_global", self.pack(key))

	def global_items(self) -> Iterator[tuple[Key, Any]]:
		unpack = self.unpack
		for d in self.call("dump", "global"):
			yield unpack(d["key"]), unpack(d["value"])

	def get_branch(self) -> Branch:
		v = self.unpack(self.call("get_global", b"\xa6branch"))
		if v is ...:
			mainbranch = Branch(
				self.unpack(self.call("get_global", b"\xabmain_branch"))
			)
			if mainbranch is None:
				return Branch("trunk")
			return mainbranch
		return v

	def get_turn(self) -> Turn:
		v = self.unpack(self.call("get_global", b"\xa4turn"))
		if v is ...:
			return Turn(0)
		return v

	def get_tick(self) -> Tick:
		v = self.unpack(self.call("get_global", b"\xa4tick"))
		if v is ...:
			return Tick(0)
		return v

	def new_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
	):
		return self.call(
			"insert1",
			"branches",
			{
				"branch": branch,
				"parent": parent,
				"parent_turn": parent_turn,
				"parent_tick": parent_tick,
				"end_turn": parent_turn,
				"end_tick": parent_tick,
			},
		)

	def update_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
		end_turn: Turn,
		end_tick: Tick,
	):
		return self.call(
			"update_branch",
			branch,
			parent,
			parent_turn,
			parent_tick,
			end_turn,
			end_tick,
		)

	def set_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
		end_turn: Turn,
		end_tick: Tick,
	):
		return self.call(
			"set_branch",
			branch,
			parent,
			parent_turn,
			parent_tick,
			end_turn,
			end_tick,
		)

	def update_turn(
		self, branch: Branch, turn: Turn, end_tick: Tick, plan_end_tick: Tick
	):
		return self.call("update_turn", branch, turn, end_tick, plan_end_tick)

	def set_turn(
		self, branch: Branch, turn: Turn, end_tick: Tick, plan_end_tick: Tick
	):
		return self.call("set_turn", branch, turn, end_tick, plan_end_tick)

	def turns_dump(self) -> Iterator[tuple[Branch, Turn, Tick, Tick]]:
		for d in self.call("dump", "turns"):
			yield d["branch"], d["turn"], d["end_tick"], d["plan_end_tick"]

	@garbage
	@mutexed
	def flush(self):
		if not any(
			(
				self._universals2set,
				self._noderb2set,
				self._portrb2set,
				self._graphvals2set,
				self._nodes2set,
				self._edges2set,
				self._edgevals2set,
				self._planticks2set,
				self._unitness,
				self._location,
				self._char_rules_handled,
				self._unit_rules_handled,
				self._char_thing_rules_handled,
				self._char_place_rules_handled,
				self._char_portal_rules_handled,
				self._node_rules_handled,
				self._portal_rules_handled,
				self._new_keyframes,
				self._new_keyframe_times,
				self._new_keyframe_extensions,
			)
		):
			return
		records = sum(
			(
				self._universals2set(),
				self._noderb2set(),
				self._portrb2set(),
				self._graphvals2set(),
				self._nodes2set(),
				self._nodevals2set(),
				self._edges2set(),
				self._edgevals2set(),
				self._planticks2set(),
			)
		)
		if self._unitness:
			self.call_silent(
				"del_units_after",
				[
					(character, graph, node, branch, turn, tick)
					for (
						character,
						graph,
						node,
						branch,
						turn,
						tick,
						_,
					) in self._unitness
				],
			)
			records += self._unitness()
		if self._location:
			self.call_silent(
				"del_things_after",
				[
					(character, thing, branch, turn, tick)
					for (
						character,
						thing,
						branch,
						turn,
						tick,
						_,
					) in self._location
				],
			)
			records += self._location()
		self._char_rules_handled()
		self._unit_rules_handled()
		self._char_thing_rules_handled()
		self._char_place_rules_handled()
		self._char_portal_rules_handled()
		self._node_rules_handled()
		self._portal_rules_handled()
		override = self.kf_interval_override()
		if override is False or (
			self.keyframe_interval is not None
			and self._records + records > self.keyframe_interval
		):
			self.snap_keyframe()
		if self.keyframe_interval:
			self._records = (self._records + records) % self.keyframe_interval
		else:
			self._records += records
		if self._new_keyframe_times:
			self.call_silent(
				"insert",
				"keyframes",
				[
					{"branch": branch, "turn": turn, "tick": tick}
					for (
						branch,
						turn,
						tick,
					) in self._new_keyframe_times
				],
			)
			self._new_keyframe_times = set()
		if self._new_keyframes:
			kfs = {}
			for (
				graph,
				branch,
				turn,
				tick,
				nodes,
				edges,
				graph_val,
			) in self._new_keyframes:
				kfs[graph, branch, turn, tick] = (nodes, edges, graph_val)
			self.call_silent(
				"keyframes_graphs_delete",
				[
					{
						"graph": graph,
						"branch": branch,
						"turn": turn,
						"tick": tick,
					}
					for (graph, branch, turn, tick) in kfs
				],
			)
			self.call_silent(
				"insert",
				"keyframes_graphs",
				[
					{
						"graph": graph,
						"branch": branch,
						"turn": turn,
						"tick": tick,
						"nodes": nodes,
						"edges": edges,
						"graph_val": graph_val,
					}
					for (graph, branch, turn, tick), (
						nodes,
						edges,
						graph_val,
					) in kfs.items()
				],
			)
		self._new_keyframe_extensions()

		self._inq.put(("echo", "flushed"))
		if (got := self._outq.get()) != "flushed":
			raise RuntimeError("Failed flush", got)

	def universals_dump(self) -> Iterator[tuple[Key, Branch, Turn, Tick, Any]]:
		unpack = self.unpack
		for d in self.call("dump", "universals"):
			yield (
				unpack(d["key"]),
				d["branch"],
				d["turn"],
				d["tick"],
				unpack(d["value"]),
			)

	def rulebooks_dump(
		self,
	) -> Iterator[
		tuple[RulebookName, Branch, Turn, Tick, tuple[list[RuleName], float]]
	]:
		unpack = self.unpack
		for d in self.call("dump", "rulebooks"):
			yield (
				unpack(d["rulebook"]),
				d["branch"],
				d["turn"],
				d["tick"],
				(unpack(d["rules"]), d["priority"]),
			)

	def rules_dump(self) -> Iterator[RuleName]:
		for d in self.call("dump", "rules"):
			yield d["rule"]

	def _rule_dump(self, typ: Literal["triggers", "prereqs", "actions"]):
		unpack = self.unpack
		for d in self.call("dump", "rule_" + typ):
			yield (
				d["rule"],
				d["branch"],
				d["turn"],
				d["tick"],
				unpack(d[typ]),
			)

	def rule_triggers_dump(
		self,
	) -> Iterator[tuple[RuleName, Branch, Turn, Tick, list[TriggerFuncName]]]:
		return self._rule_dump("triggers")

	def rule_prereqs_dump(
		self,
	) -> Iterator[tuple[RuleName, Branch, Turn, Tick, list[PrereqFuncName]]]:
		return self._rule_dump("prereqs")

	def rule_actions_dump(
		self,
	) -> Iterator[tuple[RuleName, Branch, Turn, Tick, list[ActionFuncName]]]:
		return self._rule_dump("actions")

	def rule_neighborhood_dump(
		self,
	) -> Iterator[tuple[RuleName, Branch, Turn, Tick, RuleNeighborhood]]:
		for d in self.call("dump", "rule_neighborhood"):
			yield (
				d["rule"],
				d["branch"],
				d["turn"],
				d["tick"],
				d["neighborhood"],
			)

	def node_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, NodeName, Branch, Turn, Tick, RulebookName]]:
		unpack = self.unpack
		for d in self.call("dump", "node_rulebook"):
			yield (
				unpack(d["character"]),
				unpack(d["node"]),
				d["branch"],
				d["turn"],
				d["tick"],
				unpack(d["rulebook"]),
			)

	def portal_rulebook_dump(
		self,
	) -> Iterator[
		tuple[CharName, NodeName, NodeName, Branch, Turn, Tick, RulebookName]
	]:
		unpack = self.unpack
		for d in self.call("dump", "portal_rulebook"):
			yield (
				unpack(d["character"]),
				unpack(d["orig"]),
				unpack(d["dest"]),
				d["branch"],
				d["turn"],
				d["tick"],
				unpack(d["rulebook"]),
			)

	def _character_rulebook_dump(self, typ: RulebookTypeStr):
		unpack = self.unpack
		for d in self.call("dump", f"{typ}_rulebook"):
			yield (
				unpack(d["character"]),
				d["branch"],
				d["turn"],
				d["tick"],
				unpack(d["rulebook"]),
			)

	def character_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		return self._character_rulebook_dump("character")

	def unit_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		return self._character_rulebook_dump("unit")

	def character_thing_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		return self._character_rulebook_dump("character_thing")

	def character_place_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		return self._character_rulebook_dump("character_place")

	def character_portal_rulebook_dump(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick, RulebookName]]:
		return self._character_rulebook_dump("character_portal")

	def character_rules_handled_dump(
		self,
	) -> Iterator[tuple[CharName, RulebookName, RuleName, Branch, Turn, Tick]]:
		unpack = self.unpack
		for d in self.call("dump", "character_rules_handled"):
			yield (
				unpack(d["character"]),
				unpack(d["rulebook"]),
				d["rule"],
				d["branch"],
				d["turn"],
				d["tick"],
			)

	def unit_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[
			CharName,
			CharName,
			NodeName,
			RulebookName,
			RuleName,
			Branch,
			Turn,
			Tick,
		]
	]:
		unpack = self.unpack
		for d in self.call("dump", "unit_rules_handled"):
			yield (
				unpack(d["character"]),
				unpack(d["graph"]),
				unpack(d["unit"]),
				unpack(d["rulebook"]),
				d["rule"],
				d["branch"],
				d["turn"],
				d["tick"],
			)

	def character_thing_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[CharName, NodeName, RulebookName, RuleName, Branch, Turn, Tick]
	]:
		unpack = self.unpack
		for d in self.call("dump", "character_thing_rules_handled"):
			yield (
				unpack(d["character"]),
				unpack(d["thing"]),
				unpack(d["rulebook"]),
				d["rule"],
				d["branch"],
				d["turn"],
				d["tick"],
			)

	def character_place_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[CharName, NodeName, RulebookName, RuleName, Branch, Turn, Tick]
	]:
		unpack = self.unpack
		for d in self.call("dump", "character_place_rules_handled"):
			yield (
				unpack(d["character"]),
				unpack(d["place"]),
				unpack(d["rulebook"]),
				d["rule"],
				d["branch"],
				d["turn"],
				d["tick"],
			)

	def character_portal_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[
			CharName,
			NodeName,
			NodeName,
			RulebookName,
			RuleName,
			Branch,
			Turn,
			Tick,
		]
	]:
		unpack = self.unpack
		for d in self.call("dump", "character_portal_rules_handled"):
			yield (
				unpack(d["character"]),
				unpack(d["orig"]),
				unpack(d["dest"]),
				unpack(d["rulebook"]),
				d["rule"],
				d["branch"],
				d["turn"],
				d["tick"],
			)

	def node_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[CharName, NodeName, RulebookName, RuleName, Branch, Turn, Tick]
	]:
		unpack = self.unpack
		for d in self.call("dump", "node_rules_handled"):
			yield (
				unpack(d["character"]),
				unpack(d["node"]),
				unpack(d["rulebook"]),
				d["rule"],
				d["branch"],
				d["turn"],
				d["tick"],
			)

	def portal_rules_handled_dump(
		self,
	) -> Iterator[
		tuple[
			CharName,
			NodeName,
			NodeName,
			RulebookName,
			RuleName,
			Branch,
			Turn,
			Tick,
		]
	]:
		unpack = self.unpack
		for d in self.call("dump", "portal_rules_handled"):
			yield (
				unpack(d["character"]),
				unpack(d["orig"]),
				unpack(d["dest"]),
				unpack(d["rulebook"]),
				d["rule"],
				d["branch"],
				d["turn"],
				d["tick"],
			)

	def things_dump(
		self,
	) -> Iterator[tuple[CharName, NodeName, Branch, Turn, Tick, NodeName]]:
		unpack = self.unpack
		for d in self.call("dump", "things"):
			yield (
				unpack(d["character"]),
				unpack(d["thing"]),
				d["branch"],
				d["turn"],
				d["tick"],
				unpack(d["location"]),
			)

	def units_dump(
		self,
	) -> Iterator[
		tuple[CharName, CharName, NodeName, Branch, Turn, Tick, bool]
	]:
		unpack = self.unpack
		for d in self.call("dump", "units"):
			yield (
				unpack(d["character_graph"]),
				unpack(d["unit_graph"]),
				unpack(d["unit_node"]),
				d["branch"],
				d["turn"],
				d["tick"],
				d["is_unit"],
			)

	@pqbatch("plan_ticks")
	def _planticks2set(
		self, plan_id: Plan, turn: Turn, tick: Tick
	) -> tuple[Plan, Turn, Tick]:
		return plan_id, turn, tick

	@pqbatch("universals")
	def _universals2set(
		self, key: Key, branch: Branch, turn: Turn, tick: Tick, val: Value
	) -> tuple[bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return pack(key), branch, turn, tick, pack(val)

	def universal_set(
		self, key: Key, branch: Branch, turn: Turn, tick: Tick, val: Value
	):
		self._universals2set.append((key, branch, turn, tick, val))

	def universal_del(self, key: Key, branch: Branch, turn: Turn, tick: Tick):
		self.universal_set(key, branch, turn, tick, None)

	def count_all_table(self, tbl: str) -> int:
		return self.call("rowcount", tbl)

	def set_rule_triggers(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		flist: list[TriggerFuncName],
	):
		self.call(
			"insert1",
			"rule_triggers",
			{
				"rule": rule,
				"branch": branch,
				"turn": turn,
				"tick": tick,
				"triggers": self.pack(flist),
			},
		)

	def set_rule_prereqs(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		flist: list[PrereqFuncName],
	):
		self.call(
			"insert1",
			"rule_prereqs",
			{
				"rule": rule,
				"branch": branch,
				"turn": turn,
				"tick": tick,
				"prereqs": self.pack(flist),
			},
		)

	def set_rule_actions(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		flist: list[ActionFuncName],
	):
		self.call(
			"insert1",
			"rule_actions",
			{
				"rule": rule,
				"branch": branch,
				"turn": turn,
				"tick": tick,
				"actions": self.pack(flist),
			},
		)

	def set_rule_neighborhood(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		neighborhood: RuleNeighborhood,
	):
		self.call(
			"insert1",
			"rule_neighborhood",
			{
				"rule": rule,
				"branch": branch,
				"turn": turn,
				"tick": tick,
				"neighborhood": self.pack(neighborhood),
			},
		)

	def set_rule_big(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		big: RuleBig,
	) -> None:
		self.call(
			"insert1",
			"rule_big",
			{
				"rule": rule,
				"branch": branch,
				"turn": turn,
				"tick": tick,
				"big": big,
			},
		)

	@mutexed
	def set_rule(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		triggers: list[TriggerFuncName],
		prereqs: list[PrereqFuncName],
		actions: list[ActionFuncName],
		neighborhood: RuleNeighborhood,
		big: RuleBig,
	) -> None:
		self._inq.put(("silent", "insert1", ["rules", {"rule": rule}]))
		self._inq.put(
			(
				"silent",
				"insert1",
				[
					"rule_triggers",
					{
						"rule": rule,
						"branch": branch,
						"turn": turn,
						"tick": tick,
						"triggers": self.pack(triggers),
					},
				],
			)
		)
		self._inq.put(
			(
				"silent",
				"insert1",
				[
					"rule_prereqs",
					{
						"rule": rule,
						"branch": branch,
						"turn": turn,
						"tick": tick,
						"prereqs": self.pack(prereqs),
					},
				],
			)
		)
		self._inq.put(
			(
				"silent",
				"insert1",
				[
					"rule_actions",
					{
						"rule": rule,
						"branch": branch,
						"turn": turn,
						"tick": tick,
						"actions": self.pack(actions),
					},
				],
			)
		)
		self._inq.put(
			(
				"silent",
				"insert1",
				[
					"rule_neighborhood",
					{
						"rule": rule,
						"branch": branch,
						"turn": turn,
						"tick": tick,
						"neighborhood": self.pack(neighborhood),
					},
				],
			)
		)
		self._inq.put(
			(
				"silent",
				"insert1",
				[
					"rule_big",
					{
						"rule": rule,
						"branch": branch,
						"turn": turn,
						"tick": tick,
						"big": big,
					},
				],
			)
		)
		self._inq.put(("echo", "rule set"))
		if (got := self._outq.get()) != "rule set":
			raise RuntimeError("Failed to set rule", got)

	def set_rulebook(
		self,
		name: RulebookName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rules: Optional[list[RuleName]] = None,
		prio: RulebookPriority = 0.0,
	) -> None:
		pack = self.pack
		self.call(
			"insert1",
			"rulebooks",
			{
				"rulebook": pack(name),
				"branch": branch,
				"turn": turn,
				"tick": tick,
				"rules": pack(rules),
				"priority": prio,
			},
		)

	def _set_character_something_rulebook(
		self,
		tab: str,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	) -> None:
		pack = self.pack
		self.call(
			"insert1",
			tab,
			{
				"character": pack(char),
				"branch": branch,
				"turn": turn,
				"tick": tick,
				"rulebook": pack(rb),
			},
		)

	def set_character_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	) -> None:
		self._set_character_something_rulebook(
			"character_rulebook", char, branch, turn, tick, rb
		)

	def set_unit_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	) -> None:
		self._set_character_something_rulebook(
			"unit_rulebook", char, branch, turn, tick, rb
		)

	def set_character_thing_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	) -> None:
		self._set_character_something_rulebook(
			"character_thing_rulebook", char, branch, turn, tick, rb
		)

	def set_character_place_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	) -> None:
		self._set_character_something_rulebook(
			"character_place_rulebook", char, branch, turn, tick, rb
		)

	def set_character_portal_rulebook(
		self,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	) -> None:
		self._set_character_something_rulebook(
			"character_portal_rulebook", char, branch, turn, tick, rb
		)

	def rulebooks(self) -> Iterator[RulebookName]:
		return map(self.pack, self.call("rulebooks"))

	@pqbatch("node_rulebook")
	def _noderb2set(
		self,
		character: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rulebook: RulebookName,
	) -> tuple[bytes, bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return pack(character), pack(node), branch, turn, tick, pack(rulebook)

	def set_node_rulebook(
		self,
		character: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rulebook: RulebookName,
	) -> None:
		self._noderb2set.append(
			(character, node, branch, turn, tick, rulebook)
		)

	@pqbatch("portal_rulebook")
	def _portrb2set(
		self,
		character: CharName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rulebook: RulebookName,
	) -> tuple[bytes, bytes, bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return (
			pack(character),
			pack(orig),
			pack(dest),
			branch,
			turn,
			tick,
			pack(rulebook),
		)

	def set_portal_rulebook(
		self,
		character: CharName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rulebook: RulebookName,
	) -> None:
		self._portrb2set.append(
			(character, orig, dest, branch, turn, tick, rulebook)
		)

	@pqbatch("character_rules_handled")
	def _char_rules_handled(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, RuleName, Branch, Turn, Tick]:
		pack = self.pack
		return pack(character), pack(rulebook), rule, branch, turn, tick

	def handled_character_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> None:
		self._char_rules_handled.append(
			(character, rulebook, rule, branch, turn, tick)
		)

	@pqbatch("unit_rules_handled")
	def _unit_rules_handled(
		self,
		character: CharName,
		graph: CharName,
		unit: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, bytes, bytes, RuleName, Branch, Turn, Tick]:
		pack = self.pack
		return (
			pack(character),
			pack(graph),
			pack(unit),
			pack(rulebook),
			rule,
			branch,
			turn,
			tick,
		)

	def handled_unit_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		graph: CharName,
		unit: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> None:
		self._unit_rules_handled.append(
			(
				character,
				graph,
				unit,
				rulebook,
				rule,
				branch,
				turn,
				tick,
			)
		)

	@pqbatch("character_thing_rules_handled")
	def _char_thing_rules_handled(
		self,
		character: CharName,
		thing: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, bytes, RuleName, Branch, Turn, Tick]:
		pack = self.pack
		return (
			pack(character),
			pack(thing),
			pack(rulebook),
			rule,
			branch,
			turn,
			tick,
		)

	def handled_character_thing_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		thing: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> None:
		self._char_thing_rules_handled.append(
			(
				character,
				thing,
				rulebook,
				rule,
				branch,
				turn,
				tick,
			)
		)

	@pqbatch("character_place_rules_handled")
	def _char_place_rules_handled(
		self,
		character: CharName,
		place: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, bytes, RuleName, Branch, Turn, Tick]:
		pack = self.pack
		return (
			pack(character),
			pack(place),
			pack(rulebook),
			rule,
			branch,
			turn,
			tick,
		)

	def handled_character_place_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		place: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> None:
		self._char_place_rules_handled.append(
			(
				character,
				place,
				rulebook,
				rule,
				branch,
				turn,
				tick,
			)
		)

	@pqbatch("character_portal_rules_handled")
	def _char_portal_rules_handled(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, bytes, bytes, RuleName, Branch, Turn, Tick]:
		pack = self.pack
		return (
			pack(character),
			pack(orig),
			pack(dest),
			pack(rulebook),
			rule,
			branch,
			turn,
			tick,
		)

	def handled_character_portal_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> None:
		self._char_portal_rules_handled.append(
			(character, orig, dest, rulebook, rule, branch, turn, tick)
		)

	@pqbatch("node_rules_handled")
	def _node_rules_handled(
		self,
		character: CharName,
		node: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, bytes, RuleName, Branch, Turn, Tick]:
		pack = self.pack
		return (
			pack(character),
			pack(node),
			pack(rulebook),
			rule,
			branch,
			turn,
			tick,
		)

	def handled_node_rule(
		self,
		character: CharName,
		node: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> None:
		self._node_rules_handled.append(
			(character, node, rulebook, rule, branch, turn, tick)
		)

	@pqbatch("portal_rules_handled")
	def _portal_rules_handled(
		self,
		character: CharName,
		orig: NodeName,
		dest: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, bytes, bytes, RuleName, Branch, Turn, Tick]:
		pack = self.pack
		return (
			pack(character),
			pack(orig),
			pack(dest),
			pack(rulebook),
			rule,
			branch,
			turn,
			tick,
		)

	def handled_portal_rule(
		self,
		character: CharName,
		orig: NodeName,
		dest: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> None:
		self._portal_rules_handled.append(
			(character, orig, dest, rulebook, rule, branch, turn, tick)
		)

	@pqbatch("things")
	def _location(
		self,
		character: CharName,
		thing: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		location: NodeName,
	) -> tuple[bytes, bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return (
			pack(character),
			pack(thing),
			branch,
			turn,
			tick,
			pack(location),
		)

	def set_thing_loc(
		self,
		character: CharName,
		thing: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		loc: NodeName,
	) -> None:
		self._location.append((character, thing, branch, turn, tick, loc))

	@pqbatch("units")
	def _unitness(
		self,
		character: CharName,
		graph: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		is_unit: bool,
	) -> tuple[bytes, bytes, bytes, Branch, Turn, Tick, bool]:
		pack = self.pack
		return (
			pack(character),
			pack(graph),
			pack(node),
			branch,
			turn,
			tick,
			is_unit,
		)

	def unit_set(
		self,
		character: CharName,
		graph: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		is_unit: bool,
	) -> None:
		self._unitness.append(
			(character, graph, node, branch, turn, tick, is_unit)
		)

	def rulebook_set(
		self,
		rulebook: RulebookName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rules: list[RuleName],
	) -> None:
		pack = self.pack
		self.call(
			"insert1",
			"rulebooks",
			dict(
				rulebook=pack(rulebook),
				branch=branch,
				turn=turn,
				tick=tick,
				rules=pack(rules),
			),
		)

	def turns_completed_dump(self) -> Iterator[tuple[Branch, Turn]]:
		for d in self.call("dump", "turns_completed"):
			yield d["branch"], d["turn"]

	def complete_turn(
		self, branch: Branch, turn: Turn, discard_rules: bool = False
	) -> None:
		self.call("insert1", "turns_completed", dict(branch=branch, turn=turn))
		if discard_rules:
			self._char_rules_handled.clear()
			self._unit_rules_handled.clear()
			self._char_thing_rules_handled.clear()
			self._char_place_rules_handled.clear()
			self._char_portal_rules_handled.clear()
			self._node_rules_handled.clear()
			self._portal_rules_handled.clear()

	def new_turn(
		self,
		branch: Branch,
		turn: Turn,
		end_tick: Tick = 0,
		plan_end_tick: Tick = 0,
	) -> None:
		self.call(
			"insert1",
			"turns",
			dict(
				branch=branch,
				turn=turn,
				end_tick=end_tick,
				plan_end_tick=plan_end_tick,
			),
		)

	def graph_val_dump(self) -> Iterator[GraphValRowType]:
		unpack = self.unpack
		for d in self.call("dump", "graph_val"):
			yield (
				unpack(d["character"]),
				unpack(d["key"]),
				d["branch"],
				d["turn"],
				d["tick"],
				unpack(d["value"]),
			)

	def load_graph_val(
		self,
		graph: CharName,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[GraphValRowType]:
		if (turn_to is None) ^ (tick_to is None):
			raise ValueError("I need both or neither of turn_to and tick_to")
		self._graphvals2set()
		pack = self.pack
		unpack = self.unpack
		if turn_to is None:
			it = self.call(
				"load_graph_val_tick_to_end",
				pack(graph),
				branch,
				turn_from,
				tick_from,
			)
		else:
			it = self.call(
				"load_graph_val_tick_to_tick",
				pack(graph),
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		for key, turn, tick, value in it:
			yield graph, unpack(key), branch, turn, tick, unpack(value)

	@pqbatch("graph_val")
	def _graphvals2set(
		self,
		graph: CharName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		val: Value,
	) -> tuple[bytes, bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return pack(graph), pack(key), branch, turn, tick, pack(val)

	def graph_val_set(
		self,
		graph: CharName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		val: Value,
	) -> None:
		self._graphvals2set.append((graph, key, branch, turn, tick, val))

	def graph_val_del_time(self, branch: Branch, turn: Turn, tick: Tick):
		self.call("graph_val_del_time", branch, turn, tick)

	def characters(self) -> Iterator[tuple[CharName, Branch, Turn, Tick, str]]:
		unpack = self.unpack
		for d in self.call("dump", "graphs"):
			yield (
				unpack(d["graph"]),
				d["branch"],
				d["turn"],
				d["tick"],
				d["type"],
			)

	@pqbatch("nodes")
	def _nodes2set(
		self,
		graph: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		extant: bool,
	) -> tuple[bytes, bytes, Branch, Turn, Tick, bool]:
		pack = self.pack
		return pack(graph), pack(node), branch, turn, tick, extant

	def exist_node(
		self,
		graph: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		extant: bool,
	) -> None:
		self._nodes2set.append((graph, node, branch, turn, tick, extant))

	def nodes_del_time(self, branch: Branch, turn: Turn, tick: Tick) -> None:
		self.call("nodes_del_time", branch, turn, tick)

	def nodes_dump(self) -> Iterator[NodeRowType]:
		unpack = self.unpack
		for d in self.call("dump", "nodes"):
			yield (
				unpack(d["graph"]),
				unpack(d["node"]),
				d["branch"],
				d["turn"],
				d["tick"],
				d["extant"],
			)

	def load_nodes(
		self,
		graph: CharName,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[NodeRowType]:
		if (turn_to is None) ^ (tick_to is None):
			raise TypeError("I need both or neither of turn_to and tick_to")
		self._nodes2set()
		pack = self.pack
		unpack = self.unpack
		if turn_to is None:
			it = self.call(
				"load_nodes_tick_to_end",
				pack(graph),
				branch,
				turn_from,
				tick_from,
			)
		else:
			it = self.call(
				"load_nodes_tick_to_tick",
				pack(graph),
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		for node, turn, tick, extant in it:
			yield graph, unpack(node), branch, turn, tick, extant

	def node_val_dump(self) -> Iterator[NodeValRowType]:
		unpack = self.unpack
		for d in self.call("dump", "node_val"):
			yield (
				unpack(d["graph"]),
				unpack(d["node"]),
				unpack(d["key"]),
				d["branch"],
				d["turn"],
				d["tick"],
				unpack(d["value"]),
			)

	def load_node_val(
		self,
		graph: CharName,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[NodeValRowType]:
		if (turn_to is None) ^ (tick_to is None):
			raise TypeError("I need both or neither of turn_to and tick_to")
		self._nodevals2set()
		pack = self.pack
		unpack = self.unpack
		if turn_to is None:
			it = self.call(
				"load_node_val_tick_to_end",
				pack(graph),
				branch,
				turn_from,
				tick_from,
			)
		else:
			it = self.call(
				"load_node_val_tick_to_tick",
				pack(graph),
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		for node, key, turn, tick, value in it:
			yield (
				graph,
				unpack(node),
				unpack(key),
				branch,
				turn,
				tick,
				unpack(value),
			)

	@pqbatch("node_val")
	def _nodevals2set(
		self,
		graph: CharName,
		node: NodeName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		value: Any,
	) -> tuple[bytes, bytes, bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return (
			pack(graph),
			pack(node),
			pack(key),
			branch,
			turn,
			tick,
			pack(value),
		)

	def node_val_set(
		self,
		graph: CharName,
		node: NodeName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		value: Any,
	) -> None:
		self._nodevals2set.append(
			(graph, node, key, branch, turn, tick, value)
		)
		self._increc()

	def node_val_del_time(
		self, branch: Branch, turn: Turn, tick: Tick
	) -> None:
		self.call("node_val_del_time", branch, turn, tick)

	def edges_dump(self) -> Iterator[EdgeRowType]:
		unpack = self.unpack
		for d in self.call("dump", "edges"):
			yield (
				unpack(d["graph"]),
				unpack(d["orig"]),
				unpack(d["dest"]),
				d["branch"],
				d["turn"],
				d["tick"],
				d["extant"],
			)

	def load_edges(
		self,
		graph: CharName,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[EdgeRowType]:
		if (turn_to is None) ^ (tick_to is None):
			raise ValueError("I need both or neither of turn_to and tick_to")
		self._edges2set()
		pack = self.pack
		unpack = self.unpack
		if turn_to is None:
			it = self.call(
				"load_edges_tick_to_end",
				pack(graph),
				branch,
				turn_from,
				tick_from,
			)
		else:
			it = self.call(
				"load_edges_tick_to_tick",
				pack(graph),
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		for orig, dest, turn, tick, extant in it:
			yield (
				graph,
				unpack(orig),
				unpack(dest),
				branch,
				turn,
				tick,
				extant,
			)

	@pqbatch("edges")
	def _edges2set(
		self,
		graph: CharName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		extant: bool,
	) -> tuple[bytes, bytes, bytes, int, Branch, Turn, Tick, bool]:
		pack = self.pack
		return (
			pack(graph),
			pack(orig),
			pack(dest),
			branch,
			turn,
			tick,
			bool(extant),
		)

	def exist_edge(
		self,
		graph: CharName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		extant: bool,
	) -> None:
		self._edges2set.append((graph, orig, dest, branch, turn, tick, extant))

	def edges_del_time(self, branch: Branch, turn: Turn, tick: Tick) -> None:
		self.call("edges_del_time", branch, turn, tick)

	def edge_val_dump(self) -> Iterator[EdgeValRowType]:
		unpack = self.unpack
		for d in self.call("dump", "edge_val"):
			yield (
				unpack(d["character"]),
				unpack(d["orig"]),
				unpack(d["dest"]),
				d["branch"],
				d["turn"],
				d["tick"],
				unpack(d["value"]),
			)

	def load_edge_val(
		self,
		graph: CharName,
		branch: Branch,
		turn_from: Turn,
		tick_from: Tick,
		turn_to: Optional[Turn] = None,
		tick_to: Optional[Tick] = None,
	) -> Iterator[EdgeValRowType]:
		if (turn_to is None) ^ (tick_to is None):
			raise TypeError("I need both or neither of turn_to and tick_to")
		self._edgevals2set()
		pack = self.pack
		unpack = self.unpack
		if turn_to is None:
			it = self.call(
				"load_edge_val_tick_to_end",
				pack(graph),
				branch,
				turn_from,
				tick_from,
			)
		else:
			it = self.call(
				"load_edge_val_tick_to_tick",
				pack(graph),
				branch,
				turn_from,
				tick_from,
				turn_to,
				tick_to,
			)
		for orig, dest, key, turn, tick, value in it:
			yield (
				graph,
				unpack(orig),
				unpack(dest),
				unpack(key),
				branch,
				turn,
				tick,
				unpack(value),
			)

	@pqbatch("edge_val")
	def _edgevals2set(
		self,
		graph: CharName,
		orig: NodeName,
		dest: NodeName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		value: Value,
	) -> tuple[bytes, bytes, bytes, int, bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return (
			pack(graph),
			pack(orig),
			pack(dest),
			pack(key),
			branch,
			turn,
			tick,
			pack(value),
		)

	def edge_val_set(
		self,
		graph: CharName,
		orig: NodeName,
		dest: NodeName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		value: Value,
	) -> None:
		self._edgevals2set.append(
			(graph, orig, dest, key, branch, turn, tick, value)
		)

	def edge_val_del_time(
		self, branch: Branch, turn: Turn, tick: Tick
	) -> None:
		self.call("edge_val_del_time", branch, turn, tick)

	def plans_dump(self) -> Iterator[tuple[Plan, Branch, Turn, Tick]]:
		for d in self.call("dump", "plans"):
			yield d["plan_id"], d["branch"], d["turn"], d["tick"]

	def plans_insert(
		self, plan_id: Plan, branch: Branch, turn: Turn, tick: Tick
	) -> None:
		self.call(
			"insert1",
			"plans",
			dict(plan_id=plan_id, branch=branch, turn=turn, tick=tick),
		)

	def plans_insert_many(
		self, many: list[tuple[Plan, Branch, Turn, Tick]]
	) -> None:
		self.call(
			"insert",
			"plans",
			[
				dict(zip(("plan_id", "branch", "turn", "tick"), plan))
				for plan in many
			],
		)

	def plan_ticks_insert(self, plan_id: Plan, turn: Turn, tick: Tick) -> None:
		self._planticks2set.append((plan_id, turn, tick))

	def plan_ticks_dump(self) -> Iterator[tuple[Plan, Turn, Tick]]:
		for d in self.call("dump", "plan_ticks"):
			yield d["plan_id"], d["turn"], d["tick"]

	@pqbatch("keyframes_graphs")
	def _new_keyframes(
		self,
		graph: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		nodes: NodeKeyframe,
		edges: EdgeKeyframe,
		graph_val: GraphValKeyframe,
	) -> tuple[bytes, Branch, Turn, Tick, bytes, bytes, bytes]:
		pack = self.pack
		return (
			pack(graph),
			branch,
			turn,
			tick,
			pack(nodes),
			pack(edges),
			pack(graph_val),
		)

	def keyframe_graph_insert(
		self,
		graph: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		nodes: NodeKeyframe,
		edges: EdgeKeyframe,
		graph_val: GraphValKeyframe,
	) -> None:
		self._new_keyframes.append(
			(graph, branch, turn, tick, nodes, edges, graph_val)
		)
		self._new_keyframe_times.add((branch, turn, tick))
		self._all_keyframe_times.add((branch, turn, tick))

	def keyframe_insert(self, branch: Branch, turn: Turn, tick: Tick) -> None:
		self._new_keyframe_times.add((branch, turn, tick))
		self._all_keyframe_times.add((branch, turn, tick))

	@pqbatch("keyframe_extensions")
	def _new_keyframe_extensions(
		self,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		universal: UniversalKeyframe,
		rule: RuleKeyframe,
		rulebook: RulebookKeyframe,
	) -> tuple[Branch, Turn, Tick, bytes, bytes, bytes]:
		pack = self.pack
		return branch, turn, tick, pack(universal), pack(rule), pack(rulebook)

	def keyframe_extension_insert(
		self,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		universal: UniversalKeyframe,
		rule: RuleKeyframe,
		rulebook: RulebookKeyframe,
	) -> None:
		self._new_keyframe_extensions.append(
			(branch, turn, tick, universal, rule, rulebook)
		)
		self._new_keyframe_times.add((branch, turn, tick))

	def get_all_keyframe_graphs(
		self, branch: Branch, turn: Turn, tick: Tick
	) -> Iterator[
		tuple[CharName, NodeKeyframe, EdgeKeyframe, GraphValKeyframe]
	]:
		if (branch, turn, tick) not in self._all_keyframe_times:
			raise KeyframeError(branch, turn, tick)
		unpack = self.unpack
		for graph, nodes, edges, graph_val in self.call(
			"all_keyframe_graphs", branch, turn, tick
		):
			yield (
				unpack(graph),
				unpack(nodes),
				unpack(edges),
				unpack(graph_val),
			)

	def truncate_all(self) -> None:
		self.call("truncate_all")

	def close(self) -> None:
		self._inq.put("close")
		self._holder.existence_lock.acquire()
		self._holder.existence_lock.release()
		self._t.join()

	def commit(self) -> None:
		self.flush()
		self.call("commit")

	def initdb(self) -> None:
		ret = self.call("initdb")
		self._all_keyframe_times = self.call("all_keyframe_times")
		return ret

	def bookmark_items(self) -> Iterator[tuple[Key, Time]]:
		return iter(self.call("bookmark_items"))

	def set_bookmark(self, key: Key, time: Time) -> None:
		self.call("set_bookmark", key, *time)

	def del_bookmark(self, key: Key) -> None:
		self.call("del_bookmark", key)


class SQLAlchemyConnectionHolder(ConnectionHolder):
	def __init__(
		self,
		dbstring: str,
		connect_args: dict,
		inq: Queue,
		outq: Queue,
		tables: list[str],
	):
		self.lock = Lock()
		self.existence_lock.acquire(timeout=1)
		self._dbstring = dbstring
		self._connect_args = connect_args
		self.inq = inq
		self.outq = outq
		self.tables = tables

	def commit(self):
		self.transaction.commit()
		self.transaction = self.connection.begin()

	def init_table(self, tbl):
		return self.call_one("create_{}".format(tbl))

	def call_one(self, k, *largs, **kwargs):
		from sqlalchemy import CursorResult

		statement = self.sql[k].compile(dialect=self.engine.dialect)
		if hasattr(statement, "positiontup"):
			kwargs.update(dict(zip(statement.positiontup, largs)))
			repositioned = [kwargs[param] for param in statement.positiontup]
			self.logger.debug(
				f"SQLAlchemyConnectionHolder: calling {k}; {statement}  %  {repositioned}"
			)
			ret: CursorResult = self.connection.execute(statement, kwargs)
			self.logger.debug(
				f"SQLAlchemyConnectionHolder: {k} got {ret.rowcount} rows"
			)
			return ret
		elif largs:
			raise TypeError("{} is a DDL query, I think".format(k))
		self.logger.debug(
			f"SQLAlchemyConnectionHolder: calling {k}; {statement}"
		)
		ret: CursorResult = self.connection.execute(self.sql[k], kwargs)
		self.logger.debug(
			f"SQLAlchemyConnectionHolder: {k} got {ret.rowcount} rows"
		)
		return ret

	def call_many(self, k, largs):
		statement = self.sql[k].compile(dialect=self.engine.dialect)
		return self.connection.execute(
			statement,
			[dict(zip(statement.positiontup, larg)) for larg in largs],
		)

	def gather(self, meta):
		return gather_sql(meta)

	def run(self):
		dbstring = self._dbstring
		connect_args = self._connect_args
		if hasattr(self, "gather"):
			gather_sql = self.gather
		else:
			from .alchemy import gather_sql
		self.logger.debug("about to connect " + dbstring)
		self.engine = create_engine(dbstring, connect_args=connect_args)
		self.meta = MetaData()
		self.sql = gather_sql(self.meta)
		self.connection = self.engine.connect()
		self.transaction = self.connection.begin()
		self.logger.debug("transaction started")
		while True:
			inst = self.inq.get()
			if inst == "shutdown":
				self.transaction.close()
				self.connection.close()
				self.engine.dispose()
				self.existence_lock.release()
				self.inq.task_done()
				return
			if inst == "commit":
				self.commit()
				self.inq.task_done()
				continue
			if inst == "initdb":
				self.outq.put(self.initdb())
				self.inq.task_done()
				continue
			silent = False
			if inst[0] == "silent":
				inst = inst[1:]
				silent = True
			self.logger.debug(inst[:2])
			match inst:
				case ("echo", msg):
					self.outq.put(msg)
					self.inq.task_done()
				case ("echo", msg, _):
					self.outq.put(msg)
					self.inq.task_done()
				case ("select", qry, args):
					try:
						res = self.connection.execute(qry, args)
						if not silent:
							if hasattr(res, "returns_rows"):
								if res.returns_rows:
									o = list(res)
								else:
									o = None
							else:
								o = list(res)
					except Exception as ex:
						print(ex)
						if silent:
							print(f"while silenced: {ex}")
							sys.exit(repr(ex))
						o = ex
					if not silent:
						self.outq.put(o)
					self.inq.task_done()
				case ("one", cmd, args, kwargs):
					try:
						res = self.call_one(cmd, *args, **kwargs)
						if not silent:
							if hasattr(res, "returns_rows"):
								if res.returns_rows:
									o = list(res)
								else:
									o = None
							else:
								o = list(res)
					except Exception as ex:
						print(ex)
						if silent:
							print(f"while silenced: {ex}")
							sys.exit(repr(ex))
						o = ex
					if not silent:
						self.outq.put(o)
					self.inq.task_done()
				case ("many", cmd, several):
					try:
						res = self.call_many(cmd, several)
						if not silent:
							if hasattr(res, "returns_rows"):
								if res.returns_rows:
									o = list(res)
								else:
									o = None
							else:
								rez = list(res.fetchall())
								o = rez or None
					except Exception as ex:
						if silent:
							msg = "got exception while silenced: " + repr(ex)
							print(msg)
							sys.exit(msg)
						o = ex
					if not silent:
						self.outq.put(o)
					self.inq.task_done()

	def initdb(self) -> dict[bytes, bytes]:
		"""Set up the database schema, both for allegedb and the special
		extensions for lisien

		"""
		for table in self.tables:
			try:
				self.init_table(table)
			except OperationalError:
				pass
			except Exception as ex:
				return ex
		glob_d = dict(self.call_one("global_dump").fetchall())
		if SCHEMAVER_B not in glob_d:
			self.call_one("global_insert", SCHEMAVER_B, SCHEMA_VERSION)
		elif glob_d[SCHEMAVER_B] != SCHEMA_VERSION:
			return ValueError(
				"Unsupported database schema version", glob_d[SCHEMAVER_B]
			)
		return glob_d


class SQLAlchemyBatch(list):
	silent = True

	def __init__(
		self,
		qe: "SQLAlchemyQueryEngine",
		table: str,
		serialize_record: callable,
	):
		super().__init__()
		self._qe = qe
		self._table = table
		self._serialize_record = serialize_record
		self._argspec = inspect.getfullargspec(serialize_record)

	def __call__(self):
		if not self:
			return 0
		if self.silent:
			self._qe._inq.put(
				("silent", "many", self._table + "_insert", list(self))
			)
		else:
			self._qe.call_many(self._table + "_insert", list(self))
		n = len(self)
		self.clear()
		return n

	def copy(self) -> list:
		return list(super().__iter__())

	def __iter__(self):
		return starmap(self._serialize_record, super().__iter__())

	def __getitem__(self, item: int):
		return self._serialize_record(super().__getitem__(item))


def sqlbatch(table: str, serialize_record: callable = None):
	if serialize_record is None:
		return partial(sqlbatch, table)

	@cached_property
	def the_batch(self):
		return SQLAlchemyBatch(self, table, MethodType(serialize_record, self))

	return the_batch


class SQLAlchemyQueryEngine(AbstractQueryEngine):
	IntegrityError = IntegrityError
	OperationalError = OperationalError
	holder_cls = SQLAlchemyConnectionHolder
	tables = list(meta.tables.keys())
	kf_interval_override: callable

	def __init__(self, dbstring, connect_args, pack=None, unpack=None):
		dbstring = dbstring or "sqlite:///:memory:"
		self._inq = Queue()
		self._outq = Queue()
		self._holder = self.holder_cls(
			dbstring,
			connect_args,
			self._inq,
			self._outq,
			self.tables,
		)

		if pack is None:

			def pack(s: Any) -> bytes:
				return repr(s).encode()

		if unpack is None:
			from ast import literal_eval

			def unpack(b: bytes) -> Any:
				return literal_eval(b.decode())

		self.pack = pack
		self.unpack = unpack
		self._branches = {}
		self._new_keyframes: list[
			tuple[
				CharName,
				Branch,
				Turn,
				Tick,
				NodeKeyframe,
				EdgeKeyframe,
				GraphValKeyframe,
			]
		] = []
		self._new_keyframe_times: set[Time] = set()
		self._records = 0
		self.keyframe_interval = None
		self.snap_keyframe = lambda: None
		self._t = Thread(target=self._holder.run, daemon=True)
		self._t.start()
		self.initdb()

	@sqlbatch("universals")
	def _universals2set(
		self, key: Key, branch: Branch, turn: Turn, tick: Tick, val: Value
	) -> tuple[bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return pack(key), branch, turn, tick, pack(val)

	@sqlbatch("node_rulebook")
	def _node_rulebook_to_set(
		self,
		character: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rulebook: RulebookName,
	) -> tuple[bytes, bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return pack(character), pack(node), branch, turn, tick, pack(rulebook)

	@sqlbatch("portal_rulebook")
	def _portal_rulebook_to_set(
		self,
		character: CharName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rulebook: RulebookName,
	) -> tuple[bytes, bytes, bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return (
			pack(character),
			pack(orig),
			pack(dest),
			branch,
			turn,
			tick,
			pack(rulebook),
		)

	@sqlbatch("nodes")
	def _nodes2set(
		self,
		graph: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		extant: bool,
	) -> tuple[bytes, bytes, Branch, Turn, Tick, bool]:
		pack = self.pack
		return pack(graph), pack(node), branch, turn, tick, bool(extant)

	@sqlbatch("edges")
	def _edges2set(
		self,
		graph: CharName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		extant: bool,
	) -> tuple[bytes, bytes, bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return (
			pack(graph),
			pack(orig),
			pack(dest),
			branch,
			turn,
			tick,
			bool(extant),
		)

	@sqlbatch("node_val")
	def _nodevals2set(
		self,
		graph: CharName,
		node: NodeName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		value: Value,
	) -> tuple[bytes, bytes, bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return (
			pack(graph),
			pack(node),
			pack(key),
			branch,
			turn,
			tick,
			pack(value),
		)

	@sqlbatch("edge_val")
	def _edgevals2set(
		self,
		graph: CharName,
		orig: NodeName,
		dest: NodeName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		value: Value,
	) -> tuple[bytes, bytes, bytes, int, bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return (
			pack(graph),
			pack(orig),
			pack(dest),
			pack(key),
			branch,
			turn,
			tick,
			pack(value),
		)

	@sqlbatch("graph_val")
	def _graphvals2set(
		self,
		graph: CharName,
		key: Key,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		val: Value,
	) -> tuple[bytes, bytes, Branch, Turn, Tick, bytes]:
		pack = self.pack
		return pack(graph), pack(key), branch, turn, tick, pack(val)

	@sqlbatch("keyframe_extensions")
	def _new_keyframe_extensions(
		self,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		universal: UniversalKeyframe,
		rule: RuleKeyframe,
		rulebook: RulebookKeyframe,
	) -> tuple[Branch, Turn, Tick, bytes, bytes, bytes]:
		pack = self.pack
		return branch, turn, tick, pack(universal), pack(rule), pack(rulebook)

	@sqlbatch("character_rules_handled")
	def _char_rules_handled(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, RuleName, Branch, Turn, Tick]:
		(character, rulebook) = map(self.pack, (character, rulebook))
		return (character, rulebook, rule, branch, turn, tick)

	@sqlbatch("unit_rules_handled")
	def _unit_rules_handled(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		graph: CharName,
		unit: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, bytes, bytes, RuleName, Branch, Turn, Tick]:
		character, graph, unit, rulebook = map(
			self.pack, (character, graph, unit, rulebook)
		)
		return character, graph, unit, rulebook, rule, branch, turn, tick

	@sqlbatch("character_thing_rules_handled")
	def _char_thing_rules_handled(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		thing: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, RuleName, bytes, Branch, Turn, Tick]:
		character, thing, rulebook = map(
			self.pack, (character, thing, rulebook)
		)
		return (character, rulebook, rule, thing, branch, turn, tick)

	@sqlbatch("character_place_rules_handled")
	def _char_place_rules_handled(
		self,
		character: CharName,
		place: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, bytes, RuleName, Branch, Turn, Tick]:
		character, rulebook, place = map(
			self.pack, (character, rulebook, place)
		)
		return (character, place, rulebook, rule, branch, turn, tick)

	@sqlbatch("character_portal_rules_handled")
	def _char_portal_rules_handled(
		self,
		character: CharName,
		orig: NodeName,
		dest: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, bytes, bytes, RuleName, Branch, Turn, Tick]:
		character, rulebook, orig, dest = map(
			self.pack, (character, rulebook, orig, dest)
		)
		return character, orig, dest, rulebook, rule, branch, turn, tick

	@sqlbatch("node_rules_handled")
	def _node_rules_handled(
		self,
		character: CharName,
		node: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, bytes, RuleName, Branch, Turn, Tick]:
		(character, node, rulebook) = map(
			self.pack, (character, node, rulebook)
		)
		return (character, node, rulebook, rule, branch, turn, tick)

	@sqlbatch("portal_rules_handled")
	def _portal_rules_handled(
		self,
		character: CharName,
		orig: NodeName,
		dest: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> tuple[bytes, bytes, bytes, bytes, RuleName, Branch, Turn, Tick]:
		(character, orig, dest, rulebook) = map(
			self.pack, (character, orig, dest, rulebook)
		)
		return character, orig, dest, rulebook, rule, branch, turn, tick

	@sqlbatch("units")
	def _unitness(
		self,
		character: CharName,
		graph: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		is_unit: bool,
	) -> tuple[bytes, bytes, bytes, Branch, Turn, Tick, bool]:
		(character, graph, node) = map(self.pack, (character, graph, node))
		return character, graph, node, branch, turn, tick, is_unit

	@sqlbatch("things")
	def _location(
		self,
		character: CharName,
		thing: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		location: NodeName,
	) -> tuple[bytes, bytes, Branch, Turn, Tick, bytes]:
		(character, thing, location) = map(
			self.pack, (character, thing, location)
		)
		return character, thing, branch, turn, tick, location

	@mutexed
	def call_one(self, string, *args, **kwargs):
		if self._outq.unfinished_tasks != 0:
			raise RuntimeError(
				f"{self._outq.unfinished_tasks} unfinished tasks in output queue "
				"before call_one",
			)
		self._inq.put(("one", string, args, kwargs))
		ret = self._outq.get()
		self._outq.task_done()
		if self._outq.unfinished_tasks != 0:
			raise RuntimeError(
				f"{self._outq.unfinished_tasks} unfinished tasks in output "
				"queue after call_one",
			)
		if isinstance(ret, Exception):
			raise ret
		return ret

	def call_many(self, string, args):
		with self.mutex():
			self._inq.put(("many", string, args))
			ret = self._outq.get()
			self._outq.task_done()
		if isinstance(ret, Exception):
			raise ret
		return ret

	def execute(self, stmt, *args):
		if not isinstance(stmt, Select):
			raise TypeError("Only select statements should be executed")
		self.flush()
		with self.mutex():
			self._inq.put(("select", stmt, args))
			ret = self._outq.get()
			self._outq.task_done()
			return ret

	def bookmark_items(self) -> Iterator[tuple[Key, Time]]:
		unpack = self.unpack
		for key, branch, turn, tick in self.call_one("bookmarks_dump"):
			yield unpack(key), (branch, turn, tick)

	def set_bookmark(self, key: Key, time: Time) -> None:
		key = self.pack(key)
		try:
			self.call_one("bookmarks_insert", key, *time)
		except IntegrityError:
			self.call_one("update_bookmark", key, *time)

	def del_bookmark(self, key: Key) -> None:
		self.call_one("delete_bookmark", self.pack(key))

	def keyframes_dump(self) -> Iterator[tuple[Branch, Turn, Tick]]:
		return self.call_one("keyframes_dump")

	def new_graph(
		self, graph: CharName, branch: Branch, turn: Turn, tick: Tick, typ: str
	) -> None:
		"""Declare a new graph by this name of this type."""
		graph = self.pack(graph)
		return self.call_one("graphs_insert", graph, branch, turn, tick, typ)

	def keyframe_insert(self, branch: Branch, turn: Turn, tick: Tick):
		self._new_keyframe_times.add((branch, turn, tick))

	def keyframe_graph_insert(
		self,
		graph: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		nodes: NodeKeyframe,
		edges: EdgeKeyframe,
		graph_val: GraphValKeyframe,
	) -> None:
		self._new_keyframes.append(
			(graph, branch, turn, tick, nodes, edges, graph_val)
		)
		self._all_keyframe_times.add((branch, turn, tick))

	def keyframes_graphs(
		self,
	) -> Iterator[tuple[CharName, Branch, Turn, Tick]]:
		unpack = self.unpack
		for graph, branch, turn, tick in self.call_one(
			"keyframes_graphs_list"
		):
			yield unpack(graph), branch, turn, tick

	def get_all_keyframe_graphs(
		self, branch: Branch, turn: Turn, tick: Tick
	) -> Iterator[
		tuple[CharName, NodeKeyframe, EdgeKeyframe, GraphValKeyframe]
	]:
		if (branch, turn, tick) not in self._all_keyframe_times:
			raise KeyframeError(branch, turn, tick)
		unpack = self.unpack
		for graph, nodes, edges, graph_val in self.call_one(
			"all_graphs_in_keyframe", branch, turn, tick
		):
			yield (
				unpack(graph),
				unpack(nodes),
				unpack(edges),
				unpack(graph_val),
			)

	def delete_keyframe(self, branch: Branch, turn: Turn, tick: Tick) -> None:
		def keyframe_filter(tup: tuple):
			_, kfbranch, kfturn, kftick, __, ___, ____ = tup
			return (kfbranch, kfturn, kftick) != (branch, turn, tick)

		def keyframe_extension_filter(tup: tuple):
			kfbranch, kfturn, kftick, _, __, ___ = tup
			return (kfbranch, kfturn, kftick) != (branch, turn, tick)

		new_keyframes = list(filter(keyframe_filter, self._new_keyframes))
		self._new_keyframes.clear()
		self._new_keyframes.extend(new_keyframes)
		self._new_keyframe_times.discard((branch, turn, tick))
		new_keyframe_extensions = self._new_keyframe_extensions.copy()
		self._new_keyframe_extensions.clear()
		self._new_keyframe_extensions.extend(
			filter(keyframe_extension_filter, new_keyframe_extensions)
		)
		with self._holder.lock:
			self._inq.put(
				(
					"silent",
					"one",
					"delete_from_keyframes",
					(branch, turn, tick),
					{},
				)
			)
			self._inq.put(
				(
					"silent",
					"one",
					"delete_from_keyframes_graphs",
					(branch, turn, tick),
					{},
				)
			)
			self._inq.put(
				(
					"silent",
					"one",
					"delete_from_keyframe_extensions",
					(branch, turn, tick),
					{},
				)
			)
			self._inq.put(("echo", "done deleting keyframe"))
			if (got := self._outq.get()) != "done deleting keyframe":
				raise RuntimeError("Didn't delete keyframe right", got)
			self._outq.task_done()

	def have_branch(self, branch):
		"""Return whether the branch thus named exists in the database."""
		return bool(self.call_one("ctbranch", branch)[0][0])

	def all_branches(
		self,
	) -> Iterator[tuple[Branch, Branch, Turn, Tick, Turn, Tick]]:
		"""Return all the branch data in tuples of (branch, parent,
		start_turn, start_tick, end_turn, end_tick).

		"""
		return self.call_one("branches_dump")

	def global_get(self, key: Key) -> Value:
		"""Return the value for the given key in the ``globals`` table."""
		key = self.pack(key)
		r = self.call_one("global_get", key)[0]
		if r is None:
			raise KeyError("Not set")
		return self.unpack(r[0])

	def global_items(self) -> Iterator[tuple[Key, Value]]:
		"""Iterate over (key, value) pairs in the ``globals`` table."""
		unpack = self.unpack
		dumped = self.call_one("global_dump")
		for k, v in dumped:
			yield (unpack(k), unpack(v))

	def get_branch(self) -> Branch:
		v = self.call_one("global_get", self.pack("branch"))[0]
		if v is None:
			return self.globl["main_branch"]
		return self.unpack(v[0])

	def get_turn(self) -> Turn:
		v = self.call_one("global_get", self.pack("turn"))[0]
		if v is None:
			return 0
		return self.unpack(v[0])

	def get_tick(self) -> Tick:
		v = self.call_one("global_get", self.pack("tick"))[0]
		if v is None:
			return 0
		return self.unpack(v[0])

	def global_set(self, key: Key, value: Value) -> None:
		"""Set ``key`` to ``value`` globally (not at any particular branch or
		revision)

		"""
		(key, value) = map(self.pack, (key, value))
		try:
			return self.call_one("global_insert", key, value)
		except IntegrityError:
			try:
				return self.call_one("global_update", value, key)
			except IntegrityError:
				self.commit()
				return self.call_one("global_update", value, key)

	def global_del(self, key: Key) -> None:
		"""Delete the global record for the key."""
		key = self.pack(key)
		return self.call_one("global_del", key)

	def new_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
	) -> None:
		"""Declare that the ``branch`` is descended from ``parent`` at
		``parent_turn``, ``parent_tick``

		"""
		return self.call_one(
			"branches_insert",
			branch,
			parent,
			parent_turn,
			parent_tick,
			parent_turn,
			parent_tick,
		)

	def update_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
		end_turn: Turn,
		end_tick: Tick,
	) -> None:
		return self.call_one(
			"update_branches",
			parent,
			parent_turn,
			parent_tick,
			end_turn,
			end_tick,
			branch,
		)

	def set_branch(
		self,
		branch: Branch,
		parent: Branch,
		parent_turn: Turn,
		parent_tick: Tick,
		end_turn: Turn,
		end_tick: Tick,
	):
		try:
			self.call_one(
				"branches_insert",
				branch,
				parent,
				parent_turn,
				parent_tick,
				end_turn,
				end_tick,
			)
		except IntegrityError:
			try:
				self.update_branch(
					branch,
					parent,
					parent_turn,
					parent_tick,
					end_turn,
					end_tick,
				)
			except IntegrityError:
				self.commit()
				self.update_branch(
					branch,
					parent,
					parent_turn,
					parent_tick,
					end_turn,
					end_tick,
				)

	def new_turn(
		self,
		branch: Branch,
		turn: Turn,
		end_tick: Tick = 0,
		plan_end_tick: Tick = 0,
	):
		return self.call_one(
			"turns_insert", branch, turn, end_tick, plan_end_tick
		)

	def update_turn(
		self, branch: Branch, turn: Turn, end_tick: Tick, plan_end_tick: Tick
	):
		return self.call_one(
			"update_turns", end_tick, plan_end_tick, branch, turn
		)

	def set_turn(
		self, branch: Branch, turn: Turn, end_tick: Tick, plan_end_tick: Tick
	):
		try:
			return self.call_one(
				"turns_insert", branch, turn, end_tick, plan_end_tick
			)
		except IntegrityError:
			return self.call_one(
				"update_turns", end_tick, plan_end_tick, branch, turn
			)

	def turns_dump(self) -> Iterator[tuple[Branch, Turn, Tick, Tick]]:
		return self.call_one("turns_dump")

	def graph_val_dump(self) -> Iterator[GraphValRowType]:
		"""Yield the entire contents of the graph_val table."""
		self._flush_graph_val()
		unpack = self.unpack
		for graph, key, branch, turn, tick, value in self.call_one(
			"graph_val_dump"
		):
			yield (
				unpack(graph),
				unpack(key),
				branch,
				turn,
				tick,
				unpack(value),
			)

	def load_graph_val(
		self, graph, branch, turn_from, tick_from, turn_to=None, tick_to=None
	) -> Iterator[GraphValRowType]:
		if (turn_to is None) ^ (tick_to is None):
			raise ValueError("I need both or neither of turn_to and tick_to")
		self._flush_graph_val()
		pack = self.pack
		unpack = self.unpack
		if turn_to is None:
			it = self.call_one(
				"load_graph_val_tick_to_end",
				pack(graph),
				branch,
				turn_from,
				turn_from,
				tick_from,
			)
		else:
			it = self.call_one(
				"load_graph_val_tick_to_tick",
				pack(graph),
				branch,
				turn_from,
				turn_from,
				tick_from,
				turn_to,
				turn_to,
				tick_to,
			)
		for key, turn, tick, value in it:
			yield graph, unpack(key), branch, turn, tick, unpack(value)

	def _flush_graph_val(self):
		"""Send all new and changed graph values to the database."""
		if not self._graphvals2set:
			return
		self._graphvals2set()

	def graph_val_set(self, graph, key, branch, turn, tick, value):
		self._graphvals2set.append((graph, key, branch, turn, tick, value))
		self._increc()

	def graph_val_del_time(self, branch, turn, tick):
		self._flush_graph_val()
		self.call_one("graph_val_del_time", branch, turn, tick)

	def graphs_types(
		self,
		branch,
		turn_from,
		tick_from,
		turn_to=None,
		tick_to=None,
	):
		unpack = self.unpack
		if turn_to is None:
			if tick_to is not None:
				raise ValueError("Need both or neither of turn_to and tick_to")
			for graph, turn, tick, typ in self.call_one(
				"graphs_after", branch, turn_from, turn_from, tick_from
			):
				yield unpack(graph), branch, turn, tick, typ
			return
		else:
			if tick_to is None:
				raise ValueError("Need both or neither of turn_to and tick_to")
		for graph, turn, tick, typ in self.call_one(
			"graphs_between",
			branch,
			turn_from,
			turn_from,
			tick_from,
			turn_to,
			turn_to,
			tick_to,
		):
			yield unpack(graph), branch, turn, tick, typ

	def characters(self):
		unpack = self.unpack
		for graph, branch, turn, tick, typ in self.call_one("graphs_dump"):
			yield unpack(graph), branch, turn, tick, typ

	def graphs_insert(
		self, graph: Key, branch: str, turn: int, tick: int, typ: str
	) -> None:
		self.call_one(
			"graphs_insert", self.pack(graph), branch, turn, tick, typ
		)

	def _flush_nodes(self):
		self._nodes2set()

	def exist_node(self, graph, node, branch, turn, tick, extant):
		"""Declare that the node exists or doesn't.

		Inserts a new record or updates an old one, as needed.

		"""
		self._nodes2set.append((graph, node, branch, turn, tick, extant))
		self._increc()

	def nodes_del_time(self, branch, turn, tick):
		self._flush_nodes()
		self.call_one("nodes_del_time", branch, turn, tick)

	def nodes_dump(self) -> Iterator[NodeRowType]:
		"""Dump the entire contents of the nodes table."""
		self._flush_nodes()
		unpack = self.unpack
		for graph, node, branch, turn, tick, extant in self.call_one(
			"nodes_dump"
		):
			yield (
				unpack(graph),
				unpack(node),
				branch,
				turn,
				tick,
				bool(extant),
			)

	def _iter_nodes(
		self, graph, branch, turn_from, tick_from, turn_to=None, tick_to=None
	) -> Iterator[NodeRowType]:
		if (turn_to is None) ^ (tick_to is None):
			raise TypeError("I need both or neither of turn_to and tick_to")
		self._flush_nodes()
		pack = self.pack
		unpack = self.unpack
		if turn_to is None:
			it = self.call_one(
				"load_nodes_tick_to_end",
				pack(graph),
				branch,
				turn_from,
				turn_from,
				tick_from,
			)
		else:
			it = self.call_one(
				"load_nodes_tick_to_tick",
				pack(graph),
				branch,
				turn_from,
				turn_from,
				tick_from,
				turn_to,
				turn_to,
				tick_to,
			)
		for node, turn, tick, extant in it:
			yield graph, unpack(node), branch, turn, tick, extant

	def load_nodes(
		self, graph, branch, turn_from, tick_from, turn_to=None, tick_to=None
	) -> list[NodeRowType]:
		return list(
			self._iter_nodes(
				graph, branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def node_val_dump(self) -> Iterator[NodeValRowType]:
		"""Yield the entire contents of the node_val table."""
		self._flush_node_val()
		unpack = self.unpack
		for graph, node, key, branch, turn, tick, value in self.call_one(
			"node_val_dump"
		):
			yield (
				unpack(graph),
				unpack(node),
				unpack(key),
				branch,
				turn,
				tick,
				unpack(value),
			)

	def _iter_node_val(
		self, graph, branch, turn_from, tick_from, turn_to=None, tick_to=None
	) -> Iterator[NodeValRowType]:
		if (turn_to is None) ^ (tick_to is None):
			raise TypeError("I need both or neither of turn_to and tick_to")
		self._flush_node_val()
		pack = self.pack
		unpack = self.unpack
		if turn_to is None:
			it = self.call_one(
				"load_node_val_tick_to_end",
				pack(graph),
				branch,
				turn_from,
				turn_from,
				tick_from,
			)
		else:
			it = self.call_one(
				"load_node_val_tick_to_tick",
				pack(graph),
				branch,
				turn_from,
				turn_from,
				tick_from,
				turn_to,
				turn_to,
				tick_to,
			)
		for node, key, turn, tick, value in it:
			yield (
				graph,
				unpack(node),
				unpack(key),
				branch,
				turn,
				tick,
				unpack(value),
			)

	def load_node_val(
		self, graph, branch, turn_from, tick_from, turn_to=None, tick_to=None
	):
		return list(
			self._iter_node_val(
				graph, branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _flush_node_val(self):
		if not self._nodevals2set:
			return
		self._nodevals2set()

	def node_val_set(self, graph, node, key, branch, turn, tick, value):
		"""Set a key-value pair on a node at a specific branch and revision"""
		self._nodevals2set.append(
			(graph, node, key, branch, turn, tick, value)
		)

	def node_val_del_time(self, branch, turn, tick):
		self._flush_node_val()
		self.call_one("node_val_del_time", branch, turn, tick)

	def edges_dump(self) -> Iterator[EdgeRowType]:
		"""Dump the entire contents of the edges table."""
		self._flush_edges()
		unpack = self.unpack
		for (
			graph,
			orig,
			dest,
			branch,
			turn,
			tick,
			extant,
		) in self.call_one("edges_dump"):
			yield (
				unpack(graph),
				unpack(orig),
				unpack(dest),
				branch,
				turn,
				tick,
				bool(extant),
			)

	def iter_edges(
		self, graph, branch, turn_from, tick_from, turn_to=None, tick_to=None
	) -> Iterator[EdgeRowType]:
		if (turn_to is None) ^ (tick_to is None):
			raise ValueError("I need both or neither of turn_to and tick_to")
		self._edgevals2set()
		pack = self.pack
		unpack = self.unpack
		if turn_to is None:
			it = self.call_one(
				"load_edges_tick_to_end",
				pack(graph),
				branch,
				turn_from,
				turn_from,
				tick_from,
			)
		else:
			it = self.call_one(
				"load_edges_tick_to_tick",
				pack(graph),
				branch,
				turn_from,
				turn_from,
				tick_from,
				turn_to,
				turn_to,
				tick_to,
			)
		for orig, dest, turn, tick, extant in it:
			yield (
				graph,
				unpack(orig),
				unpack(dest),
				branch,
				turn,
				tick,
				extant,
			)

	def load_edges(
		self, graph, branch, turn_from, tick_from, turn_to=None, tick_to=None
	) -> list[EdgeRowType]:
		return list(
			self.iter_edges(
				graph, branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _pack_edge2set(self, tup):
		graph, orig, dest, branch, turn, tick, extant = tup
		pack = self.pack
		return (
			pack(graph),
			pack(orig),
			pack(dest),
			branch,
			turn,
			tick,
			extant,
		)

	def _flush_edges(self):
		if not self._edges2set:
			return
		self._edges2set()

	def exist_edge(self, graph, orig, dest, branch, turn, tick, extant):
		"""Declare whether or not this edge exists."""
		self._edges2set.append((graph, orig, dest, branch, turn, tick, extant))
		self._increc()

	def edges_del_time(self, branch, turn, tick):
		self._flush_edges()
		self.call_one("edges_del_time", branch, turn, tick)

	def edge_val_dump(self) -> Iterator[EdgeValRowType]:
		"""Yield the entire contents of the edge_val table."""
		self._edgevals2set()
		unpack = self.unpack
		for (
			graph,
			orig,
			dest,
			key,
			branch,
			turn,
			tick,
			value,
		) in self.call_one("edge_val_dump"):
			yield (
				unpack(graph),
				unpack(orig),
				unpack(dest),
				unpack(key),
				branch,
				turn,
				tick,
				unpack(value),
			)

	def _iter_edge_val(
		self, graph, branch, turn_from, tick_from, turn_to=None, tick_to=None
	) -> Iterator[EdgeValRowType]:
		if (turn_to is None) ^ (tick_to is None):
			raise TypeError("I need both or neither of turn_to and tick_to")
		self._edgevals2set()
		pack = self.pack
		unpack = self.unpack
		if turn_to is None:
			it = self.call_one(
				"load_edge_val_tick_to_end",
				pack(graph),
				branch,
				turn_from,
				turn_from,
				tick_from,
			)
		else:
			it = self.call_one(
				"load_edge_val_tick_to_tick",
				pack(graph),
				branch,
				turn_from,
				turn_from,
				tick_from,
				turn_to,
				turn_to,
				tick_to,
			)
		for orig, dest, key, turn, tick, value in it:
			yield (
				graph,
				unpack(orig),
				unpack(dest),
				unpack(key),
				branch,
				turn,
				tick,
				unpack(value),
			)

	def load_edge_val(
		self, graph, branch, turn_from, tick_from, turn_to=None, tick_to=None
	):
		return list(
			self._iter_edge_val(
				graph, branch, turn_from, tick_from, turn_to, tick_to
			)
		)

	def _pack_edgeval2set(self, tup):
		graph, orig, dest, key, branch, turn, tick, value = tup
		pack = self.pack
		return (
			pack(graph),
			pack(orig),
			pack(dest),
			pack(key),
			branch,
			turn,
			tick,
			pack(value),
		)

	def edge_val_set(self, graph, orig, dest, key, branch, turn, tick, value):
		"""Set this key of this edge to this value."""
		self._edgevals2set.append(
			(graph, orig, dest, key, branch, turn, tick, value)
		)
		self._increc()

	def edge_val_del_time(self, branch, turn, tick):
		self._edgevals2set()
		self.call_one("edge_val_del_time", branch, turn, tick)

	def plans_dump(self):
		return self.call_one("plans_dump")

	def plans_insert(self, plan_id, branch, turn, tick):
		return self.call_one("plans_insert", plan_id, branch, turn, tick)

	def plans_insert_many(self, many):
		return self.call_many("plans_insert", many)

	def plan_ticks_insert(self, plan_id, turn, tick):
		return self.call_one("plan_ticks_insert", plan_id, turn, tick)

	def plan_ticks_dump(self):
		return self.call_one("plan_ticks_dump")

	@garbage
	@mutexed
	def flush(self):
		"""Put all pending changes into the SQL transaction."""
		if not any(
			(
				self._universals2set,
				self._nodes2set,
				self._edges2set,
				self._node_rulebook_to_set,
				self._portal_rulebook_to_set,
				self._graphvals2set,
				self._nodevals2set,
				self._edgevals2set,
				self._new_keyframes,
				self._new_keyframe_times,
				self._new_keyframe_extensions,
				self._unitness,
				self._location,
				self._char_rules_handled,
				self._char_thing_rules_handled,
				self._char_place_rules_handled,
				self._char_portal_rules_handled,
				self._unit_rules_handled,
				self._node_rules_handled,
				self._portal_rules_handled,
			)
		):
			return
		self._inq.put(("echo", "ready"))
		readied = self._outq.get()
		if readied != "ready":
			raise RuntimeError("Not ready to flush", readied)
		self._outq.task_done()
		self._flush()
		self._inq.put(("echo", "flushed"))
		flushed = self._outq.get()
		if flushed != "flushed":
			raise RuntimeError("Failed flush", flushed)
		self._outq.task_done()

	def _flush(self):
		pack = self.pack
		put = self._inq.put
		self._universals2set()
		self._nodes2set()
		self._edges2set()
		self._node_rulebook_to_set()
		self._portal_rulebook_to_set()
		self._graphvals2set()
		self._nodevals2set()
		self._edgevals2set()
		if self._new_keyframe_times:
			put(
				(
					"silent",
					"many",
					"keyframes_insert",
					list(self._new_keyframe_times),
				)
			)
			self._new_keyframe_times = set()
		if self._new_keyframes:
			# use only the most recent version of any given keyframe
			kfs = {}
			for (
				graph,
				branch,
				turn,
				tick,
				nodes,
				edges,
				graph_val,
			) in self._new_keyframes:
				kfs[graph, branch, turn, tick] = (nodes, edges, graph_val)
			put(
				(
					"silent",
					"many",
					"delete_keyframe_graph",
					[
						(pack(graph), branch, turn, tick)
						for (graph, branch, turn, tick) in kfs
					],
				)
			)
			put(
				(
					"silent",
					"many",
					"keyframes_graphs_insert",
					[
						(
							pack(graph),
							branch,
							turn,
							tick,
							pack(nodes),
							pack(edges),
							pack(graph_val),
						)
						for (graph, branch, turn, tick), (
							nodes,
							edges,
							graph_val,
						) in kfs.items()
					],
				)
			)
			self._new_keyframes = []
		self._new_keyframe_extensions()

		put = self._inq.put

		if self._unitness:
			put(
				(
					"silent",
					"many",
					"del_units_after",
					[
						(character, graph, node, branch, turn, turn, tick)
						for (
							character,
							graph,
							node,
							branch,
							turn,
							tick,
							_,
						) in self._unitness
					],
				)
			)
			self._unitness()
		if self._location:
			put(
				(
					"silent",
					"many",
					"del_things_after",
					[
						(character, thing, branch, turn, turn, tick)
						for (
							character,
							thing,
							branch,
							turn,
							tick,
							_,
						) in self._location
					],
				)
			)
			self._location()
		self._char_rules_handled()
		self._char_thing_rules_handled()
		self._char_place_rules_handled()
		self._char_portal_rules_handled()
		self._unit_rules_handled()
		self._node_rules_handled()
		self._portal_rules_handled()

	def commit(self):
		"""Commit the transaction"""
		self._inq.put("commit")
		self._inq.join()
		if (got := self.echo("committed")) != "committed":
			raise RuntimeError("Failed commit", got)

	def close(self):
		"""Commit the transaction, then close the connection"""
		self._inq.put("shutdown")
		self._holder.existence_lock.acquire()
		self._holder.existence_lock.release()
		self._t.join()

	def initdb(self):
		if hasattr(self, "_initialized"):
			raise RuntimeError("Tried to initialize database twice")
		self._initialized = True
		with self.mutex():
			self._inq.put("initdb")
			globals = self._outq.get()
			self._outq.task_done()
			if isinstance(globals, Exception):
				raise globals
			self.globl = GlobalKeyValueStore(
				self,
				{self.unpack(k): self.unpack(v) for (k, v) in globals.items()},
			)
			self._inq.put(("one", "keyframes_dump", (), {}))
			ret = self._outq.get()
			self._outq.task_done()
			if isinstance(ret, Exception):
				raise ret
			self._all_keyframe_times = set(ret)
		if "main_branch" not in self.globl:
			self.global_set("main_branch", "trunk")
			self.globl.data["main_branch"] = "trunk"
		if "branch" not in self.globl:
			self.global_set("branch", "trunk")
			self.globl.data["branch"] = "trunk"
		if "turn" not in self.globl:
			self.global_set("turn", 0)
			self.globl.data["turn"] = 0
		if "tick" not in self.globl:
			self.global_set("tick", 0)
			self.globl.data["tick"] = 0

	def truncate_all(self):
		"""Delete all data from every table"""
		for table in self.tables:
			try:
				self.call_one("truncate_" + table)
			except OperationalError:
				pass  # table wasn't created yet
		self.commit()

	def keyframe_extension_insert(
		self,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		universal: UniversalKeyframe,
		rule: RuleKeyframe,
		rulebook: RulebookKeyframe,
	):
		self._new_keyframe_extensions.append(
			(
				branch,
				turn,
				tick,
				universal,
				rule,
				rulebook,
			)
		)
		self._new_keyframe_times.add((branch, turn, tick))

	def get_keyframe_extensions(self, branch: Branch, turn: Turn, tick: Tick):
		if (branch, turn, tick) not in self._all_keyframe_times:
			raise KeyframeError(branch, turn, tick)
		self.flush()
		unpack = self.unpack
		exts = self.call_one("get_keyframe_extensions", branch, turn, tick)
		if not exts:
			raise KeyframeError(branch, turn, tick)
		assert len(exts) == 1, f"Incoherent keyframe {branch, turn, tick}"
		universal, rule, rulebook = exts[0]
		return (
			unpack(universal),
			unpack(rule),
			unpack(rulebook),
		)

	def universals_dump(self):
		unpack = self.unpack
		for key, branch, turn, tick, value in self.call_one("universals_dump"):
			yield unpack(key), branch, turn, tick, unpack(value)

	def rulebooks_dump(self):
		unpack = self.unpack
		for rulebook, branch, turn, tick, rules, prio in self.call_one(
			"rulebooks_dump"
		):
			yield unpack(rulebook), branch, turn, tick, (unpack(rules), prio)

	def _rule_dump(self, typ):
		unpack = self.unpack
		for rule, branch, turn, tick, lst in self.call_one(
			"rule_{}_dump".format(typ)
		):
			yield rule, branch, turn, tick, unpack(lst)

	def rule_triggers_dump(self):
		return self._rule_dump("triggers")

	def rule_prereqs_dump(self):
		return self._rule_dump("prereqs")

	def rule_actions_dump(self):
		return self._rule_dump("actions")

	def rule_neighborhood_dump(self):
		return self._rule_dump("neighborhood")

	def node_rulebook_dump(self):
		unpack = self.unpack
		for character, node, branch, turn, tick, rulebook in self.call_one(
			"node_rulebook_dump"
		):
			yield (
				unpack(character),
				unpack(node),
				branch,
				turn,
				tick,
				unpack(rulebook),
			)

	def portal_rulebook_dump(self):
		unpack = self.unpack
		for (
			character,
			orig,
			dest,
			branch,
			turn,
			tick,
			rulebook,
		) in self.call_one("portal_rulebook_dump"):
			yield (
				unpack(character),
				unpack(orig),
				unpack(dest),
				branch,
				turn,
				tick,
				unpack(rulebook),
			)

	def _charactery_rulebook_dump(self, qry):
		unpack = self.unpack
		for character, branch, turn, tick, rulebook in self.call_one(
			qry + "_rulebook_dump"
		):
			yield unpack(character), branch, turn, tick, unpack(rulebook)

	character_rulebook_dump = partialmethod(
		_charactery_rulebook_dump, "character"
	)
	unit_rulebook_dump = partialmethod(_charactery_rulebook_dump, "unit")
	character_thing_rulebook_dump = partialmethod(
		_charactery_rulebook_dump, "character_thing"
	)
	character_place_rulebook_dump = partialmethod(
		_charactery_rulebook_dump, "character_place"
	)
	character_portal_rulebook_dump = partialmethod(
		_charactery_rulebook_dump, "character_portal"
	)

	def character_rules_handled_dump(self):
		unpack = self.unpack
		for character, rulebook, rule, branch, turn, tick in self.call_one(
			"character_rules_handled_dump"
		):
			yield unpack(character), unpack(rulebook), rule, branch, turn, tick

	def character_rules_changes_dump(self):
		unpack = self.unpack
		for (
			character,
			rulebook,
			rule,
			branch,
			turn,
			tick,
			handled_branch,
			handled_turn,
		) in self.call_one("character_rules_changes_dump"):
			yield (
				unpack(character),
				unpack(rulebook),
				rule,
				branch,
				turn,
				tick,
				handled_branch,
				handled_turn,
			)

	def unit_rules_handled_dump(self):
		unpack = self.unpack
		for (
			character,
			graph,
			unit,
			rulebook,
			rule,
			branch,
			turn,
			tick,
		) in self.call_one("unit_rules_handled_dump"):
			yield (
				unpack(character),
				unpack(graph),
				unpack(unit),
				unpack(rulebook),
				rule,
				branch,
				turn,
				tick,
			)

	def unit_rules_changes_dump(self):
		jl = self.unpack
		for (
			character,
			rulebook,
			rule,
			graph,
			unit,
			branch,
			turn,
			tick,
			handled_branch,
			handled_turn,
		) in self.call_one("unit_rules_changes_dump"):
			yield (
				jl(character),
				jl(rulebook),
				rule,
				jl(graph),
				jl(unit),
				branch,
				turn,
				tick,
				handled_branch,
				handled_turn,
			)

	def character_thing_rules_handled_dump(self):
		unpack = self.unpack
		for (
			character,
			thing,
			rulebook,
			rule,
			branch,
			turn,
			tick,
		) in self.call_one("character_thing_rules_handled_dump"):
			yield (
				unpack(character),
				unpack(thing),
				unpack(rulebook),
				rule,
				branch,
				turn,
				tick,
			)

	def character_place_rules_handled_dump(self):
		unpack = self.unpack
		for (
			character,
			place,
			rulebook,
			rule,
			branch,
			turn,
			tick,
		) in self.call_one("character_place_rules_handled_dump"):
			yield (
				unpack(character),
				unpack(place),
				unpack(rulebook),
				rule,
				branch,
				turn,
				tick,
			)

	def character_portal_rules_handled_dump(self):
		unpack = self.unpack
		for (
			character,
			rulebook,
			rule,
			orig,
			dest,
			branch,
			turn,
			tick,
		) in self.call_one("character_portal_rules_handled_dump"):
			yield (
				unpack(character),
				unpack(rulebook),
				unpack(orig),
				unpack(dest),
				rule,
				branch,
				turn,
				tick,
			)

	def node_rules_handled_dump(self):
		for (
			character,
			node,
			rulebook,
			rule,
			branch,
			turn,
			tick,
		) in self.call_one("node_rules_handled_dump"):
			yield (
				self.unpack(character),
				self.unpack(node),
				self.unpack(rulebook),
				rule,
				branch,
				turn,
				tick,
			)

	def portal_rules_handled_dump(self):
		unpack = self.unpack
		for (
			character,
			orig,
			dest,
			rulebook,
			rule,
			branch,
			turn,
			tick,
		) in self.call_one("portal_rules_handled_dump"):
			yield (
				unpack(character),
				unpack(orig),
				unpack(dest),
				unpack(rulebook),
				rule,
				branch,
				turn,
				tick,
			)

	def things_dump(self):
		unpack = self.unpack
		for character, thing, branch, turn, tick, location in self.call_one(
			"things_dump"
		):
			yield (
				unpack(character),
				unpack(thing),
				branch,
				turn,
				tick,
				unpack(location),
			)

	def units_dump(
		self,
	) -> Iterator[
		tuple[CharName, CharName, NodeName, Branch, Turn, Tick, bool]
	]:
		unpack = self.unpack
		for (
			character_graph,
			unit_graph,
			unit_node,
			branch,
			turn,
			tick,
			is_av,
		) in self.call_one("units_dump"):
			yield (
				unpack(character_graph),
				unpack(unit_graph),
				unpack(unit_node),
				branch,
				turn,
				tick,
				is_av,
			)

	def universal_set(
		self, key: Key, branch: Branch, turn: Turn, tick: Tick, val: Value
	) -> None:
		self._universals2set.append((key, branch, turn, tick, val))
		self._increc()

	def universal_del(self, key: Key, branch: Branch, turn: Turn, tick: Tick):
		self._universals2set.append((key, branch, turn, tick, None))
		self._increc()

	def count_all_table(self, tbl):
		return self.call_one("{}_count".format(tbl)).fetchone()[0]

	def rules_dump(self):
		for (name,) in self.call_one("rules_dump"):
			yield name

	def _set_rule_something(self, what, rule, branch, turn, tick, flist):
		flist = self.pack(flist)
		self.call_one(
			"rule_{}_insert".format(what), rule, branch, turn, tick, flist
		)
		self._increc()

	set_rule_triggers = partialmethod(_set_rule_something, "triggers")
	set_rule_prereqs = partialmethod(_set_rule_something, "prereqs")
	set_rule_actions = partialmethod(_set_rule_something, "actions")
	set_rule_neighborhood = partialmethod(_set_rule_something, "neighborhood")

	def set_rule_big(
		self,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		big: RuleBig,
	) -> None:
		self.call_one("rule_big_insert", rule, branch, turn, tick, big)
		self._increc()

	def set_rule(
		self,
		rule,
		branch,
		turn,
		tick,
		triggers=None,
		prereqs=None,
		actions=None,
		neighborhood=None,
		big=False,
	):
		try:
			self.call_one("rules_insert", rule)
			self._increc()
		except IntegrityError:
			pass
		self.set_rule_triggers(rule, branch, turn, tick, triggers or [])
		self.set_rule_prereqs(rule, branch, turn, tick, prereqs or [])
		self.set_rule_actions(rule, branch, turn, tick, actions or [])
		self.set_rule_neighborhood(rule, branch, turn, tick, neighborhood)
		self.set_rule_big(rule, branch, turn, tick, big)

	def set_rulebook(
		self,
		name: RulebookName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rules: Optional[list[RuleName]] = None,
		prio: RulebookPriority = 0.0,
	) -> None:
		name, rules = map(self.pack, (name, rules or []))
		try:
			self.call_one(
				"rulebooks_insert",
				name,
				branch,
				turn,
				tick,
				rules,
				float(prio),
			)
			self._increc()
		except IntegrityError:
			self.call_one("rulebooks_update", rules, name, branch, turn, tick)
			# not incrementing because this didn't create a new record

	def set_rulebook_on_character(
		self,
		rbtyp: RulebookTypeStr,
		char: CharName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rb: RulebookName,
	) -> None:
		char, rb = map(self.pack, (char, rb))
		self.call_one(rbtyp + "_insert", char, branch, turn, tick, rb)
		self._increc()

	set_character_rulebook = partialmethod(
		set_rulebook_on_character, "character_rulebook"
	)
	set_unit_rulebook = partialmethod(
		set_rulebook_on_character, "unit_rulebook"
	)
	set_character_thing_rulebook = partialmethod(
		set_rulebook_on_character, "character_thing_rulebook"
	)
	set_character_place_rulebook = partialmethod(
		set_rulebook_on_character, "character_place_rulebook"
	)
	set_character_portal_rulebook = partialmethod(
		set_rulebook_on_character, "character_portal_rulebook"
	)

	def rulebooks(self):
		for book in self.call_one("rulebooks"):
			yield self.unpack(book)

	def set_node_rulebook(
		self,
		character: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rulebook: RulebookName,
	) -> None:
		self._node_rulebook_to_set.append(
			(character, node, branch, turn, tick, rulebook)
		)
		self._increc()

	def set_portal_rulebook(
		self,
		character: CharName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rulebook: RulebookName,
	) -> None:
		self._portal_rulebook_to_set.append(
			(character, orig, dest, branch, turn, tick, rulebook)
		)
		self._increc()

	def handled_character_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> None:
		self._char_rules_handled.append(
			(character, rulebook, rule, branch, turn, tick)
		)

	def handled_unit_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		graph: CharName,
		unit: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> None:
		self._unit_rules_handled.append(
			(character, graph, unit, rulebook, rule, branch, turn, tick)
		)

	def handled_character_thing_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		thing: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	):
		self._char_thing_rules_handled.append(
			(character, rulebook, rule, thing, branch, turn, tick)
		)

	def handled_character_place_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		place: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> None:
		self._char_place_rules_handled.append(
			(character, place, rulebook, rule, branch, turn, tick)
		)

	def handled_character_portal_rule(
		self,
		character: CharName,
		rulebook: RulebookName,
		rule: RuleName,
		orig: NodeName,
		dest: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> None:
		self._char_portal_rules_handled.append(
			(character, orig, dest, rulebook, rule, branch, turn, tick)
		)

	def handled_node_rule(
		self,
		character: CharName,
		node: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> None:
		self._node_rules_handled.append(
			(character, node, rulebook, rule, branch, turn, tick)
		)

	def handled_portal_rule(
		self,
		character: CharName,
		orig: NodeName,
		dest: NodeName,
		rulebook: RulebookName,
		rule: RuleName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
	) -> None:
		self._portal_rules_handled.append(
			(character, orig, dest, rulebook, rule, branch, turn, tick)
		)

	def set_thing_loc(
		self,
		character: CharName,
		thing: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		loc: NodeName,
	) -> None:
		self._location.append((character, thing, branch, turn, tick, loc))
		self._increc()

	def unit_set(
		self,
		character: CharName,
		graph: CharName,
		node: NodeName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		is_unit: bool,
	) -> None:
		self._unitness.append(
			(character, graph, node, branch, turn, tick, is_unit)
		)
		self._increc()

	def rulebook_set(
		self,
		rulebook: RulebookName,
		branch: Branch,
		turn: Turn,
		tick: Tick,
		rules: list[RuleName],
	) -> None:
		# what if the rulebook has other values set afterward? wipe them out, right?
		# should that happen in the query engine or elsewhere?
		rulebook, rules = map(self.pack, (rulebook, rules))
		try:
			self.call_one(
				"rulebooks_insert", rulebook, branch, turn, tick, rules
			)
			self._increc()
		except IntegrityError:
			try:
				self.call_one(
					"rulebooks_update", rules, rulebook, branch, turn, tick
				)
			except IntegrityError:
				self.commit()
				self.call_one(
					"rulebooks_update", rules, rulebook, branch, turn, tick
				)

	def turns_completed_dump(self) -> Iterator[tuple[Branch, Turn]]:
		return self.call_one("turns_completed_dump")

	def complete_turn(
		self, branch: Branch, turn: Turn, discard_rules: bool = False
	) -> None:
		try:
			self.call_one("turns_completed_insert", branch, turn)
		except IntegrityError:
			try:
				self.call_one("turns_completed_update", turn, branch)
			except IntegrityError:
				self.commit()
				self.call_one("turns_completed_update", turn, branch)
		self._increc()
		if discard_rules:
			self._char_rules_handled.clear()
			self._unit_rules_handled.clear()
			self._char_thing_rules_handled.clear()
			self._char_place_rules_handled.clear()
			self._char_portal_rules_handled.clear()
			self._node_rules_handled.clear()
			self._portal_rules_handled.clear()
