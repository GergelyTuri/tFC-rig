import argparse
import time

import serial


def main():
    """reads serial data from arduino and prints it to console"""

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-c", "--commport", required=True, help="Arduino's communication port"
    )
    args = ap.parse_args()
    commport = args.commport

    ser = serial.Serial(commport, 9600, timeout=10)

    while True:
        if ser.in_waiting:
            line = ser.readline().decode("utf-8").rstrip()
            print(line)
        time.sleep(1)


if __name__ == "__main__":
    main()
