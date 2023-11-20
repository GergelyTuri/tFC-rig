# import necessary libraries
import logging
import time

import camera_class as cc
import urllib3

# (optional) Disable the "insecure requests" warning for https certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)

# this is the IP address of server side of the watchtower
interface = "169.254.84.40"

cam = cc.e3VisionCamera("e3v8375")

cam.camera_action("DISCONNECT")
# this may be needed for the first time you run the script
# TODO: figure out how you can get the current state of the cameras if possible
# cam.camera_action("BIND")

cam.camera_action(
    "CONNECT",
    Config="480p15",
    Codec="MJPEG",
    IFace=interface,
    Annotation="Time",
    Segtime="3m",
)
# Syncing cameras
cam.camera_action("UPDATEMC")

# Set the cameras to record. These are going to be group operations.
serial_numbers = [cam.camera_serial]
cam.camera_action("RECORDGROUP", SerialGroup=serial_numbers)

# Record for 10 seconds
time.sleep(10)

cam.camera_action("STOPRECORDGROUP", SerialGroup=serial_numbers)
# set a 2s interval for cleanup
time.sleep(2)
cam.camera_action("DISCONNECT")
