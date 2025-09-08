import numpy as _np
import cv2 as _cv2


def squareError(pic1: _np.ndarray, pic2: _np.ndarray, normalize=False):
    """
    Compare quality of 2 pictures 
    Normalize:
        shoud picture be normalized to dimensions?
    """
    if len(pic1.shape) != len(pic2.shape) or (len(pic1.shape) == 3 and (pic1.shape[2] != pic2.shape[2])):
        raise ValueError(
            f"Input pictures have different amount of dimensions 1:{pic1.shape}, 2:{pic2.shape}")
        return 0.0

    if len(pic1.shape) == 3:
        H, W, C = pic1.shape
    else:
        H, W = pic1.shape
        C = 1

    error = _np.abs(pic1 - pic2)**2
    error = error / C / 255 / 255

    if normalize:
        error = error / H / W

    error = _np.sum(error)
    return error


def meanError(pic1: _np.ndarray, pic2: _np.ndarray, normalize=True):
    """
    Compare quality of 2 pictures
    Normalize:
        shoud picture be normalized to dimensions?
    """
    if len(pic1.shape) != len(pic2.shape) or (len(pic1.shape) == 3 and (pic1.shape[2] != pic2.shape[2])):
        raise ValueError(
            f"Input pictures have different amount of dimensions 1:{pic1.shape}, 2:{pic2.shape}")
        return 0.0

    if len(pic1.shape) == 3:
        H, W, C = pic1.shape
    else:
        H, W = pic1.shape
        C = 1

    error = _np.abs(pic1 - pic2)
    error = error / C / 255

    if normalize:
        error = error / H / W

    error = _np.sum(error)
    return error


__all__ = [
    'meanError',
    'squareError',
]

if __name__ == "__main__":
    import os
    img = _cv2.imread(os.path.join(os.path.dirname(__file__), "cat.jpg"))
