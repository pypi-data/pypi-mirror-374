from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from portabellas import Column


class ColumnPlotter:
    def __init__(self, column: Column) -> None:
        self._column = column
