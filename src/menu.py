#!/usr/bin/env python

# Example using a character LCD plate.
import math, time, json, PIR, motion_detector, urllib2
import Adafruit_CharLCD as LCD
from os import system
from wifi import Cell, Scheme
from ui import UI

class Menu:

    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    space = [' ']
    symbols = []

    # Make list of button value, text, and backlight color.
    special_chars = [(1, ( 0, 4, 0,21, 0, 4, 0, 0)), # ALL CONTROLS
                     (2, ( 0, 4, 0, 4, 0, 4, 0, 0)), # UP, SELECT, DOWN
                     (3, [ 4, 4,31, 4, 4, 0,31, 0])] # PM

    @staticmethod
    def init(display):
        UI.init(display,special_chars=Menu.special_chars)

    @staticmethod
    def main_menu():
        menu_text = ("Record", "Settings", "USB", "Display", "System")
        menu_call = (Menu.record_menu, Menu.settings_menu, Menu.usb_menu, Menu.display_menu, Menu.system_menu)
        selected_entry = UI.select_from_list(menu_text)
        return menu_call[selected_entry]

    @staticmethod
    def record_menu():
        menu_text = ("Start PIR rec", "Start video rec", "Back")
        selected_entry = UI.select_from_list(menu_text)
        if selected_entry == 0:
            print("[INFO] Starting PIR recording.")
            PIR.init()
            PIR.run()
            PIR.delete()
            print("[INFO] PIR recording ended.")
            return Menu.record_menu
        elif selected_entry == 1:
            print("[INFO] Starting video recording")
            #TODO
            return Menu.record_menu
        return Menu.main_menu

    @staticmethod
    def settings_menu():
        menu_text = ("Detection", "USB", "WiFi", "Update", "Back")
        menu_call = (Menu.edit_detection_settings_menu, Menu.edit_usb_settigs_menu, Menu.edit_wifi_menu, Menu.update_menu, Menu.main_menu)
        selected_entry = UI.select_from_list(menu_text)
        return menu_call[selected_entry]

    @staticmethod
    def edit_detection_settings_menu():
        # load configuration file
        conf = json.load(open(conf_file))
        keys_text = tuple([k for k in conf] + ["Back"])

        # initial loop over entries
        edit_key = UI.select_from_list(keys_text)

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
            edit_key = UI.select_from_list( keys_text)
            time.sleep(0.2)
        return Menu.settings_menu

    @staticmethod
    def edit_usb_settigs_menu():
        return Menu.settings_menu

    @staticmethod
    def edit_wifi_menu():
        # get all cells from the air
        menu_text = ("Current connection", "New connection", "Back")
        menu_call = (Menu.current_wifi_connection, Menu.new_wifi_connection, Menu.settings_menu)
        selected_entry = UI.select_from_list(menu_text)
        return menu_call[selected_entry]

    @staticmethod
    def current_wifi_connection():
        try:
            response = urllib2.urlopen("http://www.ugent.be",timeout=1)
            message = "Connected."
        except urllib2.URLError:
            message = "Not connected."
        display_message(display, message)
        return Menu.edit_wifi_menu

    @staticmethod
    def new_wifi_connection():
        ssids = [cell.ssid for cell in Cell.all('wlan0')]
        ssid = ssids[UI.select_from_list(ssids,display_message="Select SSID",display_controls=False)]
        enter_text(display,message,pwd_chars)
        return Menu.edit_wifi_menu

    @staticmethod
    def update_menu():
        menu_text = ("(W)LAN update", "USB update", "Back")
        menu_call = (Menu.lan_update, Menu.usb_update, Menu.settings_menu)
        selected_entry = UI.select_from_list( menu_text)
        return menu_call[selected_entry]

    @staticmethod
    def lan_update():
        print("[INFO] Updating via (W)LAN...")
        #TODO

    def usb_update():
        print("[INFO] Updating via USB...")

    @staticmethod
    def usb_menu():
        menu_text = ("Back",)
        menu_call = (Menu.main_menu,)
        selected_entry = UI.select_from_list(menu_text)
        return menu_call[selected_entry]

    @staticmethod
    def display_menu():
        menu_text = ("Back",)
        menu_call = (Menu.main_menu,)
        selected_entry = UI.select_from_list(menu_text)
        return menu_call[selected_entry]

    @staticmethod
    def system_menu():
        menu_text = ("Shut down", "Sleep", "Reboot", "Back")
        menu_call = (None, Menu.no_menu, None, Menu.main_menu)
        selected_entry = UI.select_from_list( menu_text)
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

    @staticmethod
    def no_menu():
        return Menu.no_menu
