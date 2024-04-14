import json
import os
import re
from datetime import datetime
from typing import Optional

import pandas as pd

from tfcrig.files import DATETIME_REGEX
from tfcrig.notebook import builtin_print


def extract_exp_mouse_pairs(exp_mouse_blob: str) -> list[str]:
    """
    Define a recursive function that helps extract sets of
    `{experiment_id}_{mouse_id}_` from a file name. It accepts the
    front portion of a session file name and returns a list of
    these sets
    """
    pattern = r"\d+[_-]\d+[_-]"
    string_match = re.search(pattern, exp_mouse_blob)

    if string_match:
        first_pair = string_match.group()
        rest_of_string = exp_mouse_blob[string_match.end():]
        return [first_pair] + extract_exp_mouse_pairs(rest_of_string)
    return []


def is_data_file(file_name: str) -> bool:
    # Data files contain a specific date-time blob
    if not re.search(DATETIME_REGEX, file_name):
        return False

    # Data files have the format:
    #
    #     {exp_mouse_blob}_{datetime}.json
    #
    file_name_parts = re.split(DATETIME_REGEX, file_name)
    if file_name_parts[-1] != ".json":
        return False

    return True


def get_mouse_ids_from_file_name(file_name: str) -> list[Optional[str]]:
    file_name_parts = re.split(DATETIME_REGEX, file_name)
    exp_mouse_pairs = extract_exp_mouse_pairs(file_name_parts[0])
    # The magic `[0:-1]` removes a trailing underscore. Later raw data files
    # will be examined for mouse IDs that match their names
    return [e[0:-1] for e in exp_mouse_pairs]


def get_datetime_from_file_path(file_path: str) -> datetime:
    date_match = re.search(DATETIME_REGEX, file_path)
    if date_match:
        return datetime.strptime(date_match.group(), "%Y-%m-%d_%H-%M-%S")
    return None


def datetime_to_session_id(date_time: datetime) -> int:
    return int(date_time.strftime("%Y%m%d%H%M%S"))


def get_mouse_ids(data_root: str) -> set[Optional[str]]:
    """
    Given the path to the root of the data directory, return a set of mouse
    IDs. Also checks that mouse ID, session ID pairs are unique
    """
    all_mouse_ids = []
    mouse_session_pairs = set()
    for _, _, files in os.walk(data_root):
        for file_name in files:
            if not is_data_file(file_name):
                continue

            mouse_ids = get_mouse_ids_from_file_name(file_name)
            session_id = datetime_to_session_id(
                get_datetime_from_file_path(file_name)
            )

            # Mouse ID, session ID pairs should be unique
            for mouse_id in mouse_ids:
                key = (mouse_id, session_id)
                if key in mouse_session_pairs:
                    raise ValueError(
                        "Found non-unique mouse id, session id pair: "
                        f"({mouse_id}, {session_id})"
                    )
                mouse_session_pairs.add(key)

            all_mouse_ids += mouse_ids

    return set(mouse_ids)


