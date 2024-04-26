"""
Python script to read data from Arduino serial ports and save it to a JSON file.

This script reads data from Arduino serial ports and saves it to a JSON file.
It takes command line arguments for mouse IDs and communication ports. The script continuously
reads data from the serial ports and appends it to a data list. When a specific end session
message is received, the script stops reading data, saves the data to a JSON file, and exits.

Usage:
    python -m Software.Serial_read.py_arduino_serial_camera -ids <mouse_ids>
      -p <primary arduino's port> -s1 <secondary arduino's port>
      -c1 <camera1's serial number> -c2 <camera2's serial number> 
    

Example:
    python -m Software.Serial_read.py_arduino_serial_camera -ids m1 -p COM6
"""

import argparse
import json
import logging
import time
from datetime import datetime
from os.path import join
from pathlib import Path

import serial
import urllib3
import sys

from ..camera_control import camera_class as cc
from .serial_comm import SerialComm as sc
from .serial_comm import VisualEnhancemnets as ve

# (optional) Disable the "insecure requests" warning for https certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(level=logging.INFO)


def main():
    """
    Main function that reads data from Arduino serial ports and saves it to a JSON file.

    Args:
        None

    Returns:
        None
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-ids", "--mouse_ids", required=True, help="id of the mouse")
    ap.add_argument(
        "-p",
        "--primaryport",
        required=True,
        help="Communication port for the primary Arduino",
    )
    ap.add_argument(
        "-s1",
        "--secondaryport1",
        required=False,
        help="Communication port for the secondary Arduino",
    )
    ap.add_argument(
        "-c1",
        "--camera1",
        required=False,
        help="Camera serial number for the primary camera (e3v8375)",
    )
    ap.add_argument(
        "-c2",
        "--camera2",
        required=False,
        help="Camera serial number for the secondary camera (e3v83c7)",
    )

    args = ap.parse_args()
    mouse_ids = args.mouse_ids.split(",")
    ports = [args.primaryport]

    # Add secondary port to the list if provided
    if args.secondaryport1:
        ports.append(args.secondaryport1)

    if len(mouse_ids) != len(ports):
        raise ValueError(
            f"Number of mouse ids ({len(mouse_ids)}) does not match number of arduino ports ({len(ports)})"
        )

    # Global variables
    # this is the IP address of server side of the watchtower
    INTERFACE = "172.29.96.1"
    # data path
    script_path = Path(__file__).resolve().parent
    data_path = script_path / "data"
    current_date_time = datetime.now()
    formatted_date_time = current_date_time.strftime("%Y-%m-%d_%H-%M-%S")
    end_session_message = "Session has ended"
    session_ended = False  # Flag to indicate the end of the session
    file_name = "_".join(mouse_ids) + f"_{formatted_date_time}.json"
    file_path = data_path / file_name

    data_list = {mouse_id: [] for mouse_id in mouse_ids}

    # Camera setup:
    if args.camera1 is not None:
        cam1 = cc.e3VisionCamera(args.camera1)
        # need to sync the primary camera here:
        cam1.camera_action("UPDATEMC")
        # connect the camera
        cam1.camera_action(
            "CONNECT",
            Config="480p15",
            Codec="MJPEG",
            IFace=INTERFACE,
            Annotation="Time",
            Segtime="3m",
        )
        serial_numbers = [cam1.camera_serial]
    if args.camera2 is not None:
        cam2 = cc.e3VisionCamera(args.camera2)
        # connect the camera
        cam2.camera_action(
            "CONNECT",
            Config="480p15",
            Codec="MJPEG",
            IFace=INTERFACE,
            Annotation="Time",
            Segtime="3m",
        )
        serial_numbers.append(cam2.camera_serial)

    ve.progress_bar(5)

    header = {
        "mouse_ids": mouse_ids,
        "primary_port": args.primaryport,
        "secondary_port": args.secondaryport1,
        "mouse_port_assignment": dict(zip(mouse_ids, ports)),
        "Start_time": formatted_date_time,
    }
    if args.camera1 is not None:
        header["camera1"] = cam1.camera_serial
    if args.camera2 is not None:
        header["camera2"] = cam2.camera_serial

    # Initialize serial communication
    comms = {mouse_id: sc(port, 9600) for mouse_id, port in zip(mouse_ids, ports)}
    ve.progress_bar(10)

    try:
        if args.camera1 is not None:
            cam1.camera_action("RECORDGROUP", SerialGroup=serial_numbers)
        while True:
            for mouse_id, comm in comms.items():
                data = comm.read()
                if data is not None and "error" not in data:
                    print(f"{mouse_id}: {data}")
                    data_json = {
                        "message": data,
                        "mouse_id": mouse_id,
                        "port": comm.port,
                        "absolute_time": datetime.now().strftime(
                            "%Y-%m-%d_%H-%M-%S.%f"
                        ),
                    }
                    data_list[mouse_id].append(data_json)
                    if end_session_message in data_json.get("message", ""):
                        end_message = {
                            "mesage": data,
                            "absolute_time": datetime.now().strftime(
                                "%Y-%m-%d_%H-%M-%S.%f"
                            ),
                        }
                        # adding the end session message to all the mice
                        for mouse_data in data_list.values():
                            mouse_data.append(end_message)
                        print("Session has ended, closing file and exiting...")
                        session_ended = True
                        break
                elif data is not None and "error" in data:
                    print(f"Non-JSON data: {data}")
                sys.stdout.flush()
            if session_ended:
                for comm in comms.values():
                    comm.close()
                if args.camera1 is not None:
                    cam1.camera_action("STOPRECORDGROUP", SerialGroup=serial_numbers)
                    cam1.camera_action("DISCONNECT")
                    if args.camera2 is not None:
                        cam2.camera_action("DISCONNECT")
                break  # Exit the while loop
        time.sleep(2)

    except serial.SerialException as e:
        print(f"Serial port error: {e}")
        sys.stdout.flush()
    except KeyboardInterrupt:
        keyboard_interrupt = {
            "message": "KeyboardInterrupt",
            "absolute_time": datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f"),
        }
        for mouse_data in data_list.values():
            mouse_data.append(keyboard_interrupt)
        print("KeyboardInterrupt detected. Saving data to file...")
        sys.stdout.flush()
        for comm in comms.values():
            comm.close()
        print("Closing serial ports and stopping camera recording...")
        sys.stdout.flush()
        if args.camera1 is not None:
            cam1.camera_action("STOPRECORDGROUP", SerialGroup=serial_numbers)
            cam1.camera_action("DISCONNECT")
            if args.camera2 is not None:
                cam2.camera_action("DISCONNECT")

    with file_path.open("w", encoding="utf-8") as f:
        json.dump({"header": header, "data": data_list}, f, indent=4)
        print(f"Data saved to {file_path}")
    # Time for cleaning up
    time.sleep(2)


if __name__ == "__main__":
    main()
