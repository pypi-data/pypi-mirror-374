import numpy as _np
import cv2 as _cv


def mirrorAxis(picture, verticalFlip: bool = True, pos=0.5, flip=False):
    """
    Mirror image along axis in given position. New image will differ in shape.

    :param picture: array, 2d, 3d

    :param verticalFlip: bool
            True - Image will be mirrored up-down
            False - Image will be mirrored left-right

    :param pos: Float or Int
            Float - <0, 1> Axis position = number * dimention.
            Int - <0, MaxDimension> Image position

    :param flip: bool, flip other direction

    :return:

    """

    if len(picture.shape) == 3:
        h, w, c = picture.shape
    else:
        h, w = picture.shape

    if isinstance(pos, int):
        if verticalFlip:
            center = _np.clip(pos, 0, h)
        else:
            center = _np.clip(pos, 0, w)

    elif isinstance(pos, float):
        if verticalFlip:
            center = _np.round(h * pos).astype(int)
        else:
            center = _np.round(w * pos).astype(int)
    else:
        raise ValueError("Pos must be int or float")

    if verticalFlip:
        "Vertical mirror"
        if center == h or center == 0:
            "EDGE CASES"
            return _np.flipud(picture)
        first = picture[:center, :]
        second = picture[center:, :]

    else:
        "Horizontal Mirror"
        if center == w or center == 0:
            "EDGE CASES"
            return _np.fliplr(picture)
        first = picture[:, :center]
        second = picture[:, center:]

    " NORMAL MIRROR "
    if verticalFlip:
        if flip:
            first = _np.flipud(second)
        else:
            second = _np.flipud(first)

    else:
        if flip:
            first = _np.fliplr(second)
        else:
            second = _np.fliplr(first)

    axis = 0 if verticalFlip else 1
    combined = _np.concatenate([first, second], axis=axis)

    return combined


def cutoff_alpha(img, threshold=50):
    mask = img[:, :, 3] <= threshold
    img = img.copy()
    img[mask, 3] = 0
    return img


def color_blend(image, color, alpha):
    """
    Blend image with color. Takes any image and returns 3 channel image.

    Args:
        image: `np.ndarray`
            _description_

        color: `tuple`
            3 Colors in tuple (range from 0 to 255)

        alpha: `_type_`
            _description_


    Returns:
        _type_: _description_

    """
    assert isinstance(alpha, (int, float))
    assert len(color) == 3
    # color = _np.array(color, dtype=int)
    # assert isinstance(color, (_np.ndarray,))

    if len(image.shape) == 2:
        h, w = image.shape
        image = image[:, :, _np.newaxis]

    h, w, c = image.shape

    print(f"Array: {image.shape}, {color}")

    if c == 4:
        color = (*color, 255)
        has_mask = True
    elif c == 1:
        image = _np.tile(image, [1, 1, 3])
        has_mask = False
    else:
        has_mask = False

    blank = (_np.zeros_like(image) + color).astype(_np.uint8)

    if has_mask:
        mask = image[:, :, 3].copy()

    frame = _cv.addWeighted(image, 1 - alpha, blank, alpha, 0)

    if has_mask:
        frame[:, :, 3] = mask
    return frame


def crop_image(orig, left: float, right: float, top: float, bottom: float):
    """
    Crop image by giving fractions in 0-1 range

    Args:
        orig: `_type_`
            _description_

        left: `float`
            _description_

        right: `float`
            _description_

        top: `float`
            _description_

        bottom: `float`
            _description_


    Returns:
        _type_: _description_

    """
    if len(orig.shape) > 2:
        h, w, c = orig.shape
    else:
        h, w = orig.shape
        c = None

    top, down, left, right = _np.array(
        [top, bottom, left, right], dtype=float) / 100
    top = _np.round(top * h).astype(int)
    down = _np.round(down * h).astype(int)
    left = _np.round(left * w).astype(int)
    right = _np.round(right * w).astype(int)

    if top + bottom >= h:
        return orig
    elif left + right >= w:
        return orig
    return orig[top:h - down, left:w - right]

    # return sequence


__all__ = [
    'mirrorAxis',
    'color_blend',
    'crop_image',
    'cutoff_alpha',
]


if __name__ == "__main__":
    import cv2 as _cv2
    import os
    img = _cv2.imread(os.path.join(os.path.dirname(__file__), "cat.jpg"))

    count = 0
    imFlip = mirrorAxis(img, False, 0.3, False)

    "Loop checking"
    for pos in [0.2, 0, 400, 0.8]:
        for verticalFlip in [False, True]:
            for flip in [False, True]:
                # print()
                imFlip = mirrorAxis(img, verticalFlip, pos, flip)
                # _cv2.imshow(str(count), imFlip)
                count += 1
                # _cv2.imshow("image", imFlip)
                # _cv2.waitKey()

    print("Finished with success!")
