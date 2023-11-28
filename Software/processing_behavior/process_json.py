"""
This script parses a JSON file containing behavioral data and extracts relevant information.

The script takes a command-line argument specifying the path to the JSON file to parse.
It reads the JSON file, extracts the header entries and data entries, and performs the following tasks:
- Prints the header entries
- Identifies the start and end times of a session
- Counts the number of trials and prints the start times of each trial
- Extracts information for each trial, including session and trial times, message, and absolute time
- Writes the extracted data to a new JSON file named "session.json" with an indented format

Usage: python process_json.py -f <path_to_json_file>
author: @gergelyturi
11/28/23 - version 1.0
"""

import argparse
import json

import pandas as pd


def main():
    """
    Parse a JSON file and extract relevant information.

    This function reads a JSON file, extracts specific information from it, and saves the extracted data
    into a new JSON file named "session.json".

    Args:
        None

    Returns:
        None
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", required=True, help="file to parse")
    args = ap.parse_args()

    with open(args.file, "r", encoding="cp1252") as f:
        data = json.load(f)

    header_entries = data.get("header", [])
    print(header_entries)

    data_entries = data.get("data", [])

    session = {"start": None, "end": None}
    for sess in data_entries:
        message = sess.get("message", "")
        if "Session has started" in message:
            parts = message.split(":")
            millis = int(parts[1].strip())
            session["start"] = millis
        elif "Session has ended" in message:
            parts = message.split(":")
            millis = int(parts[1].strip())
            session["end"] = millis
    print(session)

    trials = 0
    millis_list = []
    for trial in data_entries:
        message = trial.get("message", "")
        if "Trial has started" in message:
            trials += 1
            parts = message.split(":")
            millis = int(parts[1].strip())
            millis_list.append(millis)
    print("number of trials: ", trials)
    print("trial start times millis values: ", millis_list)

    current_trial = 0
    trials = {}

    for entry in data_entries:
        message = entry.get("message", "")
        absolute_time = entry.get("absolute_time", "")

        if "Trial has started" in message:
            current_trial += 1
            trial_ended = False
            trials[f"Trial_{current_trial}"] = []

        if current_trial > 0 and not trial_ended:
            parts = message.split(":")
            millis = int(parts[1].strip()) if len(parts) > 1 else None
            trial_millis = int(parts[2].strip()) if len(parts) > 2 else None
            rest_of_message = ":".join(parts[3:]).strip() if len(parts) > 3 else ""
            trials[f"Trial_{current_trial}"].append(
                {
                    "session_millis": millis,
                    "trial_millis": trial_millis,
                    "message": rest_of_message,
                    "absolute_time": absolute_time,
                }
            )
            if "Trial has ended" in message:
                trial_ended = True

    with open("session.json", "w", encoding="cp1252") as f:
        json.dump({"header": header_entries, "data": trials}, f, indent=4)


if __name__ == "__main__":
    main()
