"""
Tests script to record a video for a few seconds with two cameras.
The browser interface should be open and set up:
  * Cameras are connected, scanned, bound
  * Stream with networks is set up to Ethernet
  * Primary control camera is set up as the first camera pugged in.
  * Cameras are set to stand by
"""
# import necessary libraries
import logging
import time

import camera_class as cc
import urllib3

# (optional) Disable the "insecure requests" warning for https certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)

# this is the IP address of server side of the watchtower
INTERFACE = "169.254.84.40"

cam1 = cc.e3VisionCamera("e3v8375")
cam2 = cc.e3VisionCamera("e3v83c7")

# need to sync the primary camera here:
cam1.camera_action("UPDATEMC")
time.sleep(5)

# connect to the cameras
cam1.camera_action(
    "CONNECT",
    Config="480p15",
    Codec="MJPEG",
    IFace=INTERFACE,
    Annotation="Time",
    Segtime="3m",
)

cam2.camera_action(
    "CONNECT",
    Config="480p15",
    Codec="MJPEG",
    IFace=INTERFACE,
    Annotation="Time",
    Segtime="3m",
)

serial_numbers = [cam1.camera_serial, cam2.camera_serial]
time.sleep(10)
cam1.camera_action("RECORDGROUP", SerialGroup=serial_numbers)
# recording for 5 seconds
time.sleep(5)
cam1.camera_action("STOPRECORDGROUP", SerialGroup=serial_numbers)

# set a 2s interval for cleanup
time.sleep(2)
cam1.camera_action("DISCONNECT")
cam2.camera_action("DISCONNECT")
