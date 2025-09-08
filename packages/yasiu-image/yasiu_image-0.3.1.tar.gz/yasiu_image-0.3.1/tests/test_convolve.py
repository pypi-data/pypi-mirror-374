
from yasiu_image.convolve import convolve_pic, gauss_kernel, mean_filter, median_filter, erode_dilate

from conftest import testImage_CatValid
import pytest

# import cv2
# import os


@pytest.mark.parametrize('fix_name', testImage_CatValid)
@pytest.mark.parametrize('margin', [0, 2, 5])
@pytest.mark.parametrize('kernel', [gauss_kernel(1), gauss_kernel(3)])
@pytest.mark.parametrize('channel', [[0], [0, 1], [0, 1, 2], [2, 1]])
def test1_call_1(fix_name, margin, kernel, channel, request):
    cat_pic = request.getfixturevalue(fix_name)
    convolve_pic(cat_pic, margin, kernel, channel)


@pytest.mark.parametrize('fix_name', testImage_CatValid)
def test1_call_2(fix_name, request):
    cat_pic = request.getfixturevalue(fix_name)
    mean_filter(cat_pic)


@pytest.mark.parametrize('fix_name', testImage_CatValid)
def test1_call_3(fix_name, request):
    cat_pic = request.getfixturevalue(fix_name)
    median_filter(cat_pic)


@pytest.mark.parametrize('fix_name', testImage_CatValid)
def test1_call_4(fix_name, request):
    cat_pic = request.getfixturevalue(fix_name)
    erode_dilate(cat_pic)
