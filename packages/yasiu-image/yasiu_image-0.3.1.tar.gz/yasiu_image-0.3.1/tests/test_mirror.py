import conftest

import pytest
from yasiu_image.filters import mirrorAxis

import numpy as np


tests_params = [
    (val, ax, flag)
    for val in [*np.linspace(0, 1, 10), *range(290, 310, 2), *range(-16, 20, 2)]
    for ax in [0, 1]
    for flag in [False, True]
]



@pytest.mark.parametrize('val,ax,flag', tests_params)
@pytest.mark.parametrize('image', conftest.testImage_SimpleValid)
def test_1(image, val, ax, flag, request):
    image = request.getfixturevalue(image)

    ret = mirrorAxis(image, pos=val, verticalFlip=ax, flip=flag)
    # assert ret.shape == image.shape, "Shape must match"
