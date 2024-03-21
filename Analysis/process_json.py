"""
This script parses a JSON file containing behavioral data and extracts relevant information.

The script takes a command-line argument specifying the path to the JSON file to parse.
It reads the JSON file, extracts the header mouse_data and data mouse_data, and performs the following tasks:
- Prints the header mouse_data
- Identifies the start and end times of a session
- Counts the number of trials and prints the start times of each trial
- Extracts information for each trial, including session and trial times, message, and absolute time
- Writes the extracted data to a new JSON file named "session.json" with an indented format

Usage: python process_json.py -f <path_to_json_file>
author: @gergelyturi
11/28/23 - version 1.0
11/29/23 - version 1.1 imporving data read and save
"""

import argparse
import json


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

    with open(args.file, "r", encoding="utf-8") as f:
        data = json.load(f)

    header_entries = data.get("header", [])
    data_entries = data.get("data", [])
    mouse_ids = header_entries.get("mouse_ids", [])

    print(f"mouse IDs: {mouse_ids}")

    # processed_trial_data = {}
    # processed_intertrial_data = {}
    all_mouse_data = {}
    for mouse_id in mouse_ids:
        mouse_data = data_entries.get(mouse_id, [])
        session_info = session_summary(mouse_data)
        trial_data = process_trial_data(mouse_data, trial_type="trial")
        intertrial_data = process_trial_data(mouse_data, trial_type="intertrial")

        all_mouse_data[mouse_id] = {
            "session_info": session_info,
            "trial_data": trial_data,
            "intertrial_data": intertrial_data,
        }
    output_file_name = args.file.split(".")[0] + "_processed.json"
    with open(output_file_name, "w", encoding="utf-8") as f:
        json.dump(
            {
                "header": header_entries,
                "data": all_mouse_data,
            },
            f,
            indent=4,
        )


def session_summary(mouse_data):
    # Session information
    session = {"session_start": None, "session_end": None}
    for sess in mouse_data:
        message = sess.get("message", "")
        if "Session has started" in message:
            parts = message.split(":")
            millis = int(parts[1].strip())
            session["session_start"] = millis
        elif "Session has ended" in message:
            parts = message.split(":")
            millis = int(parts[1].strip())
            session["session_end"] = millis
    print(f"session: {session}")

    # Trial information
    trials = 0
    millis_list = []
    for trial in mouse_data:
        message = trial.get("message", "")
        port = trial.get("port", "")
        if "Trial has started" in message:
            trials += 1
            parts = message.split(":")
            millis = int(parts[1].strip())
            millis_list.append(millis)
    print("Port: ", port)
    print("number of trials: ", trials)
    print("trial start times millis values: ", millis_list)

    # Inter-trial information
    inter_trials = 0
    millis_list = []
    for inter_trial in mouse_data:
        message = inter_trial.get("message", "")
        if "Waiting the inter-trial interval" in message:
            inter_trials += 1
            parts = message.split(":")
            millis = int(parts[1].strip())
            millis_list.append(millis)
    print("number of inter-trials: ", inter_trials)
    print("inter-trial start times millis values: ", millis_list)
    return session


def process_trial_data(mouse_data, trial_type="trial"):
    current_trial = 0
    trials = {}

    if trial_type == "trial":
        start_message = "Trial has started"
        end_message = "Trial has ended"
    elif trial_type == "intertrial":
        start_message = "Waiting the inter-trial interval"
        end_message = "Trial has started"

    for entry in mouse_data:
        message = entry.get("message", "")
        absolute_time = entry.get("absolute_time", "")

        if start_message in message:
            current_trial += 1
            trial_ended = False
            trials[f"{trial_type}_{current_trial}"] = []

        if current_trial > 0 and not trial_ended:
            parts = message.split(":")
            millis = int(parts[1].strip()) if len(parts) > 1 else None
            trial_millis = int(parts[2].strip()) if len(parts) > 2 else None
            rest_of_message = ":".join(parts[3:]).strip() if len(parts) > 3 else ""
            trials[f"{trial_type}_{current_trial}"].append(
                {
                    "session_millis": millis,
                    "trial_millis": trial_millis,
                    "message": rest_of_message,
                    "absolute_time": absolute_time,
                }
            )
            if end_message in message:
                trial_ended = True
    return trials


if __name__ == "__main__":
    main()
