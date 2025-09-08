import numpy as _np

from PIL import Image as _Image
import cv2 as _cv2
import imageio


def read_gif_frames(path, convertRGB2BGR=False):
    # img = _Image.open(path, )
    mimImage = imageio.mimread(path)

    for img in mimImage:
        if convertRGB2BGR:
            img = _cv2.cvtColor(img, _cv2.COLOR_BGR2RGB)
        # print(img.shape)
        yield img


def read_gif_frames_ToList(path, *args, **kwrg):
    return [*read_gif_frames(path, *args, **kwrg)]


def read_gif_frames_ToNumpyArray(path, *args, **kwrg):
    # raise NotImplementedError
    temp = read_gif_frames_ToList(path, *args, **kwrg)
    array = _np.ones((*temp[-1].shape, len(temp)), dtype=_np.uint8)
    maxChan = temp[-1].shape[2]
    # array = array[:, :, :, _np.newaxis]
    # print("array shape:", array.shape)
    # array[:] = temp
    for i, im in enumerate(temp):
        # print(im.shape, "entry")
        if (maxChan > im.shape[2]):
            flat = _np.ones_like(im[:, :, 0])
            flat = flat[:, :, _np.newaxis]
            # print(flat.shape, "flat")
            im = _np.concat([im, flat], axis=2)

            # print(im.shape, "upper")
        # print(im.shape)

        array[:, :, :, i] = im

    return array


def read_webp_frames(path, convertRGB2BGR=False):
    # img = _Image.open(path, )
    mimImage = imageio.mimread(path)

    for img in mimImage:
        if convertRGB2BGR:
            img = _cv2.cvtColor(img, _cv2.COLOR_BGR2RGB)
        # print(img.shape)
        yield img


def save_image_list_to_gif(frames, exp_path, use_rgba=False, duration=40, quality=100, disposal=2):
    """

    Args:
        frames:
        exp_path: path to export file with ".gif" ending
        use_rgba: bool,
        duration: int, default 40, [ms], preferable in range <20, 80>
        quality: 100
        disposal: int, default 2 = clear

    Returns:

    """

    if not (exp_path.endswith("gif") or exp_path.endswith("GIF")):
        exp_path += ".gif"

    if use_rgba:
        for img in frames:
            print(img.shape)
            assert img.shape[2] == 3, f"Image must have alpha channel! But has: {img.shape}"

        pil_frames = [_Image.fromarray(fr).convert("RGBA") for fr in frames]

        for pil_fr, fr in zip(pil_frames, frames):
            alpha_pil = _Image.fromarray(fr[:, :, 3])
            pil_fr.putalpha(alpha_pil)

    else:
        pil_frames = [_Image.fromarray(fr).convert("RGB") for fr in frames]

    pil_frames[0].save(
        exp_path, save_all=True, append_images=pil_frames[1:],
        optimize=False, loop=0,
        # background=(0, 0, 0, 255),
        quality=quality, duration=duration,
        disposal=disposal,
    )
    return 0


# __all__ = ['read_webp_frames', 'read_gif_frames', 'save_image_list_to_gif']

if __name__ == "__main__":
    import os
    GIF_PATH = os.path.join(os.path.dirname(__file__), "..", "images", "vader_crop.gif")
    import yasiu_image.io
    import cv2
    for (i, frame) in enumerate(yasiu_image.io.read_gif_frames(GIF_PATH)):
        pass
        text = f"Frame {i}: shp: {frame.shape}"
        print(text)
        cv2.imshow("Image", frame)
        cv2.waitKey()
        # print

    print("Finished with success!")