def extract_features_from_session_data(
    *,
    raw_data: dict,
    mouse_id: str,
    session_id: int,
    file_name: str,
    print_bad_data_blobs: bool = False,
) -> pd.DataFrame:
    """The raw data frame is parsed into a Pandas data frame with the
    `message` field parsed into

        - trial (int)
        - session time (milliseconds from zero)
        - trial time (milliseconds from zero)
        - message (not the `message` JSON object, but the parsed message)

    The `message` is further parsed based on its content. This method is
    doing a lot of the heavy-lifting in terms of data processing, and it
    contains assumptions about the way the Rig saves data.

        -
    """
    parsed_data = []
    msg_delimiter = ": "

    # Parsing these variables (this data) assumes the messages are ordered
    # by time, and checks for certain markers in the data. It uses `{0, 1}`
    # to represent `False` and `True` respectively
    is_session = 0
    # Valid trial types: `{0, 1}`, type `-1` represents not known or no
    # current trial yet
    trial_type = -1
    negative_signal = 0
    positive_signal = 0
    water = 0
    previous_time = raw_data[0]["absolute_time"]

    # Some data integrity checks, we may want to skip data and mark sessions as
    # invalid if these fails.
    #
    # Check for session start and end:
    data_str = json.dumps(raw_data)
    session_start_msg = "Session has started"
    session_end_msg = "Session has ended"
    if (
        session_start_msg not in data_str
        or session_end_msg not in data_str
    ):
        print("Session either does not start or does not end!!!")
        builtin_print(f"    - File: {file_name}")
        return pd.DataFrame()
    # Check trial start and ends (every trial that starts, ends)
    is_trial = 0
    trial_start_msg = "Trial has started"
    trial_end_msg = "Trial has ended"
    n_trial_starts = data_str.count(trial_start_msg)
    n_trial_ends = data_str.count(trial_end_msg)
    if n_trial_starts != n_trial_ends:
        print(f"Trial start, end mismatch!!!")
        builtin_print(f"    - File: {file_name}")
        return pd.DataFrame()

    for data_blob in raw_data:
        # Parse the JSON message
        try:
            absolute_time = data_blob["absolute_time"]
            split_data = data_blob["message"].split(msg_delimiter)
            trial = int(split_data[0])
            t_sesh = int(split_data[1])
            t_trial = int(split_data[2])
            msg = msg_delimiter.join(split_data[3::])
        except (KeyError, ValueError):
            if print_bad_data_blobs:
                print(f"Bad data found in '{file_name}', skipping!")
                builtin_print(f"    - Bad data blob: {data_blob}")
            continue

        # Confirm that absolute time moves forward
        if absolute_time < previous_time:
            raise ValueError("Time did not move forwards!")
        previous_time = absolute_time
        absolute_datetime = datetime.strptime(
            absolute_time,
            "%Y-%m-%d_%H-%M-%S.%f",
        )

        # Check for session start, end
        if session_start_msg in msg:
            is_session = 1
        if session_end_msg in msg:
            is_session = 0
            trial_type = -1

        # Check for trial start, end
        if trial_start_msg in msg:
            is_trial = 1
        if trial_end_msg in msg:
            is_trial = 0

        # Get trial type
        if "currentTrialType" in msg:
            trial_type = int(msg.split(msg_delimiter)[1])
            if trial_type not in [0, 1]:
                print(f"Invalid trial type in: '{msg}'!!!")
                builtin_print(f" - File: {file_name}")
                return pd.DataFrame()

        # Check for lick
        lick = 0
        if msg == "Lick":
            lick = 1

        # Negative signal
        if "Negative signal start" in msg:
            negative_signal = 1
        if "Negative signal stop" in msg:
            negative_signal = 0

        # Positive signal
        if "Positive signal start" in msg:
            positive_signal = 1
        if "Positive signal stop" in msg:
            positive_signal = 0

        # Water reward
        if "Water on" in msg:
            water = 1
        if "Water off" in msg:
            water = 0

        # Build the parsed/rich dictionary
        parsed_data.append(
            {
                "mouse_id": mouse_id,
                "session_id": session_id,
                "absolute_time": absolute_datetime,
                "trial": trial,
                "session_time": t_sesh,
                "trial_time": t_trial,
                "message": msg,
                "is_session": is_session,
                "is_trial": is_trial,
                "trial_type": trial_type,
                "lick": lick,
                "negative_signal": negative_signal,
                "positive_signal": positive_signal,
                "water": water,
            }
        )

    return pd.DataFrame(parsed_data)


def get_data_features_from_data_file(full_file: str) -> pd.DataFrame:
    """
    Assuming that:

        - Each file contains data from a single session
        - Each file may contain data from multiple mice

    Extract data features from the data file. This _could_ be saved as
    processed data to speed up future analyses.
    """
    file_name = full_file.split("/")[-1]
    mouse_ids = get_mouse_ids_from_file_name(file_name)
    session_id = datetime_to_session_id(get_datetime_from_file_path(file_name))

    data_frames = []
    for mouse_id in mouse_ids:
        try:
            with open(full_file, "r") as f:
                json_data = json.load(f)
            raw_data = json_data["data"][mouse_id]
        except KeyError:
            # We choose to fail loudly, but continue
            print(
                f"This file name does not match its 'mouse_ids': {full_file}"
            )
            print(f'Keys: {json_data["data"].keys()}')
            continue
        df = extract_features_from_session_data(
            raw_data=raw_data,
            mouse_id=mouse_id,
            session_id=session_id,
            file_name=file_name,
        )
        if not df.empty:
            data_frames.append(df)

    if data_frames:
        return pd.concat(data_frames).reset_index(drop=True)
    return pd.DataFrame()


class Analysis:
    """
    Given a root data directory, extract features for an analysis. The data
    frame put to use in the analysis has the following columns:

        - Mouse ID
        - Session ID (date)
        - Features

    """

    def __init__(self, *, data_root: str) -> None:
        self.data_root = data_root

        # From the entire data root directory, get the set of mouse IDs
        self.mouse_ids = get_mouse_ids(self.data_root)

        # Likewise, extract features from all of the data
        data_frames = []
        for root, _, files in os.walk(DATA_ROOT):
            for file in files:
                if is_data_file(file):
                    data = get_data_features_from_data_file(
                        os.path.join(root, file)
                    )
                    if not data.empty:
                        data_frames.append(data)
        self.data = pd.concat(data_frames).reset_index(drop=True)

        # TODO: investigate for performance
        #
        #   - Extracting features into data frames, and not concatenating all
        #     data from all mice/sessions
        #   - At either point, storing processed data
        #
        # TODO: message folks about the files with mismatched mouse IDs
        #