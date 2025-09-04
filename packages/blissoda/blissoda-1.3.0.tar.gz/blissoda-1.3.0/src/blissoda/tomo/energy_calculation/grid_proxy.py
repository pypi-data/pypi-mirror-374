from __future__ import annotations

from typing import Iterable
from typing import Mapping
from typing import Optional

import numpy as np

from ...flint import BasePlot


def _arr(x):
    if x is None:
        return None
    try:
        return np.asarray(x)
    except Exception:
        return x


class GridPlotProxy(BasePlot):
    """Proxy visible to BLISS; forwards to the real QWidget inside Flint."""

    WIDGET = "blissoda.tomo.energy_calculation.grid_widget.GridPlotWidget"

    def clear(self) -> None:
        self.submit("clear")

    def set_layout(self, rows: int, cols: int) -> None:
        self.submit("set_layout", int(rows), int(cols))

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
        x = _arr(x)
        ser = []
        for s in series or []:
            sd = dict(s)
            if "y" in sd:
                sd["y"] = _arr(sd["y"])
            ser.append(sd)
        self.submit(
            "set_cell",
            int(row),
            int(col),
            x=x,
            series=ser,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
        )

    def set_cells(self, batch: Iterable[Mapping]) -> None:
        norm = []
        for it in batch:
            d = dict(it)
            d["row"] = int(d.get("row", 0))
            d["col"] = int(d.get("col", 0))
            d["x"] = _arr(d.get("x"))
            ser = []
            for s in d.get("series") or []:
                sd = dict(s)
                if "y" in sd:
                    sd["y"] = _arr(sd["y"])
                ser.append(sd)
            d["series"] = ser
            norm.append(d)
        self.submit("set_cells", norm)
