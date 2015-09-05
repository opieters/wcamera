#!/usr/bin/python
# Example using a character LCD plate.
import math
import time
import os
import json
import PIR
import motion_detector

import Adafruit_CharLCD as LCD

# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()

# create some custom characters
#lcd.create_char(1, [0, 8,12,14,12, 8, 0, 0]) # arrow to right
#lcd.create_char(2, [0, 2, 6,14, 6, 2, 0, 0]) # arrowhead to left
#lcd.create_char(3, [0, 0, 4,14,31, 0, 0, 0]) # arrowhead up
#lcd.create_char(4, [0, 0,31,14, 4, 0, 0, 0]) # arrowhead down
#lcd.create_char(5, [0,14,31,27,31,14, 0, 0]) # select

lcd.set_color(1.0, 1.0, 1.0)
lcd.clear()

conf_file = "conf.json"

# Make list of button value, text, and backlight color.
lcd.create_char(1, [ 0, 4, 0,21, 0, 4, 0, 0]) # ALL CONTROLS (SMALL)
lcd.create_char(2, [ 0, 4, 0, 4, 0, 4, 0, 0]) # only up/down/select
lcd.create_char(3, [ 4, 4,31, 4, 4, 0,31, 0]) # PM





lcd.message("Please wait...")
time.sleep(1)

def select_lcd_list(display, entries):
    pos = 0
    controls = "\x02"
    display.clear()
    display.message(entries[pos] + "\n" + controls)
    while not lcd.is_pressed(LCD.SELECT):
        if display.is_pressed(LCD.UP):
            pos = (pos - 1) % len(entries)
            display.clear()
            display.message(entries[pos] + "\n" + controls)
            time.sleep(0.2)
        if display.is_pressed(LCD.DOWN):
            pos = (pos + 1 ) % len(entries)
            display.clear()
            display.message(entries[pos] + "\n" + controls)
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
        PIR.init()
        PIR.run()
        print("[INFO] Deleting objects")
        PIR.delete()
    elif selected_entry == 1:
        print("[INFO] Starting video recording")
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

def edit_usb_settigs_menu():
    return settings_menu

def edit_detection_settings_menu():
    # load configuration file
    conf = json.load(open(conf_file))
    keys_text = tuple([k for k in conf] + ["Back"])

    # initial loop over entries
    edit_key = select_lcd_list(lcd, keys_text)
    
    while keys_text[edit_key] != "Back":
        cursor = 0 # cursor default position
        data = conf[keys_text[edit_key]] # extract data

        # list type
        if type(data) is list:
            # display cursor
            lcd.show_cursor(True)

            # display initial data
            lcd.clear()
            lcd.message(str(data) + '\n\x01 Edit: ' + str(data[cursor]))

            # wait for select (=OK) signal
            while not lcd.is_pressed(LCD.SELECT):
                # change character
                if lcd.is_pressed(LCD.UP):
                    data[cursor] += 1
                    lcd.clear()
                    lcd.message(str(data) + '\n\x01 Edit: ' + str(data[cursor])) 
                    time.sleep(0.2)
                if lcd.is_pressed(LCD.DOWN):
                    data[cursor] -= 1
                    lcd.clear()
                    lcd.message(str(data) + '\n\x01 Edit: ' + str(data[cursor]))
                    time.sleep(0.2)
                # change cursor position
                if lcd.is_pressed(LCD.RIGHT):
                    if cursor < (len(data)-1):
                        cursor += 1
                        lcd.clear()
                        lcd.message(str(data) + '\n\x01 Edit: ' + str(data[cursor]))
                    time.sleep(0.2)
                if lcd.is_pressed(LCD.LEFT):
                    if cursor > 0:
                        cursor -= 1
                        lcd.clear()
                        lcd.message(str(data) + '\n\x01 Edit: ' + str(data[cursor]))
                    time.sleep(0.2)
            time.sleep(0.2)            

        # string data
        if type(data) is str:

            # display cursor
            lcd.show_cursor(True)

            # string edit options
            min_char_value = 32
            max_char_value = 126

            # help string with controls
            controls = "\x01"

            # display initial data
            lcd.clear()
            lcd.message(data + "\n" + controls)

            # wait for select (=OK) signal
            while not lcd.is_pressed(LCD.SELECT):
                # change character
                if lcd.is_pressed(LCD.UP):
                    if ord(data[cursor]) < max_char_value:
                        data[cursor] = chr(ord(data[cursor]) + 1)
                    else:
                        data[cursor] = min_char_value
                        lcd.clear()
                        lcd.message(data + "\n" + controls)
                    time.sleep(0.2)
                if lcd.is_pressed(LCD.DOWN):
                    if ord(data[cursor]) > min_char_value:
                        data[cursor] = chr(ord(data[cursor]) - 1)
                    else:
                        data[cursor] = max_char_value
                    time.sleep(0.2)
                # change cursor position
                if lcd.is_pressed(LCD.RIGHT):
                    cursor += 1
                    # if cursor moves out of string -> insert new character
                    if cursor >= len(data):
                        data += " "
                    lcd.set_cursor(cursor,1)
                    time.sleep(0.2)
                if lcd.is_pressed(LCD.LEFT):
                    if cursor > 0:
                        cursor -= 1
                        lcd.set_cursor(cursor,1)
                    time.sleep(0.2)
                print 'one more'
            data = data.strip() # remove redundant whitespace
            time.sleep(0.2)

        # bool data
        if type(data) is bool:
            controls = "\x02"

            lcd.clear()
            lcd.message(str(data) + "\n" + controls)

            # wait for select
            while not lcd.is_pressed(LCD.SELECT):
                if lcd.is_pressed(LCD.UP) or lcd.is_pressed(LCD.DOWN):
                    data = not data
                    lcd.clear()
                    lcd.message(str(data) + "\n" + controls)
                    time.sleep(0.2)
            time.sleep(0.2)

        # numerical type (float or int)
        if type(data) is int or type(data) is float:
            # define type specific options and help string (indicates step size!)
            if type(data) is float:
                step = 1.0
                controls = "\x01\x03%f" % step
            else:
                step = 1
                controls = "\x01\x03%d" % step
            # wait for select
            while not lcd.is_pressed(LCD.SELECT):
                # change value by step size
                if lcd.is_pressed(LCD.UP):
                    data += step
                    lcd.clear()
                    lcd.message(str(data) + "\n" + controls)
                    time.sleep(0.2)
                if lcd.is_pressed(LCD.DOWN):
                    data -= step
                    lcd.clear()
                    lcd.message(str(data) + "\n" + controls)
                    time.sleep(0.2)

                # change step size (and update `controls`)
                if lcd.is_pressed(LCD.RIGHT):
                    step /= 10
                    if type(data) is int:
                        step = max(step,1)
                        controls = "\x01\x03%d" % step
                    else:
                        controls = "\x01\x03%f" % step
                    lcd.clear()
                    lcd.message(str(data) + "\n" + controls)
                    time.sleep(0.2)
                if lcd.is_pressed(LCD.LEFT):
                    step *=10
                    if type(data) is int:
                        controls = "\x01\x03%d" % step
                    else:
                        controls = "\x01\x03%f" % step
                    lcd.clear()
                    lcd.message(str(data) + "\n" + controls)
                    time.sleep(0.2)
            time.sleep(0.2)

        # hide cursor in other menus
        lcd.show_cursor(False)

        # get new edit entry
        edit_key = select_lcd_list(lcd, keys_text)
        time.sleep(0.2)
    return settings_menu


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
