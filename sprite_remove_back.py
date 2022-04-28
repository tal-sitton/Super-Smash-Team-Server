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


multipliers = []


def turn_to_RANDOM(path: str, new_path: str, name: str):
    if not multipliers:
        multipliers.append(random.randint(0, 50))
        multipliers.append(random.randint(0, 50))
        multipliers.append(random.randint(0, 10))

    img = Image.open(path + "\\" + name)
    img = img.convert("RGBA")

    pixdata = img.load()

    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y][2] > 150:
                pixdata[x, y] = (pixdata[x, y][0] * multipliers[0], pixdata[x, y][1] * multipliers[1],
                                 pixdata[x, y][2] * multipliers[2], pixdata[x, y][3])

    if not os.path.isdir(os.getcwd() + "\\" + new_path):
        os.makedirs(os.getcwd() + "\\" + new_path)

    img.save(new_path + "\\" + name)


def remove(path: str, new_path: str, name: str):
    img = Image.open(path + "\\" + name)
    img = img.convert("RGBA")

    pixdata = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y] == (77, 109, 243, 255):
                pixdata[x, y] = (255, 255, 255, 0)

    if not os.path.isdir(os.getcwd() + "\\" + new_path):
        os.makedirs(os.getcwd() + "\\" + new_path)

    img.save(new_path + "\\" + name)


def redundent_remove(path: str, new_path: str, name: str):
    img = Image.open(path + "\\" + name)
    img = img.convert("RGBA")

    pixdata = img.load()
    if img.size[0] < 10:
        os.remove(path + "\\" + name)


if __name__ == '__main__':
    print(os.getcwd())
    file_list = []
    for root, dirs, files in os.walk("Dude"):
        for file in files:
            remove(root, f"spi", file)
            # redundent_remove(root, f"spi", file)
            file_list.append((root, file))
    print(file_list)
