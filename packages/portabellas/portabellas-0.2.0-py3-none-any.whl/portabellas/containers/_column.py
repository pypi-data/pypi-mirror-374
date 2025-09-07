from __future__ import annotations

from portabellas.plotting import ColumnPlotter


# TODO: add examples  # noqa: FIX002
class Column:
    @property
    def plot(self) -> ColumnPlotter:
        """Create interactive plots of this column."""
        return ColumnPlotter(self)
