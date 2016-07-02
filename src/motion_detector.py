#!/usr/bin/env python

# this code was inspired by this tutorial by Adrian Rosebrock:
# http://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/

import time, datetime, json, cv2, warnings
import RPi.GPIO as GPIO
from argparse import ArgumentParser
from imutils import resize
from picamera.array import PiRGBArray
from picamera import PiCamera, PiCameraError
from threading import Timer

# global objects
class MD:

    def __init__(camera, conf):
        """Initialise module for recording with configuration file_conf or
        conf.json if unspecified.
        """

        self.conf = conf
        self.camera = camera
        self.run_complete = False

        # filter warnings
        warnings.filterwarnings("ignore")

        # create and configure camera object
        self.camera.resolution = tuple(conf["detection resolution"])
        self.camera.framerate = self.conf["fps"]

    # define all 'private' methods
    def reset_variables(self):
        """Reset all variables to default values."""
        self.run_complet = False

    def delete(self):
        """Release all nessesary veriables and stop timers."""

        if self.conf["show video"]:
            cv2.destroyAllWindows()

        # clean GPIO pins
        if self.conf["stop detection GPIO pin"] >= 0:
            GPIO.cleanup(self.conf["stop detection GPIO pin"])

    def run_timer_callback(self,pin):
        """"""
        self.run_complete = True

    def run(self,duration=None):
        """Perform motion detecton."""

        self.reset_variables()

        # warming up camera
        print "[INFO] warming up..."
        time.sleep(self.conf["camera warmup time"])
        avg_frame = None

        rawCapture = PiRGBArray(self.camera, size=tuple(self.conf["resolution"]))

        # limit recording duration if needed
        if self.conf["duration"] > 0:
            run_timer = Timer(self.conf["duration"], stop_recording_callback)
            run_timer.start()
        else:
            run_timer = None

        # setup GPIO pin to stop run on event
        if self.conf["stop detection GPIO pin"] >= 0:
            GPIO.setup(self.conf["stop detection GPIO pin", GPIO.IN])
            GPIO.add_event_detect(self.conf["stop detection GPIO pin"], GPIO.BOTH, callback=self.run_timer_callback)

        try:
            # loop over frames
            for raw_frame in self.camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                # capture current frame
                frame = raw_frame.array
                timestamp = datetime.datetime.now()

                # resize, convert to grayscale and blur (less noise)
                frame = resize(frame, width=self.conf["detection width"])
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, tuple(self.conf["motion blur kernel size"]), self.conf["motion blur std x"])

                # init average frame
                if avg_frame is None:
                    print("[INFO] Starting background model...")
                    avg_frame = gray.copy().astype("float")
                    rawCapture.truncate(0)
                    continue

                # update background frame
                cv2.accumulateWeighted(gray, avg_frame, self.conf["motion dection average weight"])

                # compute difference of current and average frame and detect values above threshold
                frame_diff = cv2.absdiff(gray, cv2.convertScaleAbs(avg_frame))
                frame_thr = cv2.threshold(frame_diff, self.conf["motion threshold"], 255, cv2.THRESH_BINARY)[1]

                # fill holes (dilate) in image and find countours on threshold image
                frame_thr = cv2.dilate(frame_thr, None, iterations=2)
                (cnts,_) = cv2.findContours(frame_thr.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # default: no motion
                motion = False

                # loop over contours (try to find motion)
                for c in cnts:
                    # ignore contour if too small
                    if cv2.contourArea(c) < self.conf["motion min area"]:
                        continue

                    motion = True

                    # no annotations, leave frame as is
                    if not self.conf["annotations"]:
                        break

                    # compute contour bouding box and draw on frame
                    (x,y,w,h) = cv2.boundingRect(c)
                    cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2)

                    # draw timestamp on frame
                    cv2.putText(frame, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

                    break

                # if motion has been detected, save frame to file
                if motion:
                    timestamp_txt = timestamp.strftime("%x-%X")
                    print("[INFO] Motion detected at " + timestamp_txt)
                    cv2.imwrite(self.conf["directory"] + "motion-" + timestamp_txt, frame)

                # show frame and record if user pressed key
                if self.conf["show video"]:
                    cv2.imshow("Security Feed",frame)
                    cv2.imshow("Thresh",frame_thr)
                    cv2.imshow("Frame Delta",frame_diff)

                # cleanup (go to most recent frame)
                rawCapture.truncate(0)

                # stop for-loop if needed
                if self.run_complete:
                    break

        except KeyboardInterrupt:
            print("[INFO] Motion detection stopped.")
        except PiCameraError:
            print("[ERROR] Camera error... Stopped detection.")

        # clean timer if set
        if run_timer is not None:
            run_timer.cancel()
            run_timer.join()
