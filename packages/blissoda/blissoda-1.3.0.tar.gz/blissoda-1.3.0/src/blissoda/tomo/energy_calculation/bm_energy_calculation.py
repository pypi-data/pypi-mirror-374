from __future__ import annotations

import json
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any
from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional
from typing import Tuple

from ewoksjob.client import submit

from ...flint import WithFlintAccess
from ...import_utils import unavailable_function
from ...persistent.parameters import ParameterInfo
from ...processor import BaseProcessor

try:
    from bliss.shell.getval import getval_yes_no
except ImportError as ex:
    getval_yes_no = unavailable_function(ex)

from .grid_plotter import GridPlot

try:
    from bliss import current_session
except ImportError:
    current_session = None

MATERIAL_TABLE = {
    "al": ("Al", 2.700),
    "c": ("C", 3.508),
    "be": ("Be", 1.848),
    "si": ("Si", 2.3296),
    "cu": ("Cu", 8.96),
    "ni": ("Ni", 8.908),
    "mo": ("Mo", 10.22),
    "ti": ("Ti", 4.506),
    "zr": ("Zr", 6.52),
    "cr": ("Cr", 7.19),
    "fe": ("Fe", 7.874),
    "w": ("W", 19.3),
    "air": ("Air", 0.001225),
}
_POS = re.compile(r"^\s*([A-Za-z]+)\s*([0-9]+(?:\.[0-9]+)?)\s*$")
_EMPTY = re.compile(r"^\s*(empty|out|open|none|0)\s*$", re.IGNORECASE)
_ORDER_KEY_RE = re.compile(r"^(fix|att)\d+$")


def parse_position_string(position: Any) -> Tuple[Optional[str], float]:
    s = str(position)
    if _EMPTY.match(s):
        return None, 0.0
    m = _POS.match(s)
    if not m:
        raise ValueError(f"Unrecognized attenuator position format: {position!r}")
    code = m.group(1).lower()
    mm = m.group(2)
    thickness_mm = float(mm) if "." in mm else float(int(mm)) / 1000.0
    return code, thickness_mm


class BMEnergyPlotter(WithFlintAccess):
    """Reusable base for plotters that draw in Flint."""

    def __init__(self, *, unique_name: Optional[str] = None) -> None:
        super().__init__()
        self.unique_name = unique_name or self.__class__.__name__
        self._grid: Optional[GridPlot] = None

    @property
    def grid(self) -> GridPlot:
        if self._grid is None:
            self._grid = GridPlot(unique_name=self.unique_name)
        return self._grid

    def clear(self) -> None:
        if self._grid is not None:
            self._grid.clear()

    def _plot_in_flint(self, result: Dict[str, Any]) -> None:
        energy_eV = result.get("energy_eV")
        sp_src = result.get("spectral_power")
        sp_att = result.get("attenuated_spectral_power")
        flux_src = result.get("flux")
        flux_att = result.get("attenuated_flux")
        transmission = result.get("transmission")
        cumulated_power = result.get("cumulated_power")

        x_keV = energy_eV / 1e3
        g = self.grid
        g.set_layout(2, 2)

        # 1) Spectral power
        series_sp = [{"y": sp_src, "label": "Source", "color": "red"}]
        series_sp.append({"y": sp_att, "label": "Attenuated", "color": "green"})
        g.set_cell(
            0,
            0,
            x=x_keV,
            series=series_sp,
            title="Spectral Power (source (red) vs attenuated (green))",
            xlabel="Energy [keV]",
            ylabel="Spectral Power [W/eV]",
        )

        # 2) Flux
        series_flux = []
        series_flux.append(
            {"y": flux_src, "label": "Flux (source)", "color": "darkRed"}
        )
        series_flux.append(
            {"y": flux_att, "label": "Flux (attenuated)", "color": "darkGreen"}
        )
        g.set_cell(
            0,
            1,
            x=x_keV,
            series=series_flux,
            title="Flux (source (red) vs attenuated (green))",
            xlabel="Energy [keV]",
            ylabel="Flux [Phot/s/0.1%bw]",
        )

        # 3) Transmission
        g.set_cell(
            1,
            0,
            x=x_keV,
            series=[{"y": transmission, "label": "T", "color": "blue"}],
            title="Transmission vs Energy",
            xlabel="Energy [keV]",
            ylabel="Transmission",
        )

        # 4) Cumulated power
        g.set_cell(
            1,
            1,
            x=x_keV,
            series=[{"y": cumulated_power, "label": "Cumulated", "color": "black"}],
            title="Cumulated Power vs Energy",
            xlabel="Energy [keV]",
            ylabel="Cumulated Power [W]",
        )

    def plot(self, result: Dict[str, Any]) -> None:
        self._plot_in_flint(result)


