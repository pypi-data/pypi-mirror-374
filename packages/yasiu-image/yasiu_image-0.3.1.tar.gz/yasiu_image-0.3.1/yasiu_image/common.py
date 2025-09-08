
import numpy as _np

import cv2 as _cv2


def stack_images_to_grid(
        images, labels=None, font_scale=1.2, font_thickness=3,
        border=2,
        auto_convert_monochannel=True,
        pics_in_row=3
):
    """
    Convert list of images to 1 Image in grid layout.
    """
    h, w, c = images[0].shape

    if labels is None:
        labels = [''] * len(images)
    elif len(labels) != len(images):
        raise ValueError("Lables size does not match images number")

    output_pic = None
    row_pic = None

    for ind, (ch, lb) in enumerate(zip(images, labels)):
        if len(ch.shape) == 2 and auto_convert_monochannel:
            ch = ch[:, :, _np.newaxis]
            rgb = _np.concatenate([ch, ch, ch], axis=2)

        elif ch.shape[2] == 4:
            rgb = ch[:, :, :3]

        elif ch.shape[2] == 1:
            rgb = _np.concatenate([ch, ch, ch], axis=2)

        else:
            # print("WHAT? What i missed?")
            # print(ch.shape)
            rgb = ch

        rgb = rgb.astype(_np.uint8)

        rgb = _cv2.putText(
            rgb, lb, (5, 30),
            fontScale=font_scale, fontFace=_cv2.FONT_HERSHEY_SIMPLEX, color=(
                50, 50, 0),
            thickness=font_thickness + 5,
        )
        rgb = _cv2.putText(
            rgb, lb, (5, 30),
            fontScale=font_scale, fontFace=_cv2.FONT_HERSHEY_SIMPLEX, color=(
                50, 255, 0),
            thickness=font_thickness,
        )

        # print(f"row: {row_pic.shape}, rgb: {rgb.shape}")
        if row_pic is None:
            row_pic = rgb
        else:
            row_pic = _np.concatenate([row_pic, rgb], 1)

        # print(f"Row Pic: {row_pic.shape}")

        if not ((ind + 1) % pics_in_row) and ind != 0:
            if output_pic is None:
                output_pic = row_pic
            else:
                output_pic = _np.concatenate([output_pic, row_pic], axis=0)
            row_pic = None

    if row_pic is not None:
        if output_pic is None:
            output_pic = row_pic
        else:
            _, match_w, _ = output_pic.shape
            blank = _np.zeros((h, match_w, c), dtype=_np.uint8)
            cur_h, cur_w, _ = row_pic.shape
            blank[:cur_h, :cur_w] = row_pic
            output_pic = _np.concatenate([output_pic, blank], axis=0)

    return output_pic


__all__ = [
    'stack_images_to_grid'
]

if __name__ == "__main__":
    import os
    img = _cv2.imread(os.path.join(os.path.dirname(__file__), "cat.jpg"))

    print("Finished with success!")
