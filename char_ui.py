#!/usr/bin/env python

# Example using a character LCD plate.
import math, time, json, PIR, motion_detector
import Adafruit_CharLCD as LCD
from os import system

"""Defines all character display related variables and functions."""

# Make list of button value, text, and backlight color.
special_chars = [(1, ( 0, 4, 0,21, 0, 4, 0, 0)), # ALL CONTROLS
                 (2, ( 0, 4, 0, 4, 0, 4, 0, 0)), # UP, SELECT, DOWN
                 (3, [ 4, 4,31, 4, 4, 0,31, 0])] # PM

def select_lcd_list(display, entries):
    pos = 0
    controls = "\x02"
    display.clear()
    display.message(entries[pos] + "\n" + controls)
    while not display.is_pressed(LCD.SELECT):
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

def main_menu(display):
    menu_text = ("Record", "Settings", "USB", "Display", "System")
    menu_call = (record_menu, settings_menu, usb_menu, display_menu, system_menu)
    selected_entry = select_lcd_list(display, menu_text)
    return menu_call[selected_entry]

def record_menu(display):
    menu_text = ("Start PIR rec", "Start video rec", "Back")
    selected_entry = select_lcd_list(display, menu_text)
    if selected_entry == 0:
        print("[INFO] Starting PIR recording.")
        PIR.init()
        PIR.run()
        PIR.delete()
        print("[INFO] PIR recording ended.")
        return record_menu
    elif selected_entry == 1:
        print("[INFO] Starting video recording")
        #TODO
        return record_menu
    return main_menu

def settings_menu(display):
    menu_text = ("Detection", "USB", "WiFi", "Update", "Back")
    menu_call = (edit_detection_settings_menu, edit_usb_settigs_menu, update_menu, main_menu)
    selected_entry = select_lcd_list(display, menu_text)
    return menu_call[selected_entry]

