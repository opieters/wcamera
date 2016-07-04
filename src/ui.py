#!/usr/bin/env python

# Example using a character LCD plate.
import math, time, json, PIR, motion_detector, urllib2
import Adafruit_CharLCD as LCD
from os import system
from wifi import Cell, Scheme

class UI:

    def __init__(self,display,special_chars):
        self.display = display
        if special_chars is not None:
            for char in special_chars:
                self.display.create_char(char[0], char[1])

    def select_from_list(self,entries, pos=0, display_message="", controls=True):
        if len(entries) == 0:
            print("[ERR] List without entries was provided.")
            return -1
        controls = "\x02"
        self.display.clear()
        if controls:
            self.display.message(entries[pos] + "\n" + controls)
        else:
            self.display.message(display_message + "\n" + entries[pos])
        while not self.display.is_pressed(LCD.SELECT):
            if self.display.is_pressed(LCD.UP):
                pos = (pos - 1) % len(entries)
                self.display.clear()
                if controls:
                    self.display.message(entries[pos] + "\n" + controls)
                else:
                    self.display.message(display_message + "\n" + entries[pos])
                time.sleep(0.2)
            if self.display.is_pressed(LCD.DOWN):
                pos = (pos + 1 ) % len(entries)
                self.display.clear()
                if controls:
                    self.display.message(entries[pos] + "\n" + controls)
                else:
                    self.display.message(display_message + "\n" + entries[pos])
                time.sleep(0.2)
        time.sleep(0.2)
        return pos

    def display_message(self,message,wait_for_input=True):
        self.display.clear()
        self.display.message(message)
        if type(wait_for_input) is bool:
            while not self.display.is_pressed(LCD.SELECT) and wait_for_input:
                time.sleep(0.05)
        elif type(wait_for_input) is float or type(wait_for_input) is int:
            time.sleep(wait_for_input)
        time.sleep(0.2)

    def question(self,message,options=["True","False"],pos=0):
        self.display.clear()
        self.display.message(message + "\n" + str(options[pos]))
        while not self.display.is_pressed(LCD.SELECT):
            if self.display.is_pressed(LCD.UP):
                pos = (pos-1) % len(options)
                self.display.clear()
                self.display.message(message + "\n" + options[pos])
                time.sleep(0.2)
            if self.display.is_pressed(LCD.DOWN):
                pos = (pos+1) % len(options)
                self.display.clear()
                self.display.message(message + "\n" + options[pos])
                time.sleep(0.2)
        time.sleep(0.2)
        return pos

    def enter_text(self,message,chars,limit=None):
        # add a null character that is removed afterwards
        if ' ' not in chars:
            chars = [' '] + chars

        self.display.show_cursor(True)  # always display cursor for current position
        current_char_idx = 0       # current position in chars list
        cursor = 0                 # cursor position
        text = [chars[current_char_idx]] # submitted text (list of individual chars)
        draw_from, draw_to = 0, self.display._cols # bounds that text is displayed

        # self.display text
        self.display.clear()
        self.display.message(message + "\n" + ''.join(text)[draw_from:min(draw_to,len(text))])
        self.display.set_cursor(cursor, 1)

        # wait until SELECT pressed -> done
        while not self.display.is_pressed(LCD.SELECT):
            if self.display.is_pressed(LCD.RIGHT):
                # add character if needed
                if cursor == (len(text)-1):
                    if limit is None or cursor < max(limit-1,0):
                        text.append(chars[0])
                    else:
                        continue

                cursor += 1 # update cursor
                # update self.display bounds
                draw_to = max(draw_to,cursor+1)
                draw_from = draw_to - self.display._cols
                # update message
                self.display.clear()
                self.display.message(message + "\n" + ''.join(text)[draw_from:min(draw_to,len(text))])
                self.display.set_cursor(cursor, 1)
                time.sleep(0.2)
            if self.display.is_pressed(LCD.LEFT) and cursor > 0:
                cursor -= 1 # update cursor
                # update self.display bounds
                draw_from = min(cursor, draw_from)
                draw_to = draw_from + self.display._cols
                # update message
                self.display.clear()
                self.display.message(message + "\n" + ''.join(text)[draw_from:min(draw_to,len(text))])
                self.display.set_cursor(cursor, 1)
                time.sleep(0.2)
            if self.display.is_pressed(LCD.UP):
                current_char_idx = (chars.index(text[cursor])+1) % len(chars) # change selected charcter index
                text[cursor] = chars[current_char_idx] # update text
                # update message
                self.display.clear()
                self.display.message(message + "\n" + ''.join(text)[draw_from:min(draw_to,len(text))])
                self.display.set_cursor(cursor, 1)
                time.sleep(0.2)
            if self.display.is_pressed(LCD.DOWN):
                current_char_idx = (chars.index(text[cursor])-1) % len(chars) # change selected charcter index
                text[cursor] = chars[current_char_idx] # update text
                # update message
                self.display.clear()
                self.display.message(message + "\n" + ''.join(text)[draw_from:min(draw_to,len(text))])
                self.display.set_cursor(cursor, 1)
                time.sleep(0.2)

        self.display.show_cursor(False) # stop displaying cursor, needed because others assume cursor is off
        time.sleep(0.2)
        return ''.join(text).strip() # remove whitespace

    def wait_for_input(self):
        self.display.clear()
        self.display.set_color(0.0, 0.0, 0.0)
        while not self.display.is_pressed(self.display.SELECT):
            time.sleep(1)
