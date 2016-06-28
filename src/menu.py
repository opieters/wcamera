#!/usr/bin/env python

# Example using a character LCD plate.
import math, time, json, PIR, motion_detector
import Adafruit_CharLCD as LCD
from os import system
from wifi import Cell, Scheme
from ui import UI
from core import Core

class Menu:

    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    space = [' ']
    symbols = []
    conf_file = "conf.json"

    # Make list of button value, text, and backlight color.
    special_chars = [(1, ( 0, 4, 0,21, 0, 4, 0, 0)), # ALL CONTROLS
                     (2, ( 0, 4, 0, 4, 0, 4, 0, 0)), # UP, SELECT, DOWN
                     (3, [ 4, 4,31, 4, 4, 0,31, 0])] # PM

    @staticmethod
    def init(display,conf_file):
        UI.init(display,special_chars=Menu.special_chars)
        Menu.conf_file = conf_file
        Menu.conf = json.load(open(Menu.conf_file))

    @staticmethod
    def main_menu():
        menu_text = ("Record", "Settings", "Display", "System")
        menu_call = (Menu.record_menu, Menu.settings_menu, Menu.display_menu, Menu.system_menu)
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
        menu_text = ("Detection", "WiFi", "Update", "Back")
        menu_call = (Menu.edit_detection_settings_menu, Menu.edit_wifi_menu, Menu.update_menu, Menu.main_menu)
        selected_entry = UI.select_from_list(menu_text)
        return menu_call[selected_entry]

    @staticmethod
    def edit_detection_settings_menu():
        # display all dict entries for editing
        UI.display_message("Select Done to\ncontinue")
        conf_items = ["Done and quit"] + list(Menu.conf.keys())
        selected = UI.select_from_list(conf_items,display_message="Select item",controls=False)
        while selected != 0:
            key = conf_items[selected]
            print(key)
            value = Menu.conf[key]
            if type(value) is bool:
                Menu.conf[key] = bool(UI.question(message="New %s value" % key))
            elif type(value) is int:
                Menu.conf[key] = int(UI.enter_text(message="New %s value" % key,chars=Menu.numbers))
            elif type(value) is str:
                Menu.conf[key] = UI.enter_text(message="New %s value" % key,chars=Menu.letters + Menu.numbers + Menu.symbols)
            elif type(value) is list:
                for i in range(len(value)):
                    value[i] = int(UI.enter_text(message="New %s[%d] value" % (key,i),chars=Menu.numbers))
            elif type(value) is float:
                Menu.conf[key] = float(UI.enter_text(message="New %s value" % key, chars=Menu.numbers + ['.']))
            selected = UI.select_from_list(conf_items,display_message="Select item",controls=False,pos=selected)
        if UI.question("Save to file?",options=["Yes","No"]) == "Yes":
            with open(conf_file,'w') as f:
                f.write(json.dump(Menu.conf))
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
        UI.display_message("Please wait...")
        message = "Connected" if Core.check_connection() else "Not connected"
        UI.display_message(message)
        return Menu.edit_wifi_menu

    @staticmethod
    def new_wifi_connection():
        ssids = [cell.ssid for cell in Cell.all('wlan0')]
        if len(ssids) > 0:
            ssid = ssids[UI.select_from_list(ssids,display_message="Select SSID",controls=False)]
        pwd = UI.enter_text("Enter SSID pwd",Menu.space+Menu.letters+Menu.numbers+Menu.symbols)
        Core.setup_wifi_connection(ssid,pwd)
        return Menu.edit_wifi_menu

    @staticmethod
    def update_menu():
        home_dir = Menu.conf["home"]
        message = "Updated" if Core.update(home_dir) else "Update failed"
        UI.display_message(message)
        return Menu.settings_menu

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
