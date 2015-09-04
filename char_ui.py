#!/usr/bin/python
# Example using a character LCD plate.
import math
import time
import os

import Adafruit_CharLCD as LCD

# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()

# create some custom characters
lcd.create_char(1, [2, 3, 2, 2, 14, 30, 12, 0])
lcd.create_char(2, [0, 1, 3, 22, 28, 8, 0, 0])
lcd.create_char(3, [0, 14, 21, 23, 17, 14, 0, 0])
lcd.create_char(4, [31, 17, 10, 4, 10, 17, 31, 0])
lcd.create_char(5, [8, 12, 10, 9, 10, 12, 8, 0])
lcd.create_char(6, [2, 6, 10, 18, 10, 6, 2, 0])
lcd.create_char(7, [31, 17, 21, 21, 21, 21, 17, 31])


lcd.set_color(1.0, 1.0, 1.0)
lcd.clear()

# Make list of button value, text, and backlight color.
buttons = ( (LCD.SELECT, 'Select', (1,1,1)),
            (LCD.LEFT,   'Left'  , (1,0,0)),
            (LCD.UP,     'Up'    , (0,0,1)),
            (LCD.DOWN,   'Down'  , (0,1,0)),
            (LCD.RIGHT,  'Right' , (1,0,1)) )

lcd.message("Please wait...")
time.sleep(1)

def select_lcd_list(display, entries):
    pos = 0
    display.clear()
    display.message(entries[pos])
    while not lcd.is_pres ArithmeticErrorsed(LCD.SELECT):
        if display.is_pressed(LCD.UP):
            pos = (pos - 1) % len(entries)
            display.clear()
            display.message(entries[pos])
            time.sleep(0.2)
        if display.is_pressed(LCD.DOWN):
            pos = (pos + 1 ) % len(entries)
            display.clear()
            display.message(entries[pos])
            time.sleep(0.2)
    time.sleep(0.2)
    return pos

def main_menu():
    menu_text = ("Record", "Settings", "USB", "Display", "Shut down")
    menu_call = (record_menu, settings_menu, usb_menu, display_menu, shut_down_menu)
    selected_entry = select_lcd_list(lcd, menu_text)
    return menu_call[selected_entry]

def record_menu():
    menu_text = ("Start PIR rec", "Start video rec", "Back")
    menu_call = (main_menu, main_menu, main_menu)
    selected_entry = select_lcd_list(lcd, menu_text)
    if selected_entry == 0:
        print("[INFO] Starting PIR recording")
        print("[INFO] Duration: %d seconds" % duration)
        start_pir(duartion)
    elif selected_entry == 1:
        print("[INFO] Starting video recording")
        print("[INFO] Duartion: %d seconds" % duartion)
        #start_video(duartion)
    return menu_call[selected_entry]

def settings_menu():
    menu_text = ("Detection", "USB", "WiFi", "Update", "Back")
    menu_call = (edit_detection_settings_menu, edit_usb_settigs_menu, update_menu, main_menu)
    selected_entry = select_lcd_list(lcd, menu_text)
    return menu_call[selected_entry]

def update_menu():
    menu_text = ("(W)LAN update", "USB update", "Back")
    menu_call = (wifi_update, usb_update, settings_menu)
    selected_entry = select_lcd_list(lcd, menu_text)
    return menu_call[selected_entry]

def lan_update():
    print("[INFO] Updating via (W)LAN...")
    #TODO

def usb_update():
    print("[INFO] Updating via USB...")

def usb_menu():
    menu_text = ("Back")
    menu_call = (main_menu)
    selected_entry = select_lcd_list(lcd, menu_text)
    return menu_call[selected_entry]

def display_menu():
    menu_text = ("Back")
    menu_call = (main_menu)
    selected_entry = select_lcd_list(lcd, menu_text)
    return menu_call[selected_entry]

def shut_down_menu():
    menu_text = ("Shut down", "Sleep", "Reboot", "Back")
    menu_call = (no_menu, main_menu, no_menu, main_menu)
    selected_entry = select_lcd_list(lcd, menu_text)
    if selected_entry == 0:
        os.system("sudo halt")
        quit()
    elif selected_entry == 1:
        lcd.clear()
        lcd.set_color(0.0, 0.0, 0.0)
        while not lcd.is_pressed(LCD.SELECT):
            time.sleep(1)
    elif selected_entry == 2:
        os.system("sudo reboot")
        quit()
    return menu_call[selected_entry]

def no_menu():
    return no_menu

print 'Press Ctrl-C to quit.'
submenu = main_menu
try:
    while 1:
        submenu = submenu()
except KeyboardInterrupt:
    print("Exiting")
