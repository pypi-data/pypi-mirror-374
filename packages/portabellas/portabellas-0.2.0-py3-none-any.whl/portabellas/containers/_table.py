from __future__ import annotations

from portabellas.io import TableReader, TableWriter
from portabellas.plotting import TablePlotter


# TODO: add examples  # noqa: FIX002
class Table:
    """A two-dimensional collection of data. It can either be seen as a list of rows or as a list of columns."""

    read: TableReader = TableReader()
    """Create a new table by reading from various sources."""

    @property
    def plot(self) -> TablePlotter:
        """Create interactive plots of this table."""
        return TablePlotter(self)

    @property
    def write(self) -> TableWriter:
        """Write this table to various targets."""
        return TableWriter(self)
