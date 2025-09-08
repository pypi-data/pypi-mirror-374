from yasiu_image.features import image_to_features, features_to_image

from conftest import testImage_CatValid
import pytest

# import cv2
# import os


@pytest.mark.parametrize('fix_name', testImage_CatValid)
def test1_call(fix_name, request):
    cat_pic = request.getfixturevalue(fix_name)
    image_to_features(cat_pic)


@pytest.mark.parametrize('fix_name', testImage_CatValid)
def test1_call_b(fix_name, request):
    cat_pic = request.getfixturevalue(fix_name)
    ft = image_to_features(cat_pic)
    ret = features_to_image(ft, cat_pic.shape)


@pytest.mark.parametrize('fix_name', testImage_CatValid)
def test2_equal(fix_name, request):
    cat_pic = request.getfixturevalue(fix_name)
    ft = image_to_features(cat_pic)
    ret = features_to_image(ft, cat_pic.shape)

    assert (cat_pic == ret).all(), "Image does not match!"
    assert (cat_pic.shape == ret.shape), "Shape does not match!"


@pytest.mark.parametrize('fix_name', testImage_CatValid)
def test3_pos_values(fix_name, request):
    cat_pic = request.getfixturevalue(fix_name)
    ft = image_to_features(cat_pic, include_pos=True)

    assert ft.shape[1] >= 3, "Features shape is less than 3 (x,y, color)"

    assert ft[0, -2] == 0, "First feat x should be 0"
    assert ft[0, -1] == 0, "First feat y should be 0"

    assert ft[-1, -2] == 1, "Last feat, x shoudl be 1"
    assert ft[-1, -1] == 1, "Last feat, y should be 1"


