from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from portabellas import Table


class TableWriter:
    def __init__(self, table: Table) -> None:
        self._table = table
