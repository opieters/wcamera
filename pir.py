import RPi.GPIO as GPIO
import time
import picamera
import threading

def PIR_motion_detected():
    print("Motion detected")
    camera.start_recording("myvideo.h264")

def PIR_no_motion():
    print("No motion")
    threading.Timer(10, stop_if_no_motion).start()

def stop_if_no_motion():
    if no_motion:
        camera.stop_recording()

def PIR_edge(pin):
    if GPIO.input(pin): # rising
        PIR_motion_detected()
    else: # falling
        PIR_no_motion()


# set GPIO pin numbering
GPIO.setmode(GPIO.BCM)

# PIR GPIO pin
PIR_pin = 7

# register GPIO pin
GPIO.setup(PIR_pin,GPIO.IN)

# camera
camera = picamera.PiCamera()
camera.resolution = (640, 480)

try:
    print("Press CTRL-C to exit script")
    time.sleep(1)
    GPIO.add_event_detect(PIR_pin,GPIO.BOTH,callback=PIR_edge)
    while 1:
        time.sleep(100)
except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()
