from __future__ import annotations

from typing import Iterable
from typing import Mapping
from typing import Optional

import numpy as np

from ...flint import WithFlintAccess
from ...flint import capture_errors
from .grid_proxy import GridPlotProxy


class GridPlot(WithFlintAccess):
    """Convenience wrapper to keep a named grid plot alive and easy to update."""

    def __init__(self, unique_name: str = "Grid") -> None:
        super().__init__()
        self._unique_name = unique_name

    def _grid_obj(self):
        return self._get_plot(self._unique_name, GridPlotProxy)

    @capture_errors
    def clear(self) -> None:
        self._grid_obj().clear()

    @capture_errors
    def set_layout(self, rows: int, cols: int) -> None:
        self._grid_obj().set_layout(int(rows), int(cols))

    @capture_errors
    def set_cell(
        self,
        row: int,
        col: int,
        *,
        x,
        series,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
    ) -> None:
        x_arr = None if x is None else np.asarray(x)
        ser = []
        for s in series or []:
            y = s.get("y", None)
            ser.append(
                {
                    "y": None if y is None else np.asarray(y),
                    "label": s.get("label"),
                    "color": s.get("color"),
                    "linewidth": s.get("linewidth"),
                }
            )
        self._grid_obj().set_cell(
            int(row),
            int(col),
            x=x_arr,
            series=ser,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
        )

    @capture_errors
    def set_cells(self, batch: Iterable[Mapping]) -> None:
        norm = []
        for item in batch:
            d = dict(item)
            if d.get("x") is not None:
                d["x"] = np.asarray(d["x"])
            ser = []
            for s in d.get("series") or []:
                s = dict(s)
                if "y" in s and s["y"] is not None:
                    s["y"] = np.asarray(s["y"])
                ser.append(s)
            d["series"] = ser
            norm.append(d)
        self._grid_obj().set_cells(norm)
