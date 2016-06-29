#!/usr/bin/env python

import RPi.GPIO as GPIO
import time, datetime, json, os
from picamera import PiCameraError
from threading import Timer
from argparse import ArgumentParser

class PIR:

    def __init__(self,camera,conf):
        """Initialise module for recording with configuration file_conf or
        conf.json if unspecified.
        """
        self.camera = camera
        self.conf = conf

        self.run_complete = False
        self.motion = False
        self.recording = False
        self.record_video = self.conf["record video"]
        self.run_timer = None
        self.motion_timer =  None
        self.duration = None

        # set configuration of camera
        self.camera.resolution = tuple(self.conf["resolution"])
        self.camera.led = self.conf["camera LED"]

    def motion_detected(self,file_name):
        """Callback if motion is detected. A video or still image will be created
        with name file_name.
        """

        print("[INFO] Motion detected")

        self.motion = True

        # if video file requested and not already recording, start recording
        if (not self.recording) and self.record_video:
            self.camera.start_recording(file_name)
            self.recording = True

            print("[INFO] Start recording" + file_name)

        # capture still image
        elif not self.record_video:
            self.camera.capture(file_name)

            print("[INFO] Capture frame " + file_name)


    def no_motion(self):
        """Callback if motion ended."""

        print("[INFO] Motion ended")

        self.motion = False

        if self.record_video:
            # cancel already running timer if needed
            if self.motion_timer is not None:
                self.motion_timer.cancel()

            self.motion_timer = Timer(self.conf["motion delay"], self.stop_recording).start()

    def stop_recording(self):
        """Stops camera recording (if in progress)."""


        if (not self.motion) and self.recording:
            self.camera.stop_recording()
            self.recording = False

            print("[INFO] Recording stopped.")

    def pir_event(self,pin):
        """PIR GPIO event callback."""

        if GPIO.input(pin): # rising
            if self.record_video:
                self.motion_detected(os.path.join(self.conf["directory"], "motion-" + datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".h264"))
            else:
                self.motion_detected(self.conf["directory"] + "motion-" + datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + "-%dx%d.jpg" % (self.conf["resolution"][0], self.conf["resolution"][1]))
        else: # falling
            self.no_motion()

    def run_timer_callback(self):
        """Callback to end motion detection after conf["duration"] seconds"""

        # stop recording
        self.run_complete = True

        print("[INFO] Run timer callback: stop recording")

    def run(self,duration=None):
        """Perform motion detecton."""

        GPIO.setup(self.conf["PIR GPIO pin"], GPIO.IN) # register GPIO pin

        self.run_complete = False # run flag

        # load duration from config file if needed
        if duration is None:
            self.duration = self.conf["duration"]
        else:
            self.duration = duration

        # stop recording after specified time if needed
        if self.duration > 0:
            self.run_timer = Timer(self.duration, self.run_timer_callback)
            self.run_timer.start()

        # start recording, if KeyboardInterrupt stop execution (for debugging)
        try:
            print("[INFO] Press CTRL-C to exit run function prematurely")
            time.sleep(1)

            GPIO.add_event_detect(self.conf["PIR GPIO pin"], GPIO.BOTH, callback=self.pir_event)

            # configure exit button if configured
            if self.conf["stop detection GPIO pin"] >= 0:
                print("[INFO] Detection GPIO pin active")
                GPIO.setup(self.conf["stop detection GPIO pin"], GPIO.IN)
                GPIO.add_event_detect(self.conf["stop detection GPIO pin"], GPIO.BOTH, callback=self.run_timer_callback)

            # keep function alive and check every 3 seconds if the script needs to stop
            while not self.run_complete:
                time.sleep(3)

        except KeyboardInterrupt:
            print("[INFO] Motion detection ended.")
        except PiCameraError:
            print("[ERROR] Camera error... Stopped detection.")

    def delete(self):
        """Release all nessesary veriables and stop timers."""

        # if camera is still recording, stop it before deallocation
        if self.camera.recording:
            self.camera.stop_recording()
            print('[INFO] Stopped recording.')

        if self.run_timer is not None:
            self.run_timer.cancel()
            self.run_timer.join()
            print('[INFO] Cancelled run timer.')

        if self.motion_timer is not None:
            self.motion_timer.cancel()
            self.motion_timer.join()
            print('[INFO] Cancelled motion timer.')

        # clean GPIO pins
        GPIO.cleanup(self.conf["PIR GPIO pin"])
        if self.conf["stop detection GPIO pin"] >= 0:
            GPIO.cleanup(self.conf["stop detection GPIO pin"])

        print("[INFO] Released objects")
