#!/usr/bin/env python

# Example using a character LCD plate.
import time, os, json
import Adafruit_CharLCD as LCD
from menu import Menu
from ui import UI
from core import Core

# Initialize the LCD
lcd = LCD.Adafruit_CharLCDPlate()

# activate backlight and clear display and init everything
lcd.set_color(1.0, 1.0, 1.0)
lcd.clear()
lcd.message("Please wait...")
time.sleep(1)

# define special chars
core = Core("conf.json") # configuration file
menu = Menu(lcd,core)


# check if frame/video save folder exists
if not os.path.exists(core.conf["directory"]):
    os.mkdir(core.conf["directory"])

# start program at main_menu
print("[INFO] Press Ctrl-C to quit.")
submenu = menu.main_menu

try:
    while hasattr(submenu, '__call__'):
        #core.generate_server_files()
        submenu = submenu()
except KeyboardInterrupt:
    print("[INFO] KeyboardInterrupt, exiting...")

core.delete()
