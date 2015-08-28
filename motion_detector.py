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

# configure argument parser
parser = argparse.ArgumentParser()
#parser.add_argument("-v", "--video", help="path to video file")
#parser.add_argument("-a", "--min-area", type=int,default=500, help="minimum area size")
parser.add_argument("-c","--conf",required=True,help="Path to json configuration file")

# extract arguments
args = vars(parser.parse_args())

# filter warnings
warnings.filterwarnings("ignore")

# load configuration data from file
conf = json.load(open(args["conf"]))

# create camera object
camera = PiCamera()

# configure camera
camera.resolution = tuple(conf["resolution"])
camera.framerate = conf["fps"]
rawCapture = PiRGBArray(camera, size=tuple(conf["resolution"]))

# warming up camera
print "[INFO] warming up..."
time.sleep(conf["camera_warmup_time"])
avg_frame = None
motion_counter = 0

# loop over frames
for raw_frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # capture current frame
    frame = raw_frame.array
    timestamp = datetime.datetime.now()
    text = "No wildlife"

    frame = imutils.resize(frame, width=conf["detection_width"]) # resize frame
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # convert to gray scale (gray frame)
    gray = cv2.GaussianBlur(gray, tupel(conf["motion_blur_kernel_size"]), conf["motion_blur_std_x"]) # blur frame

    # init average frame
    if avg_frame is None:
        print("[INFO] starting background model...")
        avg_frame = gray.copy().astype("float")
        rawCapture.truncate(0)
        continue

    cv2.accumulateWeighted(gray, avg_frame, conf["motion_dection_average_weight"])

    frame_diff = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    frame_thr = cv2.threshold(frame_diff, conf["motion_threshold"], 255, cv2.THRESH_BINARY)[1]

    # fill holes (dilate) in image and find countours on threshold image
    frame_thr = cv2.dilate(frame_thr, None, iterations=2)
    (cnts,_) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # loop over contours
    for c in cnts:
        # ignore contour if too small
        if cv2.contourArea(c) < args["min_area"]:
            continue

        # compute contour bouding box and draw on frame
        (x,y,w,h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2)
        text = "Occupied"

# draw text and timestamp on frame
cv2.putText(frame, "Room status: {}".format(text), (10,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
cv2.putText(frame, datetime.datetime.now().shrftime("%A $d %B %Y %I:%M:%S%p"),(10,frame.shape[0]-10),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,255),1)

# show frame and record if user pressed key
cv2.imshow("Security Feed",frame)
cv2.imshow("Thresh",thresh)
cv2.imshow("Frame Delta",frameDelta)
key = cv2.waitKey(1) & 0xFF

# quit if q pressed
if key == ord("q"):
    break

# cleanup
camera.release()
cv2.destroyAllWindows()
