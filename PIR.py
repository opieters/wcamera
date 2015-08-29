import RPi.GPIO as GPIO
import time
import picamera
import threading

# set GPIO pin numbering
GPIO.setmode(GPIO.BCM)

# PIR GPIO pin
gpio_pin = 7

# register GPIO pin
GPIO.setup(gpio_pin,GPIO.IN)

# camera
camera = picamera.PiCamera()
camera.resolution = (640, 480)

# motion variable
motion = False

# duration variable
run_complete = False

stop_detection_pin = -1

def motion_detected(video_name):
    print("Motion detected")
    recording = True
    motion = True
    if not recording:
        camera.start_recording(video_name)


def no_motion():
    print("No motion")
    motion = False
    threading.Timer(10, stop_recording).start()

def stop_recording():
    if (not motion) and recording:
        camera.stop_recording()
        recording = False

def gpio_event(pin):
    if GPIO.input(pin): # rising
        motion_detected()
    else: # falling
        no_motion()

def run_timer_callback(pin):
    run_complete = True

def run():
    run_complete = False
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
