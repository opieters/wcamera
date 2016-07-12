#!/usr/bin/env python

# Example using a character LCD plate.
from os import system
from wifi import Cell, Scheme
from ui import UI
from core import Core

class Menu:

    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    space = [' ']
    symbols = []

    # Make list of button value, text, and backlight color.
    special_chars = [(1, ( 0, 4, 0,21, 0, 4, 0, 0)), # ALL CONTROLS
                     (2, ( 0, 4, 0, 4, 0, 4, 0, 0)), # UP, SELECT, DOWN
                     (3, [ 4, 4,31, 4, 4, 0,31, 0])] # PM

    def __init__(self,display,core):
        self.ui = UI(display,special_chars=self.special_chars)
        self.conf = core.conf
        self.core = core

    def main_menu(self):
        menu_text = ("Record", "Settings", "Server", "System")
        menu_call = (self.record_menu, self.settings_menu, self.server_menu, self.system_menu)
        selected_entry = self.ui.select_from_list(menu_text)
        return menu_call[selected_entry]

    def record_menu(self):
        menu_text = ("Start PIR rec", "Start video rec", "Back")
        selected_entry = self.ui.select_from_list(menu_text)
        if selected_entry == 0:
            self.ui.backlight(False)
            self.core.pir_recording()
            self.ui.backlight(True)
            # wait till button released
            while self.core.tmp["STOP_FN"](self.core.tmp["STOP_BT"]):
                pass
            return self.record_menu
        elif selected_entry == 1:
            self.core.video_recording()
            return self.record_menu
        return self.main_menu

    def settings_menu(self):
        menu_text = ("Detection", "WiFi", "Update", "Back")
        menu_call = (self.edit_detection_settings_menu, self.edit_wifi_menu, self.update_menu, self.main_menu)
        selected_entry = self.ui.select_from_list(menu_text)
        return menu_call[selected_entry]

    def edit_detection_settings_menu(self):
        # display all dict entries for editing
        self.ui.display_message("Select Done to\ncontinue")
        conf_items = ["Done and quit"] + list(self.conf.keys())
        selected = self.ui.select_from_list(conf_items,display_message="Select item",controls=False)
        while selected != 0:
            key = conf_items[selected]
            print(key)
            value = self.conf[key]
            if type(value) is bool:
                self.conf[key] = bool(self.ui.question(message="New %s value" % key))
            elif type(value) is int:
                self.conf[key] = int(self.ui.enter_text(message="New %s value" % key,chars=Menu.numbers))
            elif type(value) is str:
                self.conf[key] = self.ui.enter_text(message="New %s value" % key,chars=Menu.letters + Menu.numbers + Menu.symbols)
            elif type(value) is list:
                for i in range(len(value)):
                    value[i] = int(self.ui.enter_text(message="New %s[%d] value" % (key,i),chars=Menu.numbers))
            elif type(value) is float:
                self.conf[key] = float(self.ui.enter_text(message="New %s value" % key, chars=Menu.numbers + ['.']))
            selected = self.ui.select_from_list(conf_items,display_message="Select item",controls=False,pos=selected)
        self.core.check_conf()
        if self.ui.question("Save to file?",options=["Yes","No"]) == "Yes":
            core.save_conf()
        return self.settings_menu

    def edit_wifi_menu(self):
        # get all cells from the air
        menu_text = ("Current connection", "New connection", "Back")
        menu_call = (self.current_wifi_connection, self.new_wifi_connection, self.settings_menu)
        selected_entry = self.ui.select_from_list(menu_text)
        return menu_call[selected_entry]

    def current_wifi_connection(self):
        self.ui.display_message("Please wait...")
        message = "Connected" if self.core.check_connection() else "Not connected"
        self.ui.display_message(message)
        return self.edit_wifi_menu

    def new_wifi_connection(self):
        ssids = [cell.ssid for cell in Cell.all('wlan0')]
        if len(ssids) > 0:
            ssid = ssids[self.ui.select_from_list(ssids,display_message="Select SSID",controls=False)]
        pwd = self.ui.enter_text("Enter SSID pwd",Menu.space+Menu.letters+Menu.numbers+Menu.symbols)
        self.core.setup_wifi_connection(ssid,pwd)
        return self.edit_wifi_menu

    def update_menu(self):
        home_dir = self.conf["home"]
        message = "Updated" if self.core.update(home_dir) else "Update failed"
        self.ui.display_message(message)
        return self.settings_menu

    def usb_menu(self):
        self.ui.display_message("Do NOT yet connect\n USB device!",wait_for_input=1.5)
        self.core.before_usb_inserted()
        self.ui.display_message("Connect USB\ndevice NOW.")
        if self.core.copy_to_usb():
            self.ui.display_message("Success.")
        else:
            self.ui.display_message("Warning or Error\noccured.")
        return self.main_menu

    def server_menu(self):
        self.ui.display_message("Server init...\nPlease wait...",wait_for_input=False)
        self.core.start_server()
        self.ui.display_message("Server running\nPush SELECT to quit")
        print("STOP")
        self.core.stop_server()
        print("RET")
        return self.main_menu

    def system_menu(self):
        menu_text = ("Shut down", "Sleep", "Reboot", "Back")
        menu_call = (None, self.no_menu, None, self.main_menu)
        selected_entry = self.ui.select_from_list( menu_text)
        if selected_entry == 0:
            system("sudo halt")
            quit()
        elif selected_entry == 1:
            self.ui.wait_for_input()
        elif selected_entry == 2:
            system("sudo reboot")
            quit()
        return menu_call[selected_entry]

    def no_menu(self):
        return self.no_menu
