# Originally Discorddit | modified and improved by verix

import requests
import json
import textwrap
from time import sleep
from os.path import isfile
from datetime import datetime
from discord_hooks import Webhook #discord_hooks by verix

def config(section):
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def filewrite(data):
    with open("idcache.txt", "w") as f:
        for id in data:
            f.write(id["data"]["id"]+"\n")

def is_selfpost(data):
    if "reddit.com" in data["data"]["url"] and not "np.reddit.com" in data["data"]["url"]:
        return True
    else:
        return False

def is_preview(data):
    try:
        i = data["data"]["preview"]
        return True
    except:
        return False

def determine(data):
    if is_selfpost(data):
        return 0
    elif is_preview(data):
        return 1
    else:
        return 3

def get(sub):
    while True:
        try:
            html = requests.get("https://www.reddit.com/r/"+sub+"/top.json")
            data = html.json()["data"]["children"]
            return data
        except:
            pass

def truncate(text):
    from textwrap import shorten
    return shorten(text, 250)

def makepost(data, footerimg, colour, thumbnail, author_icon):
    det = determine(data)
    if det == 0:
        description = truncate(data["data"]["selftext"])
        imageurl = None
    elif det == 1:
        description = '[View Image]({})'.format(data["data"]["url"])
        imageurl = data["data"]["preview"]["images"][0]["source"]["url"]
    elif det == 2:
        description = None
        imageurl = data["data"]["url"]
    elif det == 3:
        description = data["data"]["url"]
        imageurl = None
    score = data['data']['score']
    comments = data['data']['num_comments']
    ech = data["data"]["created_utc"]

    msg = Webhook(url,color=int(colour))
    msg.set_author(name=data["data"]["title"], url="https://reddit.com"+data["data"]["permalink"], icon=author_icon)
    msg.set_title(title="/u/"+data["data"]["author"], url="https://www.reddit.com/u/" + data["data"]["author"])
    if description: msg.set_desc(description)
    if imageurl:
        msg.set_thumbnail(imageurl)
    else:       
        msg.set_thumbnail(thumbnail)
    msg.set_footer(text="/r/"+data["data"]["subreddit"]+"  |  {} points and {} comments".format(score, comments),ts=ech,icon=footerimg)
    print(msg.json)


    return msg

def post(data, url, img, colour, thumbnail, author_icon):
    msg = makepost(data, img, colour, thumbnail, author_icon)
    msg.post()
    print("Posted {}".format(data["data"]["title"]).encode("utf-8"))

if __name__ == "__main__":
    required = config("Required")
    optional = config("Optional")
    print(required)
    subreddit = required["subreddit"]
    url = required["url"]
    img = optional["footerimg"]
    colour = required["colour"]
    thumbnail = optional["thumbnail"]
    author_icon = optional["author_icon"]
    x = False
    while True:
        data = get(subreddit)
        if isfile("./idcache.txt"):
            file =  open("idcache.txt","r")
            f = file.read().splitlines()
            file.close()
            i = 25 # Always will be 25 because 25 entries and a empty 26th line
            for id in reversed(data):
                i -= 1
                if id["data"]["id"] not in f:
                    post(data[i], url, img, colour, thumbnail, author_icon)
                    x = True
        filewrite(data)
        if not x:
            print("No new posts found...")
        print("Sleeping for 5 Minutes...")
        print("\n")
        sleep(300) # 5 Minutes in seconds


