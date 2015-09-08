#!/usr/bin/env python
import RPi.GPIO as GPIO
import time, datetime, json
from picamera import PiCamera, PiCameraError
from threading import Timer
from argparse import ArgumentParser

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

# define ('private') global variables
__camera__ = None
__conf__ = None
__run_complete__ = None
__motion__ = None
__recording__ = None
__record_video__ = None
__run_timer__ = None
__motion_timer__ =  None

# define all 'private' methods
def __reset_variables__():
    global __run_complete__, __motion__, __recording__, __record_video__, __run_timer__, __motion_timer__

    __camera__.resolution = tuple(__conf__["resolution"])
    __camera__.led = __conf__["camera LED"]
    __motion__ = False
    __run_complete__ = False
    __recording__ = False
    __record_video__ = __conf__["record video"]
    __run_timer__ = None
    __motion_timer__ = None

def __motion_detected__(file_name):
    """Callback if motion is detected. A video or still image will be created
    with name file_name.
    """

    print("[INFO] Motion detected")

    global __recording__, __motion__

    __motion__ = True

    # if video file requested and not already recording, start recording
    if (not __recording__) and __record_video__:
        __camera__.start_recording(file_name)
        __recording__ = True

        print("[INFO] Start recording" + file_name)

    # capture still image
    elif not __record_video__:
        __camera__.capture(file_name)

        print("[INFO] Capture frame" + file_name)


def __no_motion__():
    """Callback if motion ended."""

    print("[INFO] Motion ended")

    global __motion__, __motion_timer__

    __motion__ = False

    if __record_video__:
        # cancel already running timer if needed
        if __motion_timer__ is not None:
            __motion_timer__.cancel()

        __motion_timer__ = Timer(__conf__["motion delay"], __stop_recording__).start()

def __stop_recording__():
    """Stops camera recording (if in progress)."""

    global __recording__

    if (not __motion__) and __recording__:
        __camera__.stop_recording()
        __recording__ = False

        print("[INFO] Recording stopped.")

def __pir_event__(pin):
    """PIR GPIO event callback."""

    if GPIO.input(pin): # rising
        if __record_video__:
            __motion_detected__("motion-" + datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".h264")
        else:
            __motion_detected__("motion-" + datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".jpg")
    else: # falling
        __no_motion__()

def __run_timer_callback__():
    """Callback to end motion detection after __conf__["duration"] seconds"""

    global __run_complete__

    # stop recording
    __run_complete__ = True

    print("[INFO] Run timer callback: stop recording")

def run(duration=None):
    """Perform motion detecton."""

    __reset_variables__()

    global __run_complete__, __run_timer__

    GPIO.setup(__conf__["PIR GPIO pin"], GPIO.IN) # register GPIO pin

    __run_complete__ = False # run flag

    # load duration from config file if needed
    if duration is None:
        duration = __conf__["duration"]

    # stop recording after specified time if needed
    if duration > 0:
        __run_timer__ = Timer(__conf__["duration"], __run_timer_callback__)
        __run_timer__.start()

    # start recording, if KeyboardInterrupt stop execution (for debugging)
    try:
        print("[INFO] Press CTRL-C to exit run function prematurely")
        time.sleep(1)

        GPIO.add_event_detect(__conf__["PIR GPIO pin"], GPIO.BOTH, callback=__pir_event__)

        # configure exit button if configured
        if __conf__["stop detection GPIO pin"] >= 0:
            print("[INFO] Detection GPIO pin active")
            GPIO.setup(__conf__["stop detection GPIO pin"], GPIO.IN)
            GPIO.add_event_detect(__conf__["stop detection GPIO pin"], GPIO.BOTH, callback=__run_timer_callback__)

        # keep function alive and check every 3 seconds if the script needs to stop
        while not __run_complete__:
            time.sleep(3)

    except KeyboardInterrupt:
        print("[INFO] Motion detection ended. Cleaning and returning to menu.")
    except PiCameraError:
        print("[ERROR] Camera error... Stop detection")


def init(conf_file="conf.json"):
    """Initialise module for recording with configuration file_conf or
    conf.json if unspecified.
    """

    global __conf__, __camera__

    __conf__ = json.load(open(conf_file))
    __camera__ = PiCamera()

def delete():
    """Decallocate all nessesary veriables and stop timers."""

    __reset_variables__()

    # if camera is still recording, stop it before deallocation
    if __camera__.recording:
        __camera__.stop_recording()

    __camera__.close() # release camera

    if __run_timer__ is not None:
        __run_timer__.cancel()
        __run_timer__.join()

    if __motion_timer__ is not None:
        __motion_timer__.cancel()
        __motion_timer__.join()

    # clean GPIO pins
    GPIO.cleanup(__conf__["PIR GPIO pin"])
    if __conf__["stop detection GPIO pin"] >= 0:
        GPIO.cleanup(__conf__["stop detection GPIO pin"])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-c", "--conf", required=False, help="Path to json configuration file", default="conf.json")
    parser.add_argument("-d", "--duration", required=False, help="Duration of motion detection", default=None)

    args = vars(parser.parse_args())

    init(args["conf"])
    run(args["duration"])
    delete()
