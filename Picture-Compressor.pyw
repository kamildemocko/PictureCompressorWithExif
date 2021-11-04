import os
import math
import shutil
from PIL import Image
import piexif
from fractions import Fraction

## Config
PICTURE_QUALITY = 80
VALID_EXTENSIONS = [".jpg", ".jpeg", ".gif", ".png"]
FOLDER_TO_PROCESS = r"."


def process_image(root: str, filename: str) -> str:
    """Opens an image, optimizes the picture and saves it as jpg, returns file path"""
    """ Input file will be deleted and replaced """

    def get_exif_bytes(pil_pic: Image.Image) -> bin:

        def handle_int_touple_error(e: piexif.ImageIFD, num: int) -> None:
            """ Checks for undesired instance and changes it to touple """

            # if not e["0th"]: return
            if not "0th" in e: return
            if not num in e["0th"]: return

            # if not e["0th"][num]: return

            if isinstance(e["0th"][num], int):
                e["0th"][num] = (e["0th"][num], 1)

        # If exif exists, save it, otherwise set empty dict, handle bugs
        pic_exif = piexif.load(pil_pic.info["exif"]) if "exif" in pil_pic.info else {}
        if pic_exif:
            handle_int_touple_error(pic_exif, 282)
            handle_int_touple_error(pic_exif, 283)
        return piexif.dump(pic_exif)


    # Change orig file name
    original_file_path = os.path.join(root, "tmp." + filename)
    output_path = os.path.join(root, os.path.splitext(filename)[0] + ".jpg")
    shutil.move(os.path.join(root, filename), original_file_path)

    pic = Image.open(original_file_path)
    # convert to rgb -- some pics (gifs) are in different colorspace
    if pic.mode != "RGB":
        pic = pic.convert("RGB")

    pic_exif_bytes = get_exif_bytes(pic)

    pic.save(output_path, optimize=True, quality=PICTURE_QUALITY, exif=pic_exif_bytes)
    pic.close()

    shutil.copystat(original_file_path, output_path)

    os.remove(original_file_path)

    return output_path


def get_filesize_kb(path: str) -> int:
    file_size = os.stat(path).st_size / 1024  # size in KB
    file_size = math.floor(file_size)
    return file_size


def get_saved_percentage(input: int, output: int) -> int:
    return 100 - math.floor(output * 100 / input)


print("Start")

walk = os.walk(FOLDER_TO_PROCESS)
bytes_saved = 0


for root, _, files in walk:
    files = [
        file for file in files if os.path.splitext(file.lower())[-1] in VALID_EXTENSIONS
    ]

    if len(files) < 1:
        continue

    for file_ in files:
        input_file_size = get_filesize_kb(os.path.join(root, file_))

        output_path = process_image(root, file_)

        output_file_size = get_filesize_kb(output_path)
        bytes_saved += input_file_size - output_file_size

        print(
            f"Converted file {file_}, "
            f"saved {get_saved_percentage(input_file_size, output_file_size)}%"
        )

print(F"Bytes saved: {bytes_saved} KB ({round(bytes_saved / 1024, 2)} MB)")
input("Enter to exit")