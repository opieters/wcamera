#!/usr/bin/env python
#!/usr/bin/env python

# Example using a character LCD plate.
import time
import Adafruit_CharLCD as LCD
from char_ui import *

# Initialize the LCD
lcd = LCD.Adafruit_CharLCDPlate()

# activate backlight and clear display and init everything
lcd.set_color(1.0, 1.0, 1.0)
lcd.clear()
lcd.message("Please wait...")
time.sleep(1)

# define special chars
for char in special_chars:
    lcd.create_char(i[0], i[1])

# configuration file
conf_file = "conf.json"

print("[INFO] Press Ctrl-C to quit.")
submenu = main_menu
try:
    while hasattr(submenu, '__call__'):
        submenu = submenu()
except KeyboardInterrupt:
    print("[INFO] KeyboardInterrupt, exiting...")