class BMEnergyCalculation(
    BaseProcessor,
    parameters=[
        ParameterInfo("attenuators_names", category="attenuators"),
        ParameterInfo("fixed_elements", category="attenuators"),
        ParameterInfo("order", category="attenuators"),
        ParameterInfo("queue", category="workflows"),
        ParameterInfo("prompt_set_energy", category="handle_result"),
        ParameterInfo("plot", category="plot"),
        ParameterInfo("beam_energy_gev", category="source_configuration"),
        ParameterInfo("bfield_t", category="source_configuration"),
        ParameterInfo("current_a", category="source_configuration"),
        ParameterInfo("hor_div_mrad", category="source_configuration"),
        ParameterInfo("phot_energy_min", category="source_configuration"),
        ParameterInfo("phot_energy_max", category="source_configuration"),
        ParameterInfo("npoints", category="source_configuration"),
        ParameterInfo("log_choice", category="source_configuration"),
    ],
):
    """Submit the **BM** workflow and (optionally) plot in Flint via a plotter."""

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        defaults: Optional[Dict[str, Any]] = None,
        **deprecated_defaults: Dict[str, Any],
    ):
        defaults = self._merge_defaults(deprecated_defaults, defaults)
        defaults.update(
            {
                "attenuators_names": "att1,att2,att3,att4,att5",
                "queue": "online",
                "order": None,
                "beam_energy_gev": 6.0,
                "bfield_t": 0.8,
                "current_a": 0.2,
                "hor_div_mrad": 1.0,
                "phot_energy_min": 100.0,
                "phot_energy_max": 200000.0,
                "npoints": 2000,
                "log_choice": 1,
            }
        )
        BaseProcessor.__init__(self, config=config, defaults=defaults)
        self._plotter = BMEnergyPlotter(unique_name="Energy Calculation")

    def _info_categories(self) -> dict:
        cats = super()._info_categories()
        cats.pop("status", None)
        cats.pop("enabled", None)
        return cats

    def submit(self, save_workflow_to: Optional[str] = None):
        wf = self.get_workflow()
        submit_kwargs = self.get_submit_arguments()
        if save_workflow_to:
            p = Path(save_workflow_to)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(wf, indent=2))
            submit_kwargs["convert_destination"] = save_workflow_to
        future = submit(args=(wf,), kwargs=submit_kwargs, queue=self.queue)
        result = future.get()

        if self.plot and self._plotter is not None:
            self._plotter._plot_in_flint(result)

        mean_eV = self._extract_mean_energy_eV(result)
        if self.prompt_set_energy:
            if mean_eV is None:
                print("Calculated energy is: N/A.")
            else:
                mean_keV = mean_eV / 1e3
                if getval_yes_no(
                    f"Calculated energy is: {mean_keV:.3f} keV. Run ENERGY({mean_keV:.3f})? ",
                    default="no",
                ):
                    self._set_energy_eV(mean_eV)
        else:
            if mean_eV is not None:
                print(f"Calculated energy is: {mean_eV / 1e3:.3f} keV.")
        return

    def get_submit_arguments(self) -> dict:
        return {"inputs": self._build_submit_inputs(), "outputs": [{"all": True}]}

    def get_workflow(self) -> dict:
        return {
            "graph": {"id": "bm_attenuation_bm", "schema_version": "1.1"},
            "nodes": [
                {
                    "id": "compute",
                    "label": "compute_bm_spectrum",
                    "task_type": "class",
                    "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                },
                {
                    "id": "attenuate",
                    "label": "apply_attenuators",
                    "task_type": "class",
                    "task_identifier": "ewokstomo.tasks.energycalculation.ApplyAttenuators",
                },
                {
                    "id": "stats",
                    "label": "spectrum_stats",
                    "task_type": "class",
                    "task_identifier": "ewokstomo.tasks.energycalculation.SpectrumStats",
                },
            ],
            "links": [
                {
                    "source": "compute",
                    "target": "attenuate",
                    "data_mapping": [
                        {"source_output": "energy_eV", "target_input": "energy_eV"},
                        {
                            "source_output": "spectral_power",
                            "target_input": "spectral_power",
                        },
                        {"source_output": "flux", "target_input": "flux"},
                    ],
                },
                {
                    "source": "attenuate",
                    "target": "stats",
                    "data_mapping": [
                        {"source_output": "energy_eV", "target_input": "energy_eV"},
                        {
                            "source_output": "attenuated_flux",
                            "target_input": "attenuated_flux",
                        },
                    ],
                },
            ],
        }

    def _resolve_devices(self) -> List[Any]:
        if current_session is None:
            raise RuntimeError("BLISS current_session is not available.")
        names = [n.strip() for n in str(self.attenuators_names).split(",") if n.strip()]
        sg = getattr(current_session, "setup_globals", current_session)
        return [getattr(sg, name) for name in names]

    def _build_attenuators_from_devices(
        self, devices: Iterable[Any]
    ) -> Tuple[Dict[str, Dict[str, float]], List[str]]:
        attenuators, order_keys = OrderedDict(), []
        for idx, dev in enumerate(devices, 1):
            pos = dev.position
            code, t_mm = parse_position_string(pos)
            if (not code) or t_mm <= 0.0:
                element, density, t_mm = "Air", 0.001225, 0.0
            else:
                element, density = MATERIAL_TABLE.get(code, (code.capitalize(), 1.0))
            key = f"att{idx}"
            order_keys.append(key)
            attenuators[key] = {
                "material": element,
                "thickness_mm": float(t_mm),
                "density_g_cm3": float(density),
            }
        return attenuators, order_keys

    def _build_submit_inputs(self) -> List[dict]:
        devices = self._resolve_devices()
        att_layers, _ = self._build_attenuators_from_devices(devices)
        fixed_layers = self._build_fixed_elements()

        merged = OrderedDict()
        merged.update(fixed_layers)
        merged.update(att_layers)

        order_value = list(merged.keys()) if self.order is None else self.order

        inputs: List[dict] = [
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "TYPE_CALC",
                "value": 0,
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "VER_DIV",
                "value": 0,
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "MACHINE_NAME",
                "value": "ESRF bending magnet",
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "RB_CHOICE",
                "value": 0,
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "MACHINE_R_M",
                "value": 25.0,
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "BFIELD_T",
                "value": float(self.bfield_t),
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "BEAM_ENERGY_GEV",
                "value": float(self.beam_energy_gev),
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "CURRENT_A",
                "value": float(self.current_a),
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "HOR_DIV_MRAD",
                "value": float(self.hor_div_mrad),
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "PHOT_ENERGY_MIN",
                "value": float(self.phot_energy_min),
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "PHOT_ENERGY_MAX",
                "value": float(self.phot_energy_max),
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "NPOINTS",
                "value": int(self.npoints),
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "LOG_CHOICE",
                "value": int(self.log_choice),
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "PSI_MRAD_PLOT",
                "value": 1.0,
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "PSI_MIN",
                "value": -1.0,
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "PSI_MAX",
                "value": 1.0,
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "PSI_NPOINTS",
                "value": 500,
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ComputeBMSpectrum",
                "name": "FILE_DUMP",
                "value": False,
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ApplyAttenuators",
                "name": "attenuators",
                "value": merged,
            },
            {
                "task_identifier": "ewokstomo.tasks.energycalculation.ApplyAttenuators",
                "name": "order",
                "value": order_value,
            },
        ]
        return inputs

    @staticmethod
    def _coerce_layer(entry: Dict[str, Any]) -> Dict[str, float]:
        """
        Validate & complete one fixed layer.
        Required: material, thickness_mm.
        Optional: density_g_cm3 (fallback to MATERIAL_TABLE or 1.0).
        """
        material = str(entry.get("material", "")).strip()
        if not material:
            raise ValueError("fixed_elements entry missing 'material'")
        thickness_mm = float(entry.get("thickness_mm", 0.0))
        if "density_g_cm3" in entry:
            density = float(entry["density_g_cm3"])
        else:
            mkey = material.lower()
            density = MATERIAL_TABLE.get(mkey, (material, 1.0))[1]

        # Treat empty/air with <=0 mm as neutral layer
        if material.lower() in ("empty", "none", "air") and thickness_mm <= 0.0:
            material = "Air"
            thickness_mm = 0.0
            density = MATERIAL_TABLE["air"][1]

        return {
            "material": material,
            "thickness_mm": thickness_mm,
            "density_g_cm3": density,
        }

    def _build_fixed_elements(self) -> OrderedDict[str, Dict[str, float]]:
        fixed_src = dict(self.fixed_elements or {})
        fixed: "OrderedDict[str, Dict[str, float]]" = OrderedDict()
        gen_idx = 1
        for user_key, entry in fixed_src.items():
            layer = self._coerce_layer(entry)
            key = (
                user_key
                if isinstance(user_key, str) and _ORDER_KEY_RE.match(user_key)
                else f"fix{gen_idx}"
            )
            gen_idx += 1 if not (_ORDER_KEY_RE.match(str(user_key) or "")) else 0
            fixed[key] = layer
        return fixed

    @staticmethod
    def _extract_mean_energy_eV(result: dict) -> Optional[float]:
        v = (result.get("stats") or {}).get(
            "mean_energy_eV", result.get("mean_energy_eV")
        )
        return float(v) if v is not None else None

    def _set_energy_eV(self, energy_eV: float) -> None:
        if current_session is None:
            return
        sg = getattr(current_session, "setup_globals", current_session)
        ENERGY = getattr(sg, "ENERGY", None)
        if callable(ENERGY):
            ENERGY(float(energy_eV) / 1e3)
