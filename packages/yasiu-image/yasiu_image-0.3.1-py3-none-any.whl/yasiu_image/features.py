import numpy as _np
import cv2 as _cv2

import matplotlib.pyplot as _plt


# from yasiu_image.image import stack_images_to_grid


def image_to_features(image, include_pos=False, norm_pos=True, weight_pos=1.0):
    """
    Convert each pixel into separate feature
    include_pos: bool, to add pixel location or not.
    norm_pos: bool, to normalize position to <0,1> range
    weight_pos: scale normalized position with weight
    """
    h, w, *_ = image.shape
    fts = image.reshape(h * w, -1) / 255

    if include_pos:
        y, x = _np.ogrid[:h, :w]
        XX, YY = _np.meshgrid(x, y)
        if norm_pos:
            XX = XX / (w - 1) * weight_pos
            YY = YY / (h - 1) * weight_pos

        # print(XX)
        # print(YY)
        poses = _np.stack([XX, YY], axis=-1)
        poses = poses.reshape(h * w, 2)

        fts = _np.concatenate([fts, poses], axis=1)

    return fts


__all__ = [
    'image_to_features',
    'features_to_image',
]


def features_to_image(features, shape, remove_pos_columns=False, undo_normalization=True):
    """
    Revert features to image.
    """
    if remove_pos_columns:
        features = features[:, :-2]

    if len(shape) == 3:
        h, w, c = shape
        # shape = h, w, c
    else:
        h, w = shape
        # shape = h, w

    image = features.reshape(shape)

    if undo_normalization:
        image = _np.round(image * 255).astype(_np.uint8)

    return image


if __name__ == "__main__":
    import os
    image = _cv2.imread(os.path.join(os.path.dirname(__file__), "cat.jpg"))
    # image = _cv2.resize(image, (400, 400), )

    # image = np.arange(30, dtype=np.uint8)
    # image = image.reshape((5, 6))

    "Get Features"
    fts = image_to_features(image, include_pos=True)
    # print(image)
    # print("Features:")
    # print(fts)

    # "Revert features"
    rev_img = features_to_image(fts[:, :3], image.shape)
    # cv2.imshow("Rev", image)
    # cv2.waitKey()
    # print(image)
    # print(rev_img)
    # print(image.shape, rev_img.shape)

    # stack = stack_images_to_grid([image, rev_img])
    # image = image[:, :, [2, 1, 0]]
    stack = _np.concatenate([image, rev_img], axis=1).astype(_np.uint8)
    _plt.imshow(stack)
    # plt.figure()
    _plt.colorbar()
    _plt.show()
