import os
import random

from PIL import Image


def turn_to_red(path: str, new_path: str, name: str):
    img = Image.open(path + "\\" + name)
    img = img.convert("RGBA")

    pixdata = img.load()

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][2] > 150:
                pixdata[x, y] = (pixdata[x, y][2], pixdata[x, y][1], pixdata[x, y][0], pixdata[x, y][3])

    if not os.path.isdir(os.getcwd() + "\\" + new_path):
        os.makedirs(os.getcwd() + "\\" + new_path)

    img.save(new_path + "\\" + name)


def turn_to_green(path: str, new_path: str, name: str):
    img = Image.open(path + "\\" + name)
    img = img.convert("RGBA")

    pixdata = img.load()

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][2] > 150:
                pixdata[x, y] = (pixdata[x, y][0], pixdata[x, y][2], pixdata[x, y][1], pixdata[x, y][3])

    if not os.path.isdir(os.getcwd() + "\\" + new_path):
        os.makedirs(os.getcwd() + "\\" + new_path)

    img.save(new_path + "\\" + name)


rgb = []


def turn_to_RANDOM(path: str, new_path: str, name: str):
    global rgb
    if not rgb:
        rgb = [
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        ]

    img = Image.open(path + "\\" + name)
    img = img.convert("RGBA")

    pixdata = img.load()

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][0] > 150 and pixdata[x, y][1] < 100 and pixdata[x, y][2] < 100:
                print("done stuff")
                pixdata[x, y] = (*rgb, pixdata[x, y][3])

    if not os.path.isdir(os.getcwd() + "\\" + new_path):
        os.makedirs(os.getcwd() + "\\" + new_path)

    img.save(new_path + "\\" + name)
    print(rgb)


if __name__ == '__main__':
    print(os.getcwd())
    file_list = []
    for root, dirs, files in os.walk("RED"):
        for file in files:
            dir = root.split("\\")[1]
            turn_to_RANDOM(root, f"spi5\\{dir}", file)
            file_list.append((root, file))
    print(file_list)
