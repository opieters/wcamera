#!/usr/bin/env python

# Example using a character LCD plate.
import math, time, json, PIR, motion_detector, urllib2
import Adafruit_CharLCD as LCD
from os import system
from wifi import Cell, Scheme

class UI:
    display = None

    @staticmethod
    def init(display,special_chars):
        UI.display = display
        if special_chars is not None:
            for char in special_chars:
                UI.display.create_char(char[0], char[1])

    @staticmethod
    def select_from_list(entries, pos=0, display_message="", controls=True):
        controls = "\x02"
        UI.display.clear()
        if controls:
            UI.display.message(entries[pos] + "\n" + controls)
        else:
            UI.display.message(display_message + "\n" + entries[pos])
        while not UI.display.is_pressed(LCD.SELECT):
            if UI.display.is_pressed(LCD.UP):
                pos = (pos - 1) % len(entries)
                UI.display.clear()
                if controls:
                    UI.display.message(entries[pos] + "\n" + controls)
                else:
                    UI.display.message(display_message + "\n" + entries[pos])
                time.sleep(0.2)
            if UI.display.is_pressed(LCD.DOWN):
                pos = (pos + 1 ) % len(entries)
                UI.display.clear()
                if controls:
                    UI.display.message(entries[pos] + "\n" + controls)
                else:
                    UI.display.message(display_message + "\n" + entries[pos])
                time.sleep(0.2)
        time.sleep(0.2)
        return pos

    @staticmethod
    def display_message(message):
        UI.display.clear()
        while not UI.display.is_pressed(LCD.SELECT):
            pass

    @staticmethod
    def question(message,options=["True","False"],pos=0):
        UI.display.clear()
        dispay.message(message + "\n" + str(options[pos]))
        while not dispay.is_pressed(LCD.SELECT):
            if UI.display.is_pressed(LCD.UP):
                pos = (pos-1) % len(options)
                UI.display.clear()
                UI.display.message(message + "\n" + options[pos])
            if UI.display.is_pressed(LCD.DOWN):
                pos = (pos+1) % len(options)
                UI.display.clear()
                UI.display.message(message + "\n" + options[pos])
        return pos

    @staticmethod
    def enter_text(message,chars,limit=None):
        # add a null character that is removed afterwards
        if ' ' not in chars:
            chars = [' '] + chars

        UI.display.show_cursor(True)  # always display cursor for current position
        current_char_idx = 0       # current position in chars list
        cursor = 0                 # cursor position
        text = [chars[current_char_idx]] # submitted text (list of individual chars)
        draw_from, draw_to = 0, UI.display._cols # bounds that text is displayed

        # UI.display text
        UI.display.clear()
        UI.display.message(message + "\n" + ''.join(text)[draw_from:min(draw_to,len(text))])
        UI.display.set_cursor(cursor, 1)

        # wait until SELECT pressed -> done
        while not UI.display.is_pressed(LCD.SELECT):
            if UI.display.is_pressed(LCD.RIGHT):
                # add character if needed
                if cursor == (len(text)-1):
                    if limit is None or cursor < max(limit-1,0):
                        text.append(chars[current_char_idx])
                    else:
                        continue

                cursor += 1 # update cursor
                # update UI.display bounds
                draw_to = max(draw_to,cursor+1)
                draw_from = draw_to - UI.display._cols
                # update message
                UI.display.clear()
                UI.display.message(message + "\n" + ''.join(text)[draw_from:min(draw_to,len(text))])
                UI.display.set_cursor(cursor, 1)
            if UI.display.is_pressed(LCD.LEFT) and cursor > 0:
                cursor -= 1 # update cursor
                # update UI.display bounds
                draw_from = min(cursor, draw_from)
                draw_to = draw_from + UI.display._cols
                # update message
                UI.display.clear()
                UI.display.message(message + "\n" + ''.join(text)[draw_from:min(draw_to,len(text))])
                UI.display.set_cursor(cursor, 1)
            if UI.display.is_pressed(LCD.UP):
                current_char_idx = (current_char_idx+1) % len(chars) # change selected charcter index
                text[cursor] = chars[current_char_idx] # update text
                # update message
                UI.display.clear()
                UI.display.message(message + "\n" + ''.join(text)[draw_from:min(draw_to,len(text))])
                UI.display.set_cursor(cursor, 1)
            if UI.display.is_pressed(LCD.DOWN):
                current_char_idx = (current_char_idx-1) % len(chars) # change selected charcter index
                text[cursor] = chars[current_char_idx] # update text
                # update message
                UI.display.clear()
                UI.display.message(message + "\n" + ''.join(text)[draw_from:min(draw_to,len(text))])
                UI.display.set_cursor(cursor, 1)

        UI.display.show_cursor(False) # stop displaying cursor, needed because others assume cursor is off
        return ''.join(text).strip() # remove whitespace
