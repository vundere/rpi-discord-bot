"""Tools to handle image downloading, getting data from external files etc."""
import requests
import os
import json
from random import randint, randrange
from os import listdir
from pathlib import Path

CONF_FILE = 'cfg/bot_config.json'

with open(CONF_FILE, 'r') as conf:
    file = json.load(conf)
    IMG_FOLDER = file["localpaths"]["memes"]
    HERESY = file["localpaths"]["heresy"]
    OW = file["localpaths"]["ow"]
    BED = file["localpaths"]["pomf"]

ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif", "mp4", "gifv"]


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def file_exists(path):
    checkfile = Path(path)
    return checkfile.is_file()


def save_mem(url, filename):
    full_path = IMG_FOLDER+filename
    if file_exists(full_path) or not allowed_file(filename):
        return False
    else:
        image_content = requests.get(url).content
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        output = open(full_path, 'wb')
        output.write(image_content)
        output.close()
        return True


def stash(url, filename):
    full_path = "/home/pi/shared/rpi-discord-bot/lewdstore/"+filename
    if not allowed_file(filename) or file_exists(full_path):
        return False
    else:
        image_content = requests.get(url).content
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        output = open(full_path, 'wb')
        output.write(image_content)
        output.close()
        return True


def get_rand_mem():
    all_files = listdir(IMG_FOLDER)
    return "img/"+all_files[randint(0, (len(all_files)-1))]


def discord_filename_fix(filename):
    return filename.replace("_", " ", 2)


def is_heresy(filename):
    full_path = HERESY + filename
    return file_exists(full_path)


def get_heresy():
    with open("static/lists/bloodlist.txt", "r") as n:
        acceptable_heresy = n.read().split("\n")
    return acceptable_heresy[randrange(0, len(acceptable_heresy))]


def get_watched():
    def local():
        ow_image_folder = listdir(OW)
        result = []
        for image in ow_image_folder:
            if allowed_file(image):
                result.append(image)
        return OW+result[randint(0, (len(result)-1))]

    def imgur():
        ow_image_folder = listdir(OW)
        result = []
        for image in ow_image_folder:
            if allowed_file(image):
                result.append(image)
        selected = result[randint(0, (len(result) - 1))]
        return 'http://i.imgur.com/' + selected.rsplit(" - ")[1]

    def imgur_from_list():
        with open("static/lists/watchlist.txt", "r") as n:
            result = n.read().split("\n")
        return result[randrange(0, len(result))]

    return imgur_from_list()


def watchlist(folder):
    """This just generates a list of imgur links to save space for RasPi use
    :param folder: internal name for the directory you want to make a list of.
    """
    if folder == 'ow':
        ow_image_folder = listdir(OW)
        w = "watchlist.txt"
        with open(w, 'w') as wr:
            for i in ow_image_folder:
                if allowed_file(i):
                    wr.write('http://i.imgur.com/' + i.rsplit(" - ")[1] + "\n")
    else:
        heresy_num = listdir("Q:/Users/Olav/Pictures/Warhams/imgur_approved/numbered/")
        heresy_unum = listdir("Q:/Users/Olav/Pictures/Warhams/imgur_approved/unnumbered/")
        w_h = "bloodlist.txt"
        with open(w_h, 'w') as wr:
            for i in heresy_num:
                if allowed_file(i):
                    wr.write('http://i.imgur.com/' + i.rsplit(" - ")[1] + "\n")
            for j in heresy_unum:
                if allowed_file(j):
                    wr.write('http://i.imgur.com/' + j + "\n")


def pomf_get():
    bed = listdir(BED)
    things_to_do_on_bed = []
    for action in bed:
        if allowed_file(action):
            things_to_do_on_bed.append(action)
    return BED + things_to_do_on_bed[randint(0, (len(things_to_do_on_bed)-1))]


def init_korean():
    with open("static/lists/nouns.txt", "r") as n:
        nouns = n.read().split("\n")
    with open("static/lists/verbs.txt", "r") as v:
        verbs = v.read().split("\n")
    result = {
        "nouns": nouns,
        "verbs": verbs
    }
    return result

# TODO create function for loading data from config that can be used across all cogs and see if that's more efficient
