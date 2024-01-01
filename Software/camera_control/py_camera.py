"""
Script for triggered recordings
  * 12/29/2023 setup for two cameras
"""

# import necessary libraries
import logging
import sys
import time

sys.path.append("c:/Users/Gergo_PC/Documents/code/tFC-rig/Software/Serial_read")

import camera_class as cc
import urllib3
from serial_comm import SerialComm as sc

# (optional) Disable the "insecure requests" warning for https certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)

# this is the IP address of server side of the watchtower
INTERFACE = "169.254.84.40"

# arduino setup
port = "COM6"
arduino_trigger = sc(port, 9600)

# Camera setup:
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

with arduino_trigger:
    if arduino_trigger.listen_for_ttl_pulse():
        cam1.camera_action("RECORDGROUP", SerialGroup=serial_numbers)
        # recording for 5 seconds
        time.sleep(5)
        cam1.camera_action("STOPRECORDGROUP", SerialGroup=serial_numbers)

        # set a 2s interval for cleanup
        time.sleep(2)
        cam1.camera_action("DISCONNECT")
        cam2.camera_action("DISCONNECT")
