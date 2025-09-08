import pytest
import numpy as np
import os

# from yasiu_image.io import *
import yasiu_image.io
import types

from conftest import TEST_GIF_PATHS, TEST_AVIF_PATHS


@pytest.mark.parametrize('gifPath', TEST_GIF_PATHS)
def test1_Call_1(gifPath, request):
    result = yasiu_image.io.read_gif_frames(gifPath)

    assert isinstance(result, (types.GeneratorType,))
    with pytest.raises(TypeError):
        "No lenght for this object. Confirm"
        len(result)


@pytest.mark.parametrize('gifPath', TEST_GIF_PATHS)
def test1_Call_2(gifPath, request):
    result = yasiu_image.io.read_gif_frames_ToList(gifPath)
    assert len(result) > 0
    assert len(result) > 10


@pytest.mark.parametrize('gifPath', TEST_GIF_PATHS)
def test1_Call_3(gifPath, request):
    result = yasiu_image.io.read_gif_frames_ToNumpyArray(gifPath)
    assert len(result) > 0
    assert len(result) > 10
    assert isinstance(result, (np.ndarray,))
    assert len(result.shape) >= 2


@pytest.mark.parametrize('gifPath', TEST_AVIF_PATHS)
def test1_Call_4(gifPath, request):
    result = yasiu_image.io.read_webp_frames(gifPath)
    assert isinstance(result, (types.GeneratorType,))
    with pytest.raises(TypeError):
        "No lenght for this object. Confirm"
        len(result)


@pytest.mark.parametrize('gifPath', TEST_GIF_PATHS)
def test2_Generator_1(gifPath, request):
    yasiu_image.io.read_gif_frames(gifPath)
    counter = 0
    generator = yasiu_image.io.read_gif_frames(gifPath)
    firstFrame = next(generator)
    for frame in generator:
        pass
        # print(frame.shape)
        assert firstFrame.shape[:2] == frame.shape[:2]
        counter += 1

    assert counter > 0, "Values is empty?"
    assert counter > 10, "Too Few frames"
