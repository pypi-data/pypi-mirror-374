from blissoda.bliss_globals import setup_globals
from blissoda.demo.id14 import id14_converter


def id14_demo(expo=0.2, npoints=10):
    id14_converter.enable()
    try:
        for _ in range(2):
            scan = setup_globals.loopscan(
                npoints, expo, setup_globals.diode1, setup_globals.mca1
            )
            id14_converter.validate_result(scan.scan_info["scan_nb"])
    finally:
        id14_converter.disable()
