import numpy as np

from brooks_cases.wfc3 import DATAREJECT_BIT, RampCube, interval_good_mask


def make_cube() -> RampCube:
    time_s = np.array([0.0, 1.0, 3.0])
    return RampCube(
        rate_e_s=np.zeros((3, 8, 8), dtype=float),
        error_e_s=np.ones((3, 8, 8), dtype=float),
        dq=np.zeros((3, 8, 8), dtype=int),
        time_s=time_s,
        sampnum=np.arange(time_s.size),
        filename="dq_policy_test.fits",
    )


def test_datareject_is_retained_but_other_dq_bits_are_rejected() -> None:
    cube = make_cube()

    cube.dq[1, 4, 4] = DATAREJECT_BIT
    assert interval_good_mask(cube, 0)[4, 4]

    cube.dq[1, 4, 4] = 1024  # SPIKE: cosmic-ray spike during ramp fitting
    assert not interval_good_mask(cube, 0)[4, 4]

    cube.dq[1, 4, 4] = 4096  # CR hit / image-combination rejection
    assert not interval_good_mask(cube, 0)[4, 4]

    cube.dq[1, 4, 4] = 16  # HOTPIX
    assert not interval_good_mask(cube, 0)[4, 4]
