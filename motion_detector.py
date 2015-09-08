#!/usr/bin/env python

# this code was inspired by the tutorial by Adrian Rosebrock:
# http://www.pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/

import time, datetime, json, cv2, warnings
import RPi.GPIO as GPIO
from argparse import ArgumentParser
from imutils import resize
from picamera.array import PiRGBArray
from picamera import PiCamera, PiCameraError
from threading import Timer

"""PIR implements motion detection based on the readouts from a PIR sensor.

Can be used as a standalone script or as a module.

Script use:
    Run with: `sudo python PIR.py [-c conf_file]`
    If the configuration file is not specified, the default file will be loaded: `conf.json`
    Open help with: `python PIR.py -h` or `python PIR.py --help`

Module use:
    1. call init([conf_file="conf.json"]) to initilise module
    2. call run([duration]) to start recording, if duration unspecified, the config file duration is loaded.
    3. call delete() to release all objects and clean up.

    Successive `run` calls may be perfromed before the `delete` call. The `delete` call can be undone with an `init` call, but the init method should only be called once (at the beginning) or after a `delete` call!

Note: all methods have sufficiently small names so a from PIR import * is not advised (also because of possible naming conflicts)
"""

# global objects
__conf__ = None
__camera__ = None
__run_complete__ = False

def init(conf_file="__conf__.json"):
    """Initialise module for recording with configuration file_conf or
    conf.json if unspecified.
    """

    # filter warnings
    warnings.filterwarnings("ignore")

    global __camera__, __conf__, __run_complete__

    # load configuration data from file
    __conf__ = json.load(open(conf_file))

    # create and configure camera object
    __camera__ = PiCamera()
    __camera__.resolution = tuple(conf["detection resolution"])
    __camera__.framerate = __conf__["fps"]

# define all 'private' methods
def __reset_variables__():
    """Reset all variables to default values."""

    global __run_complete__

    __run_complete__ = False

def delete():
    """Release all nessesary veriables and stop timers."""

    __camera__.close() # release camera

    if __conf__["show video"]:
        cv2.destroyAllWindows()

    # clean GPIO pins
    if __conf__["stop detection GPIO pin"] >= 0:
        GPIO.cleanup(__conf__["stop detection GPIO pin"])

def __run_timer_callback__(pin):
    """"""
    global __run_complete__
    __run_complete__ = True

def run(duration=None):
    """Perform motion detecton."""

    __reset_variables__()

    # warming up camera
    print "[INFO] warming up..."
    time.sleep(__conf__["camera warmup time"])
    avg_frame = None

    rawCapture = PiRGBArray(__camera__, size=tuple(__conf__["resolution"]))

    # limit recording duration if needed
    if __conf__["duration"] > 0:
        run_timer = Timer(__conf__["duration"], stop_recording_callback)
        run_timer.start()
    else:
        run_timer = None

    # setup GPIO pin to stop run on event
    if __conf__["stop detection GPIO pin"] >= 0:
        GPIO.setup(__conf__["stop detection GPIO pin", GPIO.IN])
        GPIO.add_event_detect(__conf__["stop detection GPIO pin"], GPIO.BOTH, callback=__run_timer_callback__)

    try:
        # loop over frames
        for raw_frame in __camera__.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            # capture current frame
            frame = raw_frame.array
            timestamp = datetime.datetime.now()

            # resize, convert to grayscale and blur (less noise)
            frame = resize(frame, width=__conf__["detection width"])
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, tuple(__conf__["motion blur kernel size"]), __conf__["motion blur std x"])

            # init average frame
            if avg_frame is None:
                print("[INFO] Starting background model...")
                avg_frame = gray.copy().astype("float")
                rawCapture.truncate(0)
                continue

            # update background frame
            cv2.accumulateWeighted(gray, avg_frame, __conf__["motion dection average weight"])

            # compute difference of current and average frame and detect values above threshold
            frame_diff = cv2.absdiff(gray, cv2.convertScaleAbs(avg_frame))
            frame_thr = cv2.threshold(frame_diff, __conf__["motion threshold"], 255, cv2.THRESH_BINARY)[1]

            # fill holes (dilate) in image and find countours on threshold image
            frame_thr = cv2.dilate(frame_thr, None, iterations=2)
            (cnts,_) = cv2.findContours(frame_thr.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # default: no motion
            motion = False

            # loop over contours (try to find motion)
            for c in cnts:
                # ignore contour if too small
                if cv2.contourArea(c) < __conf__["motion min area"]:
                    continue

                motion = True

                # no annotations, leave frame as is
                if not __conf__["annotations"]:
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
                print("[INFO] Motion detected at "+timestamp_txt)
                cv2.imwrite("motion-" + timestamp_txt,frame)

            # show frame and record if user pressed key
            if __conf__["show video"]:
                cv2.imshow("Security Feed",frame)
                cv2.imshow("Thresh",frame_thr)
                cv2.imshow("Frame Delta",frame_diff)

            # cleanup (go to most recent frame)
            rawCapture.truncate(0)

            # stop for-loop if needed
            if __run_complete__:
                break

    except KeyboardInterrupt:
        print("[INFO] Motion detection stopped.")
    except PiCameraError:
        print("[ERROR] Camera error... Stop detection")

    # clean timer if set
    if run_timer is not None:
        run_timer.cancel()
        run_timer.join()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-c", "--conf", required=False, help="Path to json configuration file", default="conf.json")
    parser.add_argument("-d", "--duration", required=False, help="Duration of motion detection", default=None, type=int)

    args = vars(parser.parse_args())

    init(args["conf"])
    run(args["duration"])
    delete()