def edit_detection_settings_menu(display):
    # load configuration file
    conf = json.load(open(conf_file))
    keys_text = tuple([k for k in conf] + ["Back"])

    # initial loop over entries
    edit_key = select_lcd_list(display, keys_text)

    while keys_text[edit_key] != "Back":
        cursor = 0 # cursor default position
        data = conf[keys_text[edit_key]] # extract data

        # list type
        if type(data) is list:
            # display cursor
            display.show_cursor(True)

            # display initial data
            display.clear()
            display.message(str(data) + '\n\x01 Edit: ' + str(data[cursor]))

            # wait for select (=OK) signal
            while not display.is_pressed(LCD.SELECT):
                # change character
                if display.is_pressed(LCD.UP):
                    data[cursor] += 1
                    display.clear()
                    display.message(str(data) + '\n\x01 Edit: ' + str(data[cursor]))
                    time.sleep(0.2)
                if display.is_pressed(LCD.DOWN):
                    data[cursor] -= 1
                    display.clear()
                    display.message(str(data) + '\n\x01 Edit: ' + str(data[cursor]))
                    time.sleep(0.2)
                # change cursor position
                if display.is_pressed(LCD.RIGHT):
                    if cursor < (len(data)-1):
                        cursor += 1
                        display.clear()
                        display.message(str(data) + '\n\x01 Edit: ' + str(data[cursor]))
                    time.sleep(0.2)
                if display.is_pressed(LCD.LEFT):
                    if cursor > 0:
                        cursor -= 1
                        display.clear()
                        display.message(str(data) + '\n\x01 Edit: ' + str(data[cursor]))
                    time.sleep(0.2)
            time.sleep(0.2)

        # string data
        if type(data) is str:

            # display cursor
            display.show_cursor(True)

            # string edit options
            min_char_value = 32
            max_char_value = 126

            # help string with controls
            controls = "\x01"

            # display initial data
            display.clear()
            display.message(data + "\n" + controls)

            # wait for select (=OK) signal
            while not display.is_pressed(LCD.SELECT):
                # change character
                if display.is_pressed(LCD.UP):
                    if ord(data[cursor]) < max_char_value:
                        data[cursor] = chr(ord(data[cursor]) + 1)
                    else:
                        data[cursor] = min_char_value
                        display.clear()
                        display.message(data + "\n" + controls)
                    time.sleep(0.2)
                if display.is_pressed(LCD.DOWN):
                    if ord(data[cursor]) > min_char_value:
                        data[cursor] = chr(ord(data[cursor]) - 1)
                    else:
                        data[cursor] = max_char_value
                    time.sleep(0.2)
                # change cursor position
                if display.is_pressed(LCD.RIGHT):
                    cursor += 1
                    # if cursor moves out of string -> insert new character
                    if cursor >= len(data):
                        data += " "
                    display.set_cursor(cursor,1)
                    time.sleep(0.2)
                if display.is_pressed(LCD.LEFT):
                    if cursor > 0:
                        cursor -= 1
                        display.set_cursor(cursor,1)
                    time.sleep(0.2)
                print 'one more'
            data = data.strip() # remove redundant whitespace
            time.sleep(0.2)

        # bool data
        if type(data) is bool:
            controls = "\x02"

            display.clear()
            display.message(str(data) + "\n" + controls)

            # wait for select
            while not display.is_pressed(LCD.SELECT):
                if display.is_pressed(LCD.UP) or display.is_pressed(LCD.DOWN):
                    data = not data
                    display.clear()
                    display.message(str(data) + "\n" + controls)
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
            while not display.is_pressed(LCD.SELECT):
                # change value by step size
                if display.is_pressed(LCD.UP):
                    data += step
                    display.clear()
                    display.message(str(data) + "\n" + controls)
                    time.sleep(0.2)
                if display.is_pressed(LCD.DOWN):
                    data -= step
                    display.clear()
                    display.message(str(data) + "\n" + controls)
                    time.sleep(0.2)

                # change step size (and update `controls`)
                if display.is_pressed(LCD.RIGHT):
                    step /= 10
                    if type(data) is int:
                        step = max(step,1)
                        controls = "\x01\x03%d" % step
                    else:
                        controls = "\x01\x03%f" % step
                    display.clear()
                    display.message(str(data) + "\n" + controls)
                    time.sleep(0.2)
                if display.is_pressed(LCD.LEFT):
                    step *=10
                    if type(data) is int:
                        controls = "\x01\x03%d" % step
                    else:
                        controls = "\x01\x03%f" % step
                    display.clear()
                    display.message(str(data) + "\n" + controls)
                    time.sleep(0.2)
            time.sleep(0.2)

        # hide cursor in other menus
        display.show_cursor(False)

        # get new edit entry
        edit_key = select_lcd_list(display, keys_text)
        time.sleep(0.2)
    return settings_menu

def edit_usb_settigs_menu(display):
    return settings_menu

def update_menu(display):
    menu_text = ("(W)LAN update", "USB update", "Back")
    menu_call = (lan_update, usb_update, settings_menu)
    selected_entry = select_lcd_list(display, menu_text)
    return menu_call[selected_entry]

def lan_update(display):
    print("[INFO] Updating via (W)LAN...")
    #TODO

def usb_update(display):
    print("[INFO] Updating via USB...")

def usb_menu(display):
    menu_text = ("Back")
    menu_call = (main_menu)
    selected_entry = select_lcd_list(display, menu_text)
    return menu_call[selected_entry]

def display_menu(display):
    menu_text = ("Back")
    menu_call = (main_menu)
    selected_entry = select_lcd_list(display, menu_text)
    return menu_call[selected_entry]

def system_menu(display):
    menu_text = ("Shut down", "Sleep", "Reboot", "Back")
    menu_call = (None, no_menu, None, main_menu)
    selected_entry = select_lcd_list(display, menu_text)
    if selected_entry == 0:
        system("sudo halt")
        quit()
    elif selected_entry == 1:
        display.clear()
        display.set_color(0.0, 0.0, 0.0)
        while not display.is_pressed(display.SELECT):
            time.sleep(1)
    elif selected_entry == 2:
        system("sudo reboot")
        quit()
    return menu_call[selected_entry]

def no_menu():
    return no_menu
