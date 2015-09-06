#python path

#import libs
import argparse
import datetime
import imutils
import time
import cv2
import json
from picamera.array import PiRGBArray
from picamera import PiCamera
import warnings
import RPi.GPIO as GPIO
import threading

# global objects
conf = None
camera = None
stop_recording = False

def init(conf_file="conf.json"):
    # filter warnings
    warnings.filterwarnings("ignore")

    # load configuration data from file
    conf = json.load(open(conf_file))

    # create and configure camera object
    camera = PiCamera()
    camera.resolution = tuple(conf["detection resolution"])
    camera.framerate = conf["fps"]

    stop_recording = False

def delete():
    camera = None
    cv2.destroyAllWindows()
    GPIO.cleanup()

def stop_recording_callback(pin):
    stop_recording = True

def run():
    """TODO"""

    # warming up camera
    print "[INFO] warming up..."
    time.sleep(conf["camera warmup time"])
    avg_frame = None

    rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

    # limit recording duration if needed
    if conf["duration"] > 0:
        threading.Timer(conf["duration"], stop_recording_callback).start()
    else:
        stop_recording = False

    # setup GPIO pin to stop run on event
    if conf["stop detection GPIO pin"] >= 0:
        GPIO.setup(conf["stop detection GPIO pin", GPIO.IN])
        GPIO.add_event_detect(conf["stop detection GPIO pin"], GPIO.BOTH, callback=stop_recording_callback)

    try:
        # loop over frames
        for raw_frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            # capture current frame
            frame = raw_frame.array
            timestamp = datetime.datetime.now()
            text = "No wildlife"

            frame = imutils.resize(frame, width=conf["detection width"]) # resize frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert to gray scale (gray frame)
            gray = cv2.GaussianBlur(gray, tuple(conf["motion blur kernel size"]), conf["motion blur std x"]) # blur frame

            # init average frame
            if avg_frame is None:
                print("[INFO] starting background model...")
                avg_frame = gray.copy().astype("float")
                rawCapture.truncate(0)
                continue

            cv2.accumulateWeighted(gray, avg_frame, conf["motion dection average weight"])

            frame_diff = cv2.absdiff(gray, cv2.convertScaleAbs(avg_frame))
            frame_thr = cv2.threshold(frame_diff, conf["motion threshold"], 255, cv2.THRESH_BINARY)[1]

            # fill holes (dilate) in image and find countours on threshold image
            frame_thr = cv2.dilate(frame_thr, None, iterations=2)
            (cnts,_) = cv2.findContours(frame_thr.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            motion = False

            # loop over contours
            for c in cnts:
                # ignore contour if too small
                if cv2.contourArea(c) < conf["motion min area"]:
                    continue

                # compute contour bouding box and draw on frame
                (x,y,w,h) = cv2.boundingRect(c)
                cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2)
                text = "Wildlife detected"

                # draw text and timestamp on frame
                cv2.putText(frame, text, (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(frame, timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

                motion = True

            if motion:
                timestamp_txt = timestamp.strftime("%x-%X")
                print("[INFO] Motion detected at "+timestamp_txt)
                cv2.imwrite("motion-" + timestamp_txt,frame)

            # show frame and record if user pressed key
            if conf["show video"]:
                cv2.imshow("Security Feed",frame)
                cv2.imshow("Thresh",frame_thr)
                cv2.imshow("Frame Delta",frame_diff)
                key = cv2.waitKey(1) & 0xFF

            # cleanup
            rawCapture.truncate(0)
    except KeyboardInterrupt or stop_recording:
        print("[INFO] Motion detection stopped.")

if __name__ == '__main__':
    # configure argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf", required=False, help="Path to json configuration file", default="conf.json")

    # extract arguments
    args = vars(parser.parse_args())
    init(args["conf"])
