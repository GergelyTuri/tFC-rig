"""
Basic script to test camera recording.
* 12/28/2023 should be able to record with a single camera.
  The broswer interface is set as the following:
   - scanned for cameras
   - stream with network - Ethernet
   - primary control e3v8375
   - 1 active camera  
"""
# import necessary libraries
import logging
import time

import camera_class as cc
import urllib3

# (optional) Disable the "insecure requests" warning for https certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)

INTERFACE = "169.254.84.40"

cam = cc.e3VisionCamera("e3v8375")
time.sleep(5)
cam.camera_action("UPDATEMC")
time.sleep(5)
cam.camera_action(
    "CONNECT",
    Config="480p15",
    Codec="MJPEG",
    IFace=INTERFACE,
    Annotation="Time",
    Segtime="3m",
)
serial_numbers = [cam.camera_serial]
print(f"serial_numbers: {serial_numbers}")
cam.camera_action("RECORDGROUP", SerialGroup=serial_numbers)

# Record for 10 seconds
time.sleep(10)

cam.camera_action("STOPRECORDGROUP", SerialGroup=serial_numbers)
# set a 2s interval for cleanup
time.sleep(2)
cam.camera_action("DISCONNECT")
