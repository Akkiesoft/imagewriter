#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
diskimage writer

Copyright 2019 @Akkiesoft
akkiesoft@marokun.net
The MIT License
https://opensource.org/licenses/mit-license.php

* Required module and libraries(config, SH1106):
  Waveshare 1.3 inch OLED HAT
    https://www.waveshare.com/wiki/1.3inch_OLED_HAT
"""

import os
import sys
import configparser
import time
from glob import glob
from pathlib import Path
import pyudev
import parted
from subprocess import Popen, PIPE
import RPi.GPIO as GPIO

import config
import SH1106
from oledscreen import oledscreen, oledmenu

# Check argv
if len(sys.argv) > 1:
  conf_file = sys.argv[1]
else:
  print('USAGE: %s <config file>' % sys.argv[0])
  sys.exit(1)

# Read config file
try:
  conf = configparser.ConfigParser()
  conf.read(conf_file)
  font_path = conf.get('config', 'font_path')
  img_path = conf.get('config', 'img_path')
  ini_ssh = conf.getint('ssh', 'enabled')
except Exception as e:
  print("Could not read config file.: %s" % e)
  sys.exit(1)

KEY_UP_PIN    = 6
KEY_DOWN_PIN  = 19
KEY_LEFT_PIN  = 5
KEY_RIGHT_PIN = 26
KEY_PRESS_PIN = 13
KEY1_PIN      = 21
KEY2_PIN      = 20
# KEY3_PIN      = 16

lock_screen = False

GPIO.setmode(GPIO.BCM)
GPIO.setup(KEY_UP_PIN,    GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_DOWN_PIN,  GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_LEFT_PIN,  GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_RIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY_PRESS_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY1_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
GPIO.setup(KEY2_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up
# GPIO.setup(KEY3_PIN,      GPIO.IN, pull_up_down=GPIO.PUD_UP) # Input with pull-up

# こいつはimagewriter専用なのでここでいい
class oledstatus(oledscreen):
    def __init__(self, width, height, font_path, font_size, line_height, cursor = 0):
        super().__init__(width, height, font_path, font_size, line_height, cursor)
        self.type = "status"
        self.canwrite = False
    def setimage(self, s):
        self.text(0, "Image:")
        self.text(1, s)
    def setssh(self, s):
        self.text(2, "SSH: %s" % s)
    def setstatus(self, s, disp = False):
        self.text(3, "Status: %s" % s)
        if disp:
            self.flush(disp)
    def progress(self, s, disp):
        self.text(4, s)
        self.flush(disp)
    def flush(self, disp):
        disp.ShowImage(disp.getbuffer(self.image))

# controll menu <-> status
def button_menu(channel):
    global current_screen, mainmenu, imgmenu, sshmenu, lock_screen
    if current_screen.type == "menu":
        if channel == KEY_UP_PIN:
            current_screen.moveup()
        elif channel == KEY_DOWN_PIN:
            current_screen.movedown()
        elif channel == KEY_PRESS_PIN:
            if current_screen.is_parent():
                current_screen = current_screen.child[current_screen.cursor]
            elif current_screen.is_child():
                current_screen = current_screen.parent
        elif channel == KEY1_PIN:
            current_screen = mainscreen
            mainscreen.setimage(imgmenu.menu[imgmenu.cursor])
            mainscreen.setssh(sshmenu.menu[sshmenu.cursor])
    elif current_screen.type == "status":
        if channel == KEY1_PIN and not lock_screen:
            current_screen = mainmenu
            mainmenu.setcursor(0)
    disp.ShowImage(disp.getbuffer(current_screen.image))

# only KEY_2::Write button
def button_burn(channel):
    global lock_screen, dev
    if not mainscreen.canwrite:
        return
    lock_screen = True
    mainscreen.setstatus("Writing.", disp)
    img = img_path_list[imgmenu.cursor]
    dd_img(img, dev)
    if sshmenu.cursor:
        mainscreen.setstatus("Touch ssh file", disp)
        touch_ssh(dev)
    mainscreen.setstatus("Done!", disp)
    lock_screen = False

def dd_img(img, dev):
    cmd_dd = ["dd", "of=%s" % dev, "bs=4M", "conv=fsync", "status=progress"]
    # 雑
    if img == "/dev/zero":
        cmd_dd.insert(1, "if=%s" % img)
        dd = Popen(cmd_dd, stderr=PIPE)
    else:
        cmd_unzip = ["unzip", "-p", img]
        unzip = Popen(cmd_unzip, stdout=PIPE, stderr=PIPE)
        dd = Popen(cmd_dd, stdin=unzip.stdout, stderr=PIPE)
        unzip.stdout.close()

    # https://stackoverflow.com/questions/54856890/
    # https://gist.github.com/hikoz/741643
    line = ''
    while dd.poll() is None:
        try:
            s = dd.stderr.read(1).decode("utf-8")
        except UnicodeDecodeError:
            # for multibyte locales
            pass
        if s == '\r':
            i = line.replace('(', '').replace(')', '').replace(',', '').split(' ')
            if 9 < len(i):
                mainscreen.progress(''.join([i[2], i[3], "(", i[9], i[10], ")"]), disp)
            line = ''
        else:
            line = line + s
    mainscreen.progress('', disp)

def touch_ssh(dev):
    cmd_mount = ['mount', '%s1' % dev, "/mnt"]
    mount = Popen(cmd_mount, stderr=PIPE)
    while mount.poll() is None:
        time.sleep(0.1)
    Path('/mnt/ssh').touch()
    cmd_umount = ['umount', '%s1' % dev]
    umount = Popen(cmd_umount, stderr=PIPE)
    while umount.poll() is None:
        time.sleep(0.1)


def detect_storage(path):
    global current_screen, mainscreen
    try:
        parted.getDevice(path).removeFromCache()
        mainscreen.setstatus("%s detected" % path)
        if current_screen == mainscreen:
            mainscreen.flush(disp)
            time.sleep(2)
        mainscreen.setstatus("Press KEY2 to write!")
        if current_screen == mainscreen:
            mainscreen.flush(disp)
        mainscreen.canwrite = True
    except parted.IOException:
        mainscreen.canwrite = False
        if current_screen == mainscreen:
            mainscreen.setstatus("%s removed" % path)
            mainscreen.flush(disp)
            time.sleep(2)
        mainscreen.setstatus("Ready.")
        if current_screen == mainscreen:
            mainscreen.flush(disp)

img_path_list = sorted(glob(img_path), reverse=True)
img_path_list.append("/dev/zero")
img_name_list = []
for i in img_path_list:
    img_name_list.append(Path(i).name.replace("-raspbian", "").replace(".zip", ""))

dev = ''

try:
    # Initialize library.
    disp = SH1106.SH1106()
    disp.Init()
    disp.clear()

    # main menu
    mainmenu = oledmenu(disp.width, disp.height, font_path, 8, 10, 5)
    mainmenu.settitle('Menu')
    mainmenu.setmenu(['Select Image File', 'SSH Configuration'])

    # image menu class
    imgmenu = oledmenu(disp.width, disp.height, font_path, 8, 10, 5)
    imgmenu.settitle('Select Image File')
    imgmenu.setmenu(img_name_list)

    # SSH menu class
    sshmenu = oledmenu(disp.width, disp.height, font_path, 8, 10, 5)
    sshmenu.settitle('SSH Configuration')
    sshmenu.setmenu(["Disable", "Enable"])
    sshmenu.setcursor(ini_ssh)

    # set menu relations
    mainmenu.setchild([imgmenu, sshmenu])
    imgmenu.setparent(mainmenu)
    sshmenu.setparent(mainmenu)

    # main screen
    mainscreen = oledstatus(disp.width, disp.height, font_path, 8, 10, 5)
    mainscreen.settitle('Raspbian Image Writer')
    mainscreen.setimage(imgmenu.menu[imgmenu.cursor])
    mainscreen.setssh(sshmenu.menu[sshmenu.cursor])
    mainscreen.setstatus("Ready")

    current_screen = mainscreen
    mainscreen.flush(disp)

    GPIO.add_event_detect(KEY_UP_PIN,    GPIO.RISING, bouncetime=200, callback=button_menu)
    GPIO.add_event_detect(KEY_DOWN_PIN,  GPIO.RISING, bouncetime=200, callback=button_menu)
    GPIO.add_event_detect(KEY_PRESS_PIN, GPIO.RISING, bouncetime=200, callback=button_menu)
    GPIO.add_event_detect(KEY1_PIN,      GPIO.RISING, bouncetime=200, callback=button_menu)
    GPIO.add_event_detect(KEY2_PIN,      GPIO.RISING, bouncetime=200, callback=button_burn)

    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem = 'block', device_type = 'disk')
    monitor.start()

    for device in iter(monitor.poll, None):
        a = device.action
        c = device.get('DISK_MEDIA_CHANGE')
        u = device.get('ID_BUS')
        if a == "change" and c == "1" and u == "usb":
            dev = device.get('DEVNAME')
            detect_storage(dev)

except IOError as e:
    print(e)

except KeyboardInterrupt:
    print("ctrl + c")
    GPIO.cleanup()
    exit()
