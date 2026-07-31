from brooks_cases.wfc3 import DATAREJECT_BIT, RampCube, interval_good_mask

from test_wfc3 import make_cube


def test_datareject_is_retained_but_other_dq_bits_are_rejected() -> None:
    cube: RampCube = make_cube()

    cube.dq[1, 60, 60] = DATAREJECT_BIT
    assert interval_good_mask(cube, 0)[60, 60]

    cube.dq[1, 60, 60] = 1024  # SPIKE: cosmic-ray spike during ramp fitting
    assert not interval_good_mask(cube, 0)[60, 60]

    cube.dq[1, 60, 60] = 4096  # CR hit / image-combination rejection
    assert not interval_good_mask(cube, 0)[60, 60]

    cube.dq[1, 60, 60] = 16  # HOTPIX
    assert not interval_good_mask(cube, 0)[60, 60]
