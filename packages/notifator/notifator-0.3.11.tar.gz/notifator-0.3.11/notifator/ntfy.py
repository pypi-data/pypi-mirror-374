#!/usr/bin/env python3

from fire import Fire
import datetime as dt
from notifator.version import __version__

import cv2
import requests
import os
import sys
#----------------- text config file --------
from configparser import ConfigParser
# for take_image
import subprocess as sp
from PIL import Image

import base64

DEFAULT_RC = os.path.expanduser("~/.notifator.rcx")
DEFAULT_SECTION = "default"

TOTAL_NTFY_RC = os.path.expanduser("~/.config/influxdb/totalconfig.conf")
TOTAL_NTFY_SECTION = "ntfy"


def load_config( mysection, cfile=DEFAULT_RC, rowname="address"):
    configur = ConfigParser()
    address = None
    ok  = False
    try:
        #print("D... config path",os.path.expanduser(cfile))
        configur.read(os.path.expanduser(cfile) )
        ok = True
    except:
        print("X... cannot read the config from file ",cfile)
    if not ok:
        sys.exit(1)

    sections=configur.sections()
    if mysection in sections:
        address = configur.get(mysection, rowname)
        return address
    else:
        print("X... section not found: ", mysection)
        print("X... possible sections:", sections)
        sys.exit(0)


def take_screenshot( w=640, h=None):
    """
    gnome-screenshot
    """
    # Take the screenshot
    file_size = None
    sp.run(['gnome-screenshot', '-f', '/tmp/screenshot.png'])
    filename = None
    # Open the screenshot, resize, and save as JPG
    with Image.open('/tmp/screenshot.png') as img:
        original_width, original_height = img.size
        aspect_ratio = original_height / original_width
        h = int(w * aspect_ratio)
        img = img.convert('RGB')
        img = img.resize((w, h))
        filename=f'/tmp/screenshot_{w}_{h}.jpg'
        img.save(filename, 'JPEG')
        file_size = os.path.getsize(filename)
        print(f"i... file size = {file_size}")
    return filename



def send_ntf(message, title, section="default", scrshot=False, image=None):
    """
    send to ntfy.sh
    """

    url_full = ""
    username = None
    password = None
    topic = None
    if os.path.exists(DEFAULT_RC):
        url_full = load_config( section )
        # we expect http://ntfy.sh/test
    else:
        # we expect https://server
        # topic extra
        # u/p extra
        if os.path.exists(TOTAL_NTFY_RC):
            url_full = load_config( TOTAL_NTFY_SECTION, cfile=TOTAL_NTFY_RC, rowname="server")
            username = load_config( TOTAL_NTFY_SECTION, cfile=TOTAL_NTFY_RC, rowname="username")
            password = load_config( TOTAL_NTFY_SECTION, cfile=TOTAL_NTFY_RC, rowname="password")
            topic = load_config( TOTAL_NTFY_SECTION, cfile=TOTAL_NTFY_RC, rowname="topic")
        else:
            print("X... config doesnt exist: {TOTAL_NTFY_RC}")
            sys.exit(1)
    print(f"i... URL: {url_full}")

    #now = take_time()
    #title = f"{now}"
    #message = message
    #filename = None

    data = None
    filename = None
    msg2 = message
    tit2 = title
    authHeader = None
    if scrshot:
        print(f"i.... screenshot version...")
        msg2 = f""#THE message {now}"
        tit2 = message # the message will be in the title
        filename = take_screenshot()  #w=200
        data=open(filename, 'rb')
        filename = filename
    elif image is not None and os.path.exists( os.path.expanduser(image)):
        print(f"i.... image send version...")
        msg2 = f""#THE message {now}"
        tit2 = message # the message will be in the title
        filename = os.path.expanduser(image)#take_screenshot()  #w=200
        data=open(filename, 'rb')
        filename = filename
    else:
        print(f"D.... message version...")
        data = message
        #
        tit2 = ""  # It is nicer without a TITLE if not IMAGE
        #
        # no message here for some reason... and title = "" to make it short
        # "Actions": "http, OpenSeznam, https://www.seznam.cz/, method=PUT, headers.Authorization=Bearer zAzsx1sk.., body={\"action\": \"close\"}"   }

    print(f"i... sending request to {url_full}")

    if username is not None and password is not None and topic is not None:
        #username   = "testuser"
        #password   = "fakepassword"
        uspa = f"{username}:{password}"
        #print(uspa)
        bbb = base64.b64encode(uspa.encode() ).decode()
        print("D... base64", bbb)
        authHeader = "Basic " + bbb# '(username + ":" + password)# // -> Basic dGVzdHVzZXI6ZmFrZXBhc3N3b3Jk
        #print(authHeader)
        url_full = f"{url_full}/{topic}"
        #print(url_full)
        #print(data)
    #elif :
    #    print("x... username password or topic is not known")
    #    sys.exit(1)


    HEADERS = { "Title": f"{tit2}", # i dont use title if not image
                "Authorization": authHeader,
                "Filename": filename,
                "message": msg2,
                # "Actions": "http, OpenSeznam, https://www.seznam.cz/ "
               }
    #HEADERS = { "Authorization": authHeader }

    response = requests.post( url_full,
                             data=data,
                             headers=HEADERS
                            )

    if response.status_code == 200:
        print(f"Notification with image sent successfully!  {url_full}")
    else:
        print(f"Failed to send notification.  {url_full} ... {response.status_code}")
    return #message




def main():
    ad = load_config( "default" )
    print(f"i... sending to {ad}")
    send_ntf(f"test {dt.datetime.now()}", "tItLe", scrshot=False)

if __name__ == "__main__":
    Fire(main)
