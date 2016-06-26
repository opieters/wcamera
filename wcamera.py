#!/usr/bin/env python
#!/usr/bin/env python

# Example using a character LCD plate.
import time, os, json
import Adafruit_CharLCD as LCD
from char_ui import *

# Initialize the LCD
lcd = LCD.Adafruit_CharLCDPlate()

# activate backlight and clear display and init everything
lcd.set_color(1.0, 1.0, 1.0)
lcd.clear()
lcd.message("Please wait...")
time.sleep(1)

# configuration file
conf_file = "conf.json"
conf = json.load(open(conf_file))

# check if frame/video save folder exists
if not os.path.exists(conf["directory"]):
    os.makedirs(conf["directory"])

# define special chars
for char in special_chars:
    lcd.create_char(char[0], char[1])

# start program at main_menu
print("[INFO] Press Ctrl-C to quit.")
submenu = main_menu
try:
    while hasattr(submenu, '__call__'):
        submenu = submenu(lcd)
except KeyboardInterrupt:
    print("[INFO] KeyboardInterrupt, exiting...")
