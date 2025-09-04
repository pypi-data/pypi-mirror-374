from __future__ import annotations

from typing import Iterable
from typing import Mapping
from typing import Optional
from typing import Sequence

import numpy as np
from silx.gui import qt
from silx.gui.plot import Plot1D


class GridPlotWidget(qt.QWidget):
    """Grid of interactive silx Plot1D widgets rendered inside Flint."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._rows = 0
        self._cols = 0
        self._plots: list[list[Plot1D]] = []

        self._grid = qt.QGridLayout()
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(4)

        wrapper = qt.QWidget(self)
        wrapper.setLayout(self._grid)

        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(wrapper)

        # default 2x2
        self.set_layout(2, 2)

    def clear(self):
        """Clear all plots in the grid."""
        for row in self._plots:
            for plot in row:
                self._clear_plot(plot)

    def set_layout(self, rows: int, cols: int):
        """Create/resize the grid of Plot1D widgets."""
        rows, cols = max(1, int(rows)), max(1, int(cols))
        if (rows, cols) == (self._rows, self._cols) and self._plots:
            return

        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

        self._plots = []
        for r in range(rows):
            row_plots: list[Plot1D] = []
            for c in range(cols):
                p = Plot1D(parent=self)
                p.setDataMargins(0.06, 0.06, 0.06, 0.06)
                p.setGraphGrid(which="both")
                p.setActiveCurveStyle(linewidth=2, symbol=None)
                self._grid.addWidget(p, r, c)
                row_plots.append(p)
            self._plots.append(row_plots)

        self._rows, self._cols = rows, cols

    def set_cell(
        self,
        row: int,
        col: int,
        *,
        x,
        series: Sequence[Mapping],
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
    ):
        """Update a single cell (row, col) with one or more curves."""
        plot = self._plot_at(row, col)
        self._clear_plot(plot)

        # Labels / title
        if title is not None:
            plot.setGraphTitle(str(title))
        if xlabel is not None:
            plot.setGraphXLabel(str(xlabel))
        if ylabel is not None:
            plot.setGraphYLabel(str(ylabel))

        x_arr = None if x is None else np.asarray(x)
        plotted = False

        if x_arr is not None and series:
            for s in series:
                y = s.get("y", None)
                if y is None:
                    continue
                y_arr = np.asarray(y)
                n = min(x_arr.size, y_arr.size)
                if n == 0:
                    continue

                plot.addCurve(
                    x_arr[:n],
                    y_arr[:n],
                    legend=s.get("label"),
                    color=s.get("color"),
                    linewidth=s.get("linewidth", 1.5),
                    resetzoom=False,
                )
                plotted = True

        if plotted:
            plot.resetZoom()

    def set_cells(self, batch: Iterable[Mapping]):
        """Batch update: iterable of dicts accepted by set_cell."""
        for item in batch:
            item = dict(item)
            self.set_cell(**item)

    def _plot_at(self, row: int, col: int) -> Plot1D:
        r = int(row)
        c = int(col)
        if r < 0 or c < 0 or r >= self._rows or c >= self._cols:
            raise IndexError(
                f"Cell ({row}, {col}) out of range {self._rows}x{self._cols}"
            )
        return self._plots[r][c]

    @staticmethod
    def _clear_plot(plot: Plot1D) -> None:
        # Remove curves without resetting zoom at each removal (avoid flicker)
        for curve in list(plot.getAllCurves()):
            plot.removeCurve(curve.getLegend())
        plot.setGraphTitle("")
        plot.setGraphXLabel("")
        plot.setGraphYLabel("")
