"""
This script reads data from an Arduino connected to the specified communication port and
saves it to a JSON file.

The script takes two arguments: mouse_id (str) and commport (str).

The data is saved in a JSON file with the name "{mouse_id}_{formatted_date_time}.json".

The script uses the SerialComm class from the serial_comm module to establish
a connection with the Arduino.

The data is read from the Arduino and saved to a list of dictionaries,
where each dictionary contains the message and the absolute time of the message.

The script stops reading data when it receives
the "Session has ended" message from the Arduino or when the user interrupts the script.

The data is saved to the JSON file along with a header containing
the mouse_id, start time, and commport.
"""
import argparse
import json
import time
from datetime import datetime

import serial
from serial_comm import SerialComm as sc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-ids", "--mouse_ids", required=True, help="id of the mouse")
    ap.add_argument(
        "-p",
        "--primaryport",
        required=True,
        help="Communication port for the primary Arduino",
    )
    ap.add_argument(
        "s1",
        "--secondaryport1",
        required=True,
        help="Communication port for the secondary Arduino",
    )

    args = ap.parse_args()
    mouse_ids = list(args.mouse_id)
    arduinos = list(args.primaryport, args.secondaryport1)
    current_date_time = datetime.now()
    formatted_date_time = current_date_time.strftime("%Y-%m-%d_%H-%M-%S")

    primary_data_list = []
    secondary_data_list = []    
    end_session_message = "Session has ended"
    for mouse, port in zip(mouse_ids, arduinos):
        file_path = f"{mouse}_{formatted_date_time}.json"

        header = {
            "mouse_id": mouse,
            "Start_time": formatted_date_time,
            "commport": port,
        }
    time.sleep(2)

    try:
        for ardiuno in arduinos:

        with sc(commport, 9600) as comm:
            print(f"{comm} is connected")
            while True:
                data = comm.read()
                if data is not None and "error" not in data:
                    print(f"data: {data}")
                    try:
                        data_json = {
                            "message": data,
                            "absolute_time": datetime.now().strftime(
                                "%Y-%m-%d_%H-%M-%S.%f"
                            ),
                        }
                    except json.JSONDecodeError:
                        print(f"JSONDecodeError: {data}")
                    data_list.append(data_json)
                    if end_session_message in data_json.get("message", ""):
                        print("Session has ended, closing file and exiting...")
                        break
                else:
                    # TODO: supperss these print statements if not in debug mode
                    # maybe do something more meaningful here (error handling, restarting communication, etc.)
                    print(f"Non-JSON data: {data}")
                time.sleep(0.05)
    except serial.SerialException as e:
        print(f"{commport} is not connected: {e}")
    except KeyboardInterrupt:
        data_list.append(
            {"KeyboardInterrupt": datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")}
        )
        print("KeyboardInterrupt detected. Saving data to file...")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump({"header": header, "data": data_list}, f, indent=4)
        print(f"Data saved to {file_path}")


if __name__ == "__main__":
    main()
