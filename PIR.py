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

def init(conf_file="conf.json"):
    global conf, camera, run_complete, motion, recording, record_video
    conf = json.load(open(conf_file))
    camera = PiCamera()
    camera.resolution = tuple(conf["resolution"])
    motion = False
    run_complete = False
    recording = False
    record_video = conf["record video"]
    camera.led = conf["camera LED"]

def delete():
    global camera, run_timer, motion_timer
    del camera
    if 'run_timer' in globals() and run_timer is not None:
        run_timer.cancel()
        run_timer.join()
    if 'motion_timer' in globals() and motion_timer is not None:
        motion_timer.cancel()
        motion_timer.join()
    GPIO.cleanup()

def motion_detected(file_name):
    """Callback if motion is detected. A video will be created with name
    `video_name`."""
    print("[INFO] Motion detected")
    global recording, motion, record_video
    motion = True
    if not recording and record_video:
        camera.start_recording(file_name)
        recording = True
        print("[INFO] Start recording" + file_name)
    elif not record_video:
        camera.capture(file_name)
        print("[INFO] Capture frame" + file_name)


def no_motion():
    """Callback if motion ended."""
    print("[INFO] Motion ended")
    global motion, motion_timer, conf
    motion = False
    if record_video:
        if 'motion_timer' in globals() and motion_timer is not None:
            motion_timer.cancel()
        motion_timer = Timer(conf["motion delay"], stop_recording).start()

def stop_recording():
    """Stops camera recording (if in progress)."""
    global camera, recording
    if (not motion) and recording:
        camera.stop_recording()
        recording = False
        print("[INFO] Recording stopped.")

def gpio_event(pin):
    """GPIO event callback."""
    if GPIO.input(pin): # rising
        if record_video:
            motion_detected("motion-" + datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".h264")
        else:
            motion_detected("motion-" + datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".jpg")
    else: # falling
        no_motion()

def run_timer_callback():
    """Callback to end motion detection after `conf["duration"]` seconds"""
    global run_complete
    run_complete = True
    print("[INFO] Run timer callback: stop recording")

def run():
    """Perform motion detecton."""
    global run_complete, run_timer
    GPIO.setup(conf["PIR GPIO pin"], GPIO.IN) # register GPIO pin
    run_complete = False # run flag
    if conf["duration"] > 0: # stop recording after specified time
        run_timer = Timer(conf["duration"], run_timer_callback)
        run_timer.start()
    else:
        run_complete = False
    try:
        print("[INFO] Press CTRL-C to exit run function prematurely")
        time.sleep(1)
        GPIO.add_event_detect(conf["PIR GPIO pin"], GPIO.BOTH, callback=gpio_event)
        if conf["stop detection GPIO pin"] >= 0:
            print("[INFO] Detection GPIO pin active")
            GPIO.setup(conf["stop detection GPIO pin"], GPIO.IN)
            GPIO.add_event_detect(conf["stop detection GPIO pin"], GPIO.BOTH, callback=run_timer_callback)
        while not run_complete:
            time.sleep(3)
    except KeyboardInterrupt :
        print("[INFO] Motion detection ended. Cleaning and returning to menu.")

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-c", "--conf", required=False, help="Path to json configuration file", default="conf.json")

    args = vars(parser.parse_args())
    conf_file = args["conf"]

    init(conf_file)
    run()
    delete()
