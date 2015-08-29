import RPi.GPIO as GPIO
import time

def PIR_motion_detected(pin):
    print("Motion detected")

# set GPIO pin numbering
GPIO.setmode(GPIO.BCM)

# PIR GPIO pin
PIR_pin = 7

# register GPIO pin
GPIO.setup(PIR_pin,GPIO.IN)

try:
    print("Press CTRL-C to exit script")
    time.sleep(1)
    GPIO.add_event_detect(PIR_pin,GPIO.RISING,callback=PIR_motion_detected)
    while 1:
        time.sleep(100)
except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()
