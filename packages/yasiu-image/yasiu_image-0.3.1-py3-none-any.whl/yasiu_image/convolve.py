from scipy.signal import convolve2d as _convolve2d
import numpy as _np
import cv2 as _cv
from scipy import stats as _st


def gauss_kernel(kernlen=21, nsig=3):
    """Returns a 2D Gaussian kernel."""
    assert kernlen >= 0
    x = _np.linspace(-nsig, nsig, kernlen + 1)
    kern1d = _np.diff(_st.norm.cdf(x))
    kern2d = _np.outer(kern1d, kern1d)
    return kern2d / kern2d.sum()


def convolve_pic(image, keep_margin: int, kernel, allowed_channels):
    assert keep_margin >= 0
    assert isinstance(keep_margin, (int,))

    mask_of_original_pixels = _np.ones_like(image, dtype=bool)
    mask_of_original_pixels[keep_margin:-
                            keep_margin, keep_margin:-keep_margin] = False

    if len(image.shape) == 2:
        picture_channels = 0
    else:
        picture_channels = image.shape[2]
    allowed_channels = [
        ch for ch in allowed_channels if ch < picture_channels
    ]

    allowed_channels = list(set(allowed_channels))

    if not allowed_channels:
        return image

    output = image.copy()
    for ch_i in allowed_channels:
        channel = image[:, :, ch_i]
        new_ch = _convolve2d(channel, kernel, 'same')
        new_ch = _np.clip(new_ch.round(), 0, 255).astype(_np.uint8)
        output[:, :, ch_i] = new_ch

    output[mask_of_original_pixels] = image[mask_of_original_pixels]
    return output


def mean_filter(image, radius=1, channel_ind=0):
    size = 1 + 2 * radius
    kernel = _np.ones((size, size))
    kernel = kernel / kernel.sum()

    if channel_ind == 4:
        allowed_channels = [0, 1, 2, 3]
    else:
        allowed_channels = [channel_ind]

    output = convolve_pic(image, radius, kernel, allowed_channels)

    return output


def median_filter(image, dist=1, channel=0):
    size = 1 + 2 * dist
    kernel = _np.zeros((size, size))
    kernel[size // 2, :] = 1 / size
    kernel[:, size // 2] = 1 / size
    kernel[size // 2, size // 2] = size
    kernel /= kernel.sum()

    if channel == -1:
        allowed_channels = [0, 1, 2, 3]
    else:
        allowed_channels = [channel]

    output = convolve_pic(image, dist, kernel, allowed_channels)

    return output


def erode_dilate(image, dilate=False, repeat=1, radius=1, affected_channels=[0, 1, 2]):
    size = 2 * radius + 1
    half = radius
    kernel = _np.zeros((size, size), dtype=_np.uint8)
    kernel[half, :] = 1
    kernel[:, half] = 1
    output = image.copy()

    if len(image.shape) > 2:
        c = image.shape[2]
    else:
        c = None

    if c is None:
        chan = image.copy()
        if dilate:
            new_ch = _cv.dilate(chan, kernel, iterations=repeat)
        else:
            new_ch = _cv.erode(chan, kernel, iterations=repeat)

        output = _np.clip(new_ch.round(), 0, 255).astype(_np.uint8)
        # output[:, :, ch] = new_ch
    else:
        allowedChannels = [ch for ch in affected_channels if ch < c]

        for ch in allowedChannels:
            chan = image[:, :, ch]
            if dilate:
                new_ch = _cv.dilate(chan, kernel, iterations=repeat)
            else:
                new_ch = _cv.erode(chan, kernel, iterations=repeat)

            new_ch = _np.clip(new_ch.round(), 0, 255).astype(_np.uint8)
            output[:, :, ch] = new_ch

    return output
