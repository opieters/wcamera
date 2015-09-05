import RPi.GPIO as GPIO
import time, datetime, json
from picamera import PiCamera
from threading import Timer
from argparse import ArgumentParser

"""PIR implements motion detection based on the readouts from a PIR sensor.

Other global paramters are:
* `camera`: Raspberry Pi camera module object, set to a resolution of 640x480 by
 default. The camera object should not changed. Camera perameters can be
 modified.
* `stop detection GPIO pin`: GPIO pin number associated with terminate signal. A
 rising or falling edge event ends motion detection.
* `duration`: how long motion detection should run in seconds (0 = infinity)
* `motion`: keeps track of ongoing motion detection (do NOT modify!)
* `run_complete`: flag if motion detection should terminate (do NOT modify!)

Note: do not load with the `from ... import *` syntax to avoid naming conflicts.
"""

# camera
camera = None

# motion variable
motion = False

# duration variable
run_complete = False

def init(conf_file="conf.json"):
    conf = json.load(open(conf_file))
    camera = PiCamera()
    camera.resolution = tuple(conf["resolution"])
    motion = False
    run_complete = False
    camera.led = conf["camera LED"]

def delete():
    camera = None
    GPIO.cleanup()

def motion_detected(video_name):
    """Callback if motion is detected. A video will be created with name
    `video_name`."""
    print("[INFO] Motion detected")
    recording = True
    motion = True
    if not recording:
        camera.start_recording(video_name)


def no_motion():
    """Callback if motion ended."""
    print("[INFO] Motion ended")
    motion = False
    threading.Timer(10, stop_recording).start()

def stop_recording():
    """Stops camera recording (if in progress)."""
    if (not motion) and recording:
        camera.stop_recording()
        recording = False

def gpio_event(pin):
    """GPIO event callback."""
    if GPIO.input(pin): # rising
        motion_detected("motion-" + datetime.datetime.now().strftime("%x-%X") + ".h264")
    else: # falling
        no_motion()

def run_timer_callback(pin):
    """Callback to end motion detection after `conf["duration"]` seconds"""
    run_complete = True

def run():
    """Perform motion detecton."""
    GPIO.setup(conf["PIR GPIO pin"], GPIO.IN) # register GPIO pin
    run_complete = False # run flag
    if conf["duration"] > 0: # stop recording after specified time
        Timer(conf["duration"], run_timer_callback).start()
    else:
        run_complete = False
    try:
        print("[INFO] Press CTRL-C to exit run function prematurely")
        time.sleep(1)
        GPIO.add_event_detect(conf["PIR GPIO pin"], GPIO.BOTH, callback=gpio_event)
        if conf["stop detection GPIO pin"] >= 0:
            GPIO.setup(conf["stop detection GPIO pin"], GPIO.IN)
            GPIO.add_event_detect(conf["stop detection GPIO pin"], GPIO.BOTH, callback=run_timer_callback)
        while 1:
            time.sleep(100)
    except KeyboardInterrupt or run_complete:
        print("[INFO] Motion detection ended. Cleaning and returning to menu.")

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-c", "--conf", required=False, help="Path to json configuration file", default="conf.json")

    args = vars(parser.parse_args())
    conf_file = args["conf"]

    init(conf_file)
