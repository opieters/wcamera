import RPi.GPIO as GPIO
import time, datetime
import picamera
import threading

"""PIR implements motion detection based on the readouts from a PIR sensor.

In order to correcly function, the following GPIO pin number parameter must be
set *before* the actual detection starts with: `PIR.gpio_pin`.

Other global paramters are:
* `camera`: Raspberry Pi camera module object, set to a resolution of 640x480 by
 default. The camera object should not changed. Camera perameters can be
 modified.
* `stop_detection_pin`: GPIO pin number associated with terminate signal. A
 rising or falling edge event ends motion detection.
* `duration`: how long motion detection should run in seconds (0 = infinity)
* `motion`: keeps track of ongoing motion detection (do NOT modify!)
* `run_complete`: flag if motion detection should terminate (do NOT modify!)

Note: do not load with the `from ... import *` syntax to avoid naming conflicts.
"""

# PIR GPIO pin
gpio_pin = 26

# camera
camera = picamera.PiCamera()
camera.resolution = (640, 480)

# motion variable
motion = False

# duration variable
run_complete = False

# register specific pin to prematurely end detection on GPIO event
stop_detection_pin = -1

# set run duration (0 = run infinitly long)
duration = 0

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
    """Callback to end motion detection after `duration` seconds"""
    run_complete = True

def run():
    """Perform motion detecton."""
    GPIO.setup(gpio_pin, GPIO.IN) # register GPIO pin
    run_complete = False # run flag
    if duration > 0: # stop duration after specified time
        threading.Timer(duration, run_timer_callback).start()
    try:
        print("[INFO] Press CTRL-C to exit run function prematurely")
        time.sleep(1)
        GPIO.add_event_detect(gpio_pin, GPIO.BOTH, callback=gpio_event)
        if stop_detection_pin >= 0:
            GPIO.add_event_detect(gpio_pin, GPIO.BOTH, callback=run_timer_callback)
        while 1:
            time.sleep(100)
    except KeyboardInterrupt or run_complete:
        print("[INFO] Motion detection ended. Cleaning and returning to menu.")
        GPIO.cleanup()
