#!/usr/bin/env python3
import os
import tempfile
import shutil
from sys import argv
import zipfile
from bs4 import BeautifulSoup
import ebooklib
from ebooklib import epub

if len(argv) == 1 or len(argv) > 3:
    print("Usage: epubimgext.py EPUB_FILE [OUTPUT_DIR]")
    exit()

epub_file = argv[1]
output_dir = argv[1] + "_img"
if len(argv) == 3:
    output_dir = argv[2]
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

try:
    reader = epub.EpubReader(epub_file)
    book = reader.load()
    reader.process()
except Exception as e:
    print("Failed to read EPUB with EbookLib:", e)
    exit()

tempdir = tempfile.TemporaryDirectory().name
try:
    with zipfile.ZipFile(epub_file, "r") as zip_ref:
        zip_ref.extractall(tempdir)
        zip_ref.close()
except Exception as e:
    print("Failed to extract:", e)
    exit()

imgindex=1
for itemId in book.spine:
    html = book.get_item_with_id(itemId[0]).get_name()
    html_path=os.path.join(tempdir, reader.opf_dir, html)
    html_file=open(html_path,"r", encoding="utf-8")
    soup = BeautifulSoup(html_file, 'html.parser')
    # Image element is for image in svg, like kobo. Its link is in xlink:href attribute
    images = soup.select("image, img")
    imglist = []
    for element in images:
        img_src = ""
        if element.name == "img":
            img_src = element["src"]
        else:
            img_src = element["xlink:href"]
        img_path = os.path.normpath(os.path.join(os.path.dirname(html_path), img_src))
        ext = img_src.split('.')[-1]
        newname = str(imgindex).zfill(3) + "." + ext
        newpath = os.path.join(output_dir, newname)
        print(img_src + ' -> '+ newname)
        imgindex += 1
        shutil.copy2(img_path, newpath)

        if img_path in imglist:
            print("duplicate image: ", newname)
        imglist.append(img_path)
    html_file.close()

shutil.rmtree(tempdir)
