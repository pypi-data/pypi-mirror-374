
from yasiu_image.filters import *

from conftest import testImage_CatValid
import pytest


@pytest.mark.parametrize("fix_name", testImage_CatValid)
def test_Call_1(fix_name, request):
    cat_pic = request.getfixturevalue(fix_name)
    color_blend(cat_pic, (150, 200, 50), 0.5)


@pytest.mark.parametrize("fix_name", testImage_CatValid)
@pytest.mark.parametrize("t", [0, 0.1, 0.15])
@pytest.mark.parametrize("b", [0, 0.1, 0.15])
@pytest.mark.parametrize("l", [0, 0.1, 0.15])
@pytest.mark.parametrize("r", [0, 0.1, 0.15])
def test_Call_2(fix_name, t, b, l, r, request):
    cat_pic = request.getfixturevalue(fix_name)
    crop_image(cat_pic, t, b, l, r)


# @pytest.mark.parametrize("fix_name", testImage_CatValid)
# def test_Call_3(fix_name, request):
#     cat_pic = request.getfixturevalue(fix_name)
#     cutoff_alpha(cat_pic, 30)
