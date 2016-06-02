import json
import os
from PIL import Image, ImageOps
from PIL.ExifTags import TAGS
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('path', metavar='PATH', type=str, help='Path to images to use for gallery')
parser.add_argument('-f', '--first', type=str, help="Filename of gallery showcase image, defaults to first in folder")
parser.add_argument('-b', '--base', type=str, default="", help="Base path for gallery, specify the relative path to the images on your server")
parser.add_argument('-m', '--meta', action='store_true', default=False, help="Read title tag from metadata, requires pyexiv2 will default to use filename as title")

def ThumbNail(path, large=False):
    if large:
        size = (240, 240)
    else:
        size = (240, 160)
    infile = path
    outfile = RESULT + "/" + path.split("/")[-1:][0] + "_thumb.jpg"
    if infile != outfile:
        try:
            im = Image.open(infile)
            im = ImageOps.fit(im, size, Image.ANTIALIAS)
            im.save(outfile, "JPEG")
        except IOError:
            print("cannot create thumbnail for", infile)
    return outfile

def bigImage(path):
    large_size = (1920, 1080)

    im = Image.open(path)
    outfile = RESULT + "/" + path.split("/")[-1:][0] + "_big.jpg"
    image_w, image_h = im.size
    aspect_ratio = image_w / float(image_h)
    new_height = int(large_size[0] / aspect_ratio)

    if new_height < 1080:
        final_width = large_size[0]
        final_height = new_height
    else:
        final_width = int(aspect_ratio * large_size[1])
        final_height = large_size[1]

    imaged = im.resize((final_width, final_height), Image.ANTIALIAS)

    imaged.save(outfile, quality=80)
    return {
            "src": outfile,
            "size": str(final_width) +"x"+str(final_height)
        }

def smallImage(path):
    large_size = (800, 600)

    im = Image.open(path)
    outfile = RESULT + "/" + path.split("/")[-1:][0] + "_small.jpg"
    image_w, image_h = im.size
    aspect_ratio = image_w / float(image_h)
    new_height = int(large_size[0] / aspect_ratio)

    if new_height < 600:
        final_width = large_size[0]
        final_height = new_height
    else:
        final_width = int(aspect_ratio * large_size[1])
        final_height = large_size[1]

    imaged = im.resize((final_width, final_height), Image.ANTIALIAS)

    imaged.save(outfile, quality=60)
    return {
            "src": outfile,
            "size": str(final_width) +"x"+str(final_height)
        }

SLIDES = []

args = parser.parse_args()

PATH = args.path
RESULT = "output"
if args.first:
    first = args.first
else:
    first = None
stored = False

for filename in os.listdir(PATH):
    data = {
        "originalImage": bigImage(PATH + "/" + filename),
        "mediumImage": smallImage(PATH + "/" + filename)
    }
    if args.meta:
        import pyexiv2
        metadata = pyexiv2.ImageMetadata(PATH + "/" + filename)
        metadata.read()
        if 'Xmp.dc.title' in metadata.xmp_keys:
            data["title"] = (metadata['Xmp.dc.title'].raw_value['x-default'])
    else:
        data["title"] = filename.split(".")[0]

    if filename == first or (first == None and not stored):
        data["msrc"] = ThumbNail(PATH + "/" + filename, True)
        SLIDES.insert(0, data)
        stored = True
    else:
        data["msrc"] = ThumbNail(PATH + "/" + filename)
        SLIDES.append(data)

with open("gallery.json", "w") as f:
    json.dump({"data":SLIDES},f)
