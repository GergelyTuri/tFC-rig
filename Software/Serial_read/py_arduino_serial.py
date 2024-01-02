"""
Python script to read data from Arduino serial ports and save it to a JSON file.

This script reads data from Arduino serial ports and saves it to a JSON file.
It takes command line arguments for mouse IDs and communication ports. The script continuously
reads data from the serial ports and appends it to a data list. When a specific end session
message is received, the script stops reading data, saves the data to a JSON file, and exits.

Usage:
    python py_arduino_serial.py -ids <mouse_ids> -p <primaryport> -s1 <secondaryport1>

Example:
    python py_arduino_serial.py -ids mouse1,mouse2 -p COM3 -s1 COM4
"""

import argparse
import json
import time
from datetime import datetime
from os.path import join

import serial
from serial_comm import SerialComm as sc


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
        help="Communication port for the secondary Arduino (optional)",
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
    current_date_time = datetime.now()
    formatted_date_time = current_date_time.strftime("%Y-%m-%d_%H-%M-%S")
    end_session_message = "Session has ended"
    session_ended = False  # Flag to indicate the end of the session
    file_name = "_".join(mouse_ids) + f"_{formatted_date_time}.json"

    data_list = {mouse_id: [] for mouse_id in mouse_ids}

    header = {
        "mouse_ids": mouse_ids,
        "primary_port": args.primaryport,
        "secondary_port": args.secondaryport1,
        "mouse_port_assignment": dict(zip(mouse_ids, ports)),
        "Start_time": formatted_date_time,
    }
    # Initialize serial communication
    comms = {mouse_id: sc(port, 9600) for mouse_id, port in zip(mouse_ids, ports)}
    time.sleep(2)

    try:
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
                            "message": data,
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
            if session_ended:
                for comm in comms.values():
                    comm.close()
                break  # Exit the while loop

    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    except KeyboardInterrupt:
        keyboard_interrupt = {
            "message": "KeyboardInterrupt",
            "absolute_time": datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f"),
        }
        for mouse_data in data_list.values():
            mouse_data.append(keyboard_interrupt)
        print("KeyboardInterrupt detected. Saving data to file...")

    with open(join("data", file_name), "w", encoding="utf-8") as f:
        json.dump({"header": header, "data": data_list}, f, indent=4)
        print(f"Data saved to {file_name}")
    # Time for cleaning up
    time.sleep(2)


if __name__ == "__main__":
    main()
