import argparse
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-f", "--file", required=True, help="file to parse")
    args = ap.parse_args()

    with open(args.file, "r") as f:
        data = json.load(f)

    header = data.get("header")
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
    print("millis values: ", millis_list)

    current_trial = 0
    trials = {}

    for entry in data_entries:
        message = entry.get("message", "")
        absolute_time = entry.get("absolute_time", "")

        if "Trial has started" in message:
            current_trial += 1
            trials[current_trial] = []

        if current_trial > 0:
            trials[current_trial].append((message, absolute_time))

    for trial, events in trials.items():
        print(f"Trial {trial}:")
        for event in events:
            print(f" Event: {event[0]}, {event[1]}")


if __name__ == "__main__":
    main()
