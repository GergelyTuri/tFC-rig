import argparse
import json
import time
from datetime import datetime

import serial
from serial_comm import SerialComm as sc


def main():
    """
    Reads data from an Arduino connected to the specified communication port and saves it to a JSON file.

    Args:
        mouse_id (str): ID of the mouse.
        commport (str): Communication port of the Arduino.

    Returns:
        None
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-id", "--mouse_id", required=True, help="id of the mouse")
    ap.add_argument(
        "-c", "--commport", required=True, help="Arduino's communication port"
    )

    args = ap.parse_args()
    mouse_id = args.mouse_id
    commport = args.commport
    current_date_time = datetime.now()
    formatted_date_time = current_date_time.strftime("%Y-%m-%d_%H-%M-%S")

    file_path = f"{mouse_id}_{formatted_date_time}.json"

    time.sleep(2)

    try:
        with sc(commport, 9600) as comm, open(file_path, "w", encoding="utf-8") as f:
            print(f"{comm} is connected")
            while True:
                data = comm.read_json()
                print(f"data: {data}")
                if data is not None and "error" not in data:
                    print(data)
                    json.dump(data, f)
                    f.write("\n")  # Write a newline to separate JSON entries
                    f.flush()
                else:
                    print(f"Non-JSON data: {data}")
                time.sleep(1)
    except serial.SerialException as e:
        print(f"{commport} is not connected: {e}")
    except KeyboardInterrupt:
        print("KeyboardInterrupt")


if __name__ == "__main__":
    main()
