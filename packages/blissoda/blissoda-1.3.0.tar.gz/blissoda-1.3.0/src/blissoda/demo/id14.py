from typing import List

from ..id14.converter import Id14Hdf5ToSpecConverter
from ..import_utils import unavailable_type

try:
    from bliss.scanning.scan import Scan as BlissScanType
except ImportError as ex:
    BlissScanType = unavailable_type(ex)


class DemoId14Hdf5ToSpecConverter(Id14Hdf5ToSpecConverter):
    def _get_inputs_for_mca(self, scan: BlissScanType) -> List[dict]:
        inputs = super()._get_inputs_for_mca(scan)
        task_identifier = "Hdf5ToSpec"
        inputs.append(
            {
                "task_identifier": task_identifier,
                "name": "mca_counter",
                "value": "mca1_det0",
            }
        )
        return inputs

    def _scan_requires_mca_conversion(self, scan: BlissScanType) -> bool:
        return True

    def _scan_requires_asc_conversion(self, scan: BlissScanType) -> bool:
        return True

    def validate_result(self, scan_number: int) -> None:
        result = self._future_for_counters.result(timeout=10)
        output_filename = result["output_filename"]
        self._validate_file(output_filename, scan_number)

        result = self._future_for_mca.result(timeout=10)
        output_filenames = result["output_filenames"]
        if not output_filenames:
            raise RuntimeError(
                "No filenames returned from ID14 MCA conversion workflow"
            )
        for output_filename in output_filenames:
            self._validate_file(output_filename, scan_number)

    def _validate_file(self, output_filename: str, scan_number: int) -> None:
        find_string = f"#S {scan_number}"
        with open(output_filename, "r") as f:
            for line in f:
                if find_string in line:
                    break
            else:
                raise RuntimeError(f"{find_string!r} not found in {output_filename!r}")
        print("SPEC file is ok:", output_filename)


id14_converter = DemoId14Hdf5ToSpecConverter()
