import cv2 as _cv2
import numpy as _np


def resize_with_aspect_ratio(orig, resize_key='outer', new_dim=150):
    """

    :param sequence:
    :param resize_key:
        - outer
        - inner
        - height
        - width

    :param new_dim:
    :return:
    """
    h, w, c = orig.shape

    h_w_ratio = h / w
    w_h_ratio = w / h

    if h >= w and resize_key == 'outer':
        new_h = new_dim
        new_w = new_dim * w_h_ratio

    elif w >= h and resize_key == 'outer':
        new_w = new_dim
        new_h = new_dim * h_w_ratio

    elif resize_key == "height":
        new_h = new_dim
        new_w = new_dim * w_h_ratio

    elif resize_key == "width":
        new_w = new_dim
        new_h = new_dim * h_w_ratio

    elif h < w and resize_key == 'inner':
        new_h = new_dim
        new_w = new_dim * w_h_ratio
    else:
        new_w = new_dim
        new_h = new_dim * h_w_ratio

    new_h = _np.round(new_h).astype(int)
    new_w = _np.round(new_w).astype(int)

    # print(f"Resize: kwarg: {kwarg}")
    # sequence = [imutils.resize(fr, **kwarg) for fr in sequence]
    ret = _cv2.resize(orig, (new_w, new_h))
    return ret


def downscale_with_aspect_ratio(orig, resize_key='outer', max_dimension=150):
    """
    Scales picture down if size exceeds give dimension.


    :param orig:


    :param resize_key: specify which axis to resize
    :type resize_key: float

    resize_key:
        #. `outer` : resize bigger axis
        #. `inner` : resize smaller axis
        #. `height`: check height size
        #. `width` : check width size
    :type: str


    :type resize_key: str

    :param max_dimension:
    :return:
    """
    h, w, c = orig.shape

    h_w_ratio = h / w
    w_h_ratio = w / h

    if h >= w and resize_key == 'outer' and h > max_dimension:
        new_h = max_dimension
        new_w = max_dimension * w_h_ratio

    elif w >= h and resize_key == 'outer' and w > max_dimension:
        new_w = max_dimension
        new_h = max_dimension * h_w_ratio

    elif resize_key == "height" and h > max_dimension:
        new_h = max_dimension
        new_w = max_dimension * w_h_ratio

    elif resize_key == "width" and w > max_dimension:
        new_w = max_dimension
        new_h = max_dimension * h_w_ratio

    elif h < w and resize_key == 'inner' and h < max_dimension:
        new_h = max_dimension
        new_w = max_dimension * w_h_ratio
    elif w < h and resize_key == 'inner' and w < max_dimension:
        new_w = max_dimension
        new_h = max_dimension * h_w_ratio
    else:
        return orig

    new_h = _np.round(new_h).astype(int)
    new_w = _np.round(new_w).astype(int)

    # print(f"Resize: kwarg: {kwarg}")
    # sequence = [imutils.resize(fr, **kwarg) for fr in sequence]
    if new_w < w or new_h < h:
        ret = _cv2.resize(orig, (new_w, new_h))
        return ret
    return orig


def squerify(img: _np.ndarray, /, offset: float = 0.0, *, type_="clip"):
    """
    Clip excessive fraction of image.

    :param img: 2d np.ndarry

    :param type_: Only 'clip' is supported

    :param offset_val: float
        Pan clip to side.
        Horizonatal: -1 is left, 1 is right.
        Vertical: -1 is up, 1 is down.

        Offset = 0 clips at center.

    :return:
    """

    is_3d = len(img.shape) == 3

    if is_3d:
        H, W, C = img.shape
    else:
        H, W = img.shape
        C = None

    if H == W:
        "Square already"
        return img

    if type_ == "clip":
        gap = abs(H - W)
        pos = (_np.clip(offset, -1, 1) + 1) / 2

        first = (gap * pos).round().astype(int)
        second = first - gap
        if second == 0:
            second = None

        if H > W:
            new_img = img[first:second, :]
        else:
            new_img = img[:, first:second]

        # print("new shape", new_img.shape)
        return new_img
    else:
        raise KeyError("Only clip supported")


def extend(sequence, increase: tuple[float, float]):
    h, w, c = sequence[0].shape

    offset_y, offset_x = _np.abs(increase)
    offset_x = int(offset_x)
    offset_y = int(offset_y)

    output = []
    new_h = h + int(abs(offset_y))
    new_w = w + int(abs(offset_x))

    blank = _np.zeros((new_h, new_w, c), dtype=_np.uint8)

    # h_ind = (new_h - h) // 2
    # w_ind = (new_w - w) // 2
    h_off = 0 if offset_x > 0 else abs(offset_x)
    w_off = 0 if abs(offset_y) < 0 else offset_y

    for fr in sequence:
        new_frame = blank.copy()
        new_frame[h_off:h_off + h, w_off:w_off + w] = fr
        output.append(new_frame)

    return output


__all__ = [
    'squerify',
    'resize_with_aspect_ratio',
    'downscale_with_aspect_ratio',
    'extend',
]


if __name__ == "__main__":
    import os
    img = _cv2.imread(os.path.join(os.path.dirname(__file__), "cat.jpg"))
    smol = downscale_with_aspect_ratio(img, max_dimension=400)
    smol2 = downscale_with_aspect_ratio(smol, max_dimension=600)
    img = smol[200:, :, :]

    _cv2.imshow("Orig", img)
    # _cv2.imshow("Smol", smol)
    # _cv2.imshow("Smol600", smol2)

    sq = squerify(img, -1)
    _cv2.imshow("Cat Square -1", sq)
    sq = squerify(img, 0)
    _cv2.imshow("Cat Square 0 ", sq)
    sq = squerify(img, 0.5)
    _cv2.imshow("Cat Square 1", sq)
    _cv2.waitKey()
