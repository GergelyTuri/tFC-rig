import calendar
import json
import os
import re
from datetime import datetime
from typing import Optional

import ipywidgets as widgets
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import seaborn as sns
from IPython.display import display

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


def datetime_to_day_of_week(date_time: datetime) -> str:
    return calendar.day_name[date_time.weekday()]


def int_session_id_to_date_string(session_id: int) -> str:
    """
    Input is a session ID integer representing a `YYYYMMDDHHMMSS` date,
    output is a date string `YYYY-MM-DDTHH:MM:SS`
    """
    session_id = str(session_id)
    year = session_id[0:4]
    month = session_id[4:6]
    day = session_id[6:8]
    hour = session_id[8:10]
    minute = session_id[10:12]
    second = session_id[12:14]
    return f"{year}-{month}-{day}T{hour}:{minute}:{second}"


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

    # Include day of week in data
    date_time = get_datetime_from_file_path(file_name)
    day_of_week = datetime_to_day_of_week(date_time)

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

    # Some trial parameters we will try to extract
    air_puff_start_time = -1
    air_puff_stop_time = -1
    air_puff_total_time = -1
    first_puff_started = 0

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
            trial_type = -1

        # Get trial type
        if "currentTrialType" in msg:
            trial_type = int(msg.split(msg_delimiter)[1])
            if trial_type not in [0, 1]:
                print(f"Invalid trial type in: '{msg}'!!!")
                builtin_print(f" - File: {file_name}")
                return pd.DataFrame()

        # Get all trial types, check for balance. Note that if an
        # imbalance is intentional, this will print false positive
        # error messages
        if "trialTypes" in msg:
            trial_types = msg.split(msg_delimiter)[1]
            if trial_types.count("0") != trial_types.count("1"):
                if print_bad_data_blobs:
                    print(f"Unbalanced trial types in: '{msg}'!!!")
                    builtin_print(f" - File: {file_name}")
                continue

        # Check for some trial parameters
        if "AIR_PUFF_START_TIME" in msg:
            air_puff_start_time = int(msg.split(msg_delimiter)[1])
        if "AIR_PUFF_TOTAL_TIME" in msg:
            air_puff_total_time = int(msg.split(msg_delimiter)[1])
            air_puff_stop_time = air_puff_start_time + air_puff_total_time

        # Check for lick
        lick = 0
        if msg == "Lick":
            lick = 1

        # Check for puff start
        if msg == "Puff start":
            first_puff_started = 1

        # Check for an "air puff lick"
        # An "air puff lick" is a lick that occurs when air puffing is
        # occurring, which is determined based on trial time and air
        # puff parameters
        puffed_lick = 0
        if air_puff_start_time > 0 and air_puff_stop_time > 0:
            # We are in a part of the trial where these parameters have
            # been determined, given that we initialize them as `-1`
            if (
                lick and
                first_puff_started and
                t_trial >= air_puff_start_time and
                t_trial <= air_puff_stop_time
            ):
                puffed_lick = 1

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
                "date": date_time,
                "day_of_week": day_of_week,
                "absolute_time": absolute_datetime,
                "trial": trial,
                "session_time": t_sesh,
                "trial_time": t_trial,
                "message": msg,
                "is_session": is_session,
                "is_trial": is_trial,
                "trial_type": trial_type,
                "lick": lick,
                "puffed_lick": puffed_lick,
                "negative_signal": negative_signal,
                "positive_signal": positive_signal,
                "water": water,
            }
        )

    return pd.DataFrame(parsed_data)


def get_data_features_from_data_file(
    full_file: str,
    verbose: bool = False,
) -> tuple[list, pd.DataFrame]:
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
            print_bad_data_blobs=verbose,
        )
        if not df.empty:
            data_frames.append(df)

    # Files can contain multiple mouse/session pairs. Extract features
    # from each data frame (pair)
    data_features = []
    if not data_frames:
        return (data_features, pd.DataFrame())
    for df in data_frames:
        total_licks = df["lick"].sum()
        total_puffed_licks = df["puffed_lick"].sum()

        # Total licks by trial type, only during trial
        dft = df[df["is_trial"] == 1]
        total_licks_in_trial = dft["lick"].sum()
        total_puffed_licks_in_trial = dft["puffed_lick"].sum()
        df0 = df[df["trial_type"] == 0]
        df0 = df0[df0["is_trial"] == 1]
        total_licks_type_0 = df0["lick"].sum()
        total_puffed_licks_type_0 = df0["puffed_lick"].sum()
        df1 = df[df["trial_type"] == 1]
        df1 = df1[df1["is_trial"] == 1]
        total_licks_type_1 = df1["lick"].sum()
        total_puffed_licks_type_1 = df1["puffed_lick"].sum()

        # Total licks, water is on
        df_water = df[df["water"] == 1]
        total_licks_water_on = df_water["lick"].sum()
        total_puffed_licks_water_on = df_water["puffed_lick"].sum()
        df_water_t0 = df[df["water"] == 1]
        df_water_t0 = df_water_t0[df_water_t0["is_trial"] == 1]
        df_water_t0 = df_water_t0[df_water_t0["trial_type"] == 0]
        total_licks_water_on_type_0 = df_water_t0["lick"].sum()
        total_puffed_licks_water_on_type_0 = df_water_t0["puffed_lick"].sum()
        df_water_t1 = df[df["water"] == 1]
        df_water_t1 = df_water_t1[df_water_t1["is_trial"] == 1]
        df_water_t1 = df_water_t1[df_water_t1["trial_type"] == 1]
        total_licks_water_on_type_1 = df_water_t1["lick"].sum()
        total_puffed_licks_water_on_type_1 = df_water_t1["puffed_lick"].sum()

        # Some math
        z_total_licks_in_trial = total_licks_in_trial/total_licks
        z_total_licks_type_0 = total_licks_type_0/total_licks
        z_total_licks_type_1 = total_licks_type_1/total_licks
        z_total_licks_water_on_type_0 = total_licks_water_on_type_0/total_licks_water_on
        z_total_licks_water_on_type_1 = total_licks_water_on_type_1/total_licks_water_on
        # Puffed
        z_total_puffed_licks_in_trial = total_puffed_licks_in_trial/total_puffed_licks
        z_total_puffed_licks_type_0 = total_puffed_licks_type_0/total_puffed_licks
        z_total_puffed_licks_type_1 = total_puffed_licks_type_1/total_puffed_licks
        z_total_puffed_licks_water_on_type_0 = total_puffed_licks_water_on_type_0/total_puffed_licks_water_on
        z_total_puffed_licks_water_on_type_1 = total_puffed_licks_water_on_type_1/total_puffed_licks_water_on

        # Defining learning rate as the ratio of puffed licks in trial type0 to
        # licks in trial type1. Air puffs are delivered in type1 and as
        # the mouse learns type1 licks should go down (type0 up)
        z_learning_rate = z_total_puffed_licks_type_0/z_total_puffed_licks_type_1
        z_learning_rate_reward = z_total_puffed_licks_water_on_type_0/z_total_puffed_licks_water_on_type_1

        # It might be useful to clean these up
        data_features.append(
            {
                "mouse_id": df["mouse_id"].iloc[0],
                "session_id": df["session_id"].iloc[0],
                "day_of_week": df["day_of_week"].iloc[0],
                "total_licks": total_licks,
                "total_puffed_licks": total_puffed_licks,
                "total_licks_in_trial": total_licks_in_trial,
                "total_puffed_licks_in_trial": total_puffed_licks_in_trial,
                "z_total_licks_in_trial": z_total_licks_in_trial,
                "z_total_puffed_licks_in_trial": z_total_puffed_licks_in_trial,
                "total_licks_type_0": total_licks_type_0,
                "z_total_licks_type_0": z_total_licks_type_0,
                "z_total_puffed_licks_type_0": z_total_puffed_licks_type_0,
                "total_licks_type_1": total_licks_type_1,
                "z_total_licks_type_1": z_total_licks_type_1,
                "z_total_puffed_licks_type_1": z_total_puffed_licks_type_1,
                "total_licks_water_on": total_licks_water_on,
                "total_licks_water_on_type_0": total_licks_water_on_type_0,
                "z_total_licks_water_on_type_0": z_total_licks_water_on_type_0,
                "z_total_puffed_licks_water_on_type_0": z_total_puffed_licks_water_on_type_0,
                "total_licks_water_on_type_1": total_licks_water_on_type_1,
                "z_total_licks_water_on_type_1": z_total_licks_water_on_type_1,
                "z_total_puffed_licks_water_on_type_1": z_total_puffed_licks_water_on_type_1,
                "z_learning_rate": z_learning_rate,
                "z_learning_rate_reward": z_learning_rate_reward,
            }
        )
    return (
        data_features,
        pd.concat(data_frames).reset_index(drop=True),
    )


class Analysis:
    """
    Given a root data directory, extract features for an analysis. The data
    frame put to use in the analysis has the following columns:

        - Mouse ID
        - Session ID (date)
        - Features

    """
    # TODO: investigate if performance becomes an issue
    #
    #   - Extracting features into data frames, and not concatenating all
    #     data from all mice/sessions
    #   - At either point, storing processed data
    #
    # TODO: message folks about the files with mismatched mouse IDs
    #

    def __init__(self, *, data_root: str, verbose: bool=False) -> None:
        self.data_root = data_root
        self.verbose = verbose

        # From the entire data root directory, get the set of mouse IDs
        self.mouse_ids = get_mouse_ids(self.data_root)

        # Likewise, extract features from all of the data
        features = []
        data_frames = []
        for root, _, files in os.walk(self.data_root):
            for file in files:
                if is_data_file(file):
                    f_features, f_data_frames = get_data_features_from_data_file(
                        full_file=os.path.join(root, file),
                        verbose=self.verbose,
                    )
                    features += f_features
                    if not f_data_frames.empty:
                        data_frames.append(f_data_frames)
        self.df = pd.DataFrame(features)
        self.df = self.df.sort_values(by=["session_id", "mouse_id"])
        self.data = pd.concat(data_frames).reset_index(drop=True)

        # Session plotting hooks
        self.mouse_id_widget = widgets.Dropdown(
            options=sorted(list(self.data["mouse_id"].unique())),
            description="Mouse ID:",
            disabled=False,
        )
        self.session_id_widget = widgets.Dropdown(
            description="Session ID:",
            disabled=False,
        )
        self.plot_region_widget = widgets.Dropdown(
            options=["trial_type", "is_trial"],
            description="Plot Region:",
            disabled=False,
        )
        self.mouse_id_widget.observe(self.update_session_id_options, names="value")
        self.update_session_id_options()

    def info(self, df: pd.DataFrame) -> None:
        """
        Write some useful meta data about the analysis that can be used
        as a sanity check
        """
        df.info()

        print("Unique data categories:")
        builtin_print(f'- mouse_id: {df["mouse_id"].unique()}')
        builtin_print(f'- session_id: {df["session_id"].unique()}')
        builtin_print(f'- day_of_week: {df["day_of_week"].unique()}')
        builtin_print(f'- is_session: {df["is_session"].unique()}')
        builtin_print(f'- trial_type: {df["trial_type"].unique()}')
        builtin_print(f'- trial: {df["trial"].unique()}')
        builtin_print(f'- is_trial: {df["is_trial"].unique()}')
        builtin_print(f'- lick: {df["lick"].unique()}')
        builtin_print(f'- negative_signal: {df["negative_signal"].unique()}')
        builtin_print(f'- positive_signal: {df["positive_signal"].unique()}')
        builtin_print(f'- water: {df["water"].unique()}')
        builtin_print("")
        print("Value counts:")
        builtin_print(f'- mouse_id: {df["mouse_id"].value_counts()}')
        builtin_print(f'- session_id: {df["session_id"].value_counts()}')
        builtin_print(f'- day_of_week: {df["day_of_week"].value_counts()}')
        builtin_print(f'- is_session: {df["is_session"].value_counts()}')
        builtin_print(f'- trial_type: {df["trial_type"].value_counts()}')
        builtin_print(f'- trial: {df["trial"].value_counts()}')
        builtin_print(f'- is_trial: {df["is_trial"].value_counts()}')
        builtin_print(f'- lick: {df["lick"].value_counts()}')
        builtin_print(f'- negative_signal: {df["negative_signal"].value_counts()}')
        builtin_print(f'- positive_signal: {df["positive_signal"].value_counts()}')
        builtin_print(f'- water: {df["water"].value_counts()}')

    def summarize_licks_per_session(
        self,
        mouse_ids: list=[],
        min_session: int=0,
        water_on: bool=False,
        tail_length: Optional[int]=None,
    ) -> None:
        """
        Creates a bar plot showing licks per session and for each mouse.

        Args:
            mouse_ids: The set of mice to plot
            min_session: Filter sessions lower than this value
            water_on: Set to `True` to only consider licks when water
                reward is available
            tail_length: Set to an integer to only graph a tail of
                sessions with this length, e.g. set to `12` to only
                show the last 12 sessions
        """
        if not mouse_ids:
            mouse_ids = self.mouse_ids

        df = self.df.sort_values(by=["session_id", "mouse_id"])
        df = df[df["mouse_id"].isin(mouse_ids)]
        df = df[df["session_id"] > min_session]

        # Some filtering options
        if water_on:
            df = df[
                [
                    "mouse_id",
                    "session_id",
                    "z_total_licks_water_on_type_0",
                    "z_total_licks_water_on_type_1",
                ]
            ]
            df = df.rename(
                columns={
                    "z_total_licks_water_on_type_0": "type0",
                    "z_total_licks_water_on_type_1": "type1",
                },
            )
        else:
            df = df[
                [
                    "mouse_id",
                    "session_id",
                    "z_total_licks_type_0",
                    "z_total_licks_type_1",
                ]
            ]
            df = df.rename(
                columns={
                    "z_total_licks_type_0": "type0",
                    "z_total_licks_type_1": "type1",
                },
            )

        # Get a tail of sessions
        if tail_length:
            df = df.groupby(
                "mouse_id"
            ).apply(
                lambda x: x.sort_values("session_id").tail(tail_length)
            ).reset_index(
                drop=True
            )

        # Accounts for trial type
        df = df.melt(
            id_vars=["mouse_id", "session_id"],
            value_vars=["type0", "type1"],
            var_name="Type",
            value_name="Licks",
        )

        g = sns.FacetGrid(
            df,
            col="mouse_id",
            col_wrap=2,
            sharex=False,
            sharey=False,
            height=4,
            aspect=1,
        )
        g.map_dataframe(
            sns.barplot,
            x="session_id",
            y="Licks",
            hue="Type",
            errorbar=None,
        )
        g.add_legend(title="Lick Type")

        for ax in g.axes:
            if ax in g.axes[:-2]:
                ax.set_xticklabels("")
            else:
                ax.set_xticklabels(ax.get_xticklabels(), rotation=90)

        g.set_axis_labels("", "Total Licks")
        g.set_titles("Mouse: {col_name}")

        suptitle = "Total Licks Over Time by Mouse"

        plt.suptitle(suptitle, y=1.05)
        plt.show()

    def learning_rate_heat_map(
        self,
        mouse_ids: list=[],
        min_session: int=0,
        water_on: bool=False,
        tail_length: Optional[int]=None,
    ) -> None:
        # TODO: Need to align on the air puff day, which should be
        # Wednesday, which should be ... 7 and 8 in the current plot?
        # Can get this from the Cohort Info, may consider adding
        # it to the rig output

        if not mouse_ids:
            mouse_ids = self.mouse_ids

        df = self.df.sort_values(by=["session_id", "mouse_id"])
        df = df[df["mouse_id"].isin(mouse_ids)]
        df = df[df["session_id"] > min_session]

        # Some filtering options
        if water_on:
            df = df[
                [
                    "mouse_id",
                    "session_id",
                    "z_learning_rate",
                ]
            ]
            df = df.rename(
                columns={
                    "z_learning_rate": "learning_rate",
                },
            )
        else:
            df = df[
                [
                    "mouse_id",
                    "session_id",
                    "z_learning_rate_reward",
                ]
            ]
            df = df.rename(
                columns={
                    "z_learning_rate_reward": "learning_rate",
                },
            )

        # Get a tail of sessions
        if tail_length:
            def process_group(x):
                """
                Gets the tail of sessions and gives them an index
                """
                x = x.sort_values("session_id").tail(tail_length)
                x["session_id"] = range(1, tail_length + 1)
                return x
            df = df.groupby(
                "mouse_id"
            ).apply(
                process_group
            ).reset_index(
                drop=True
            )

        # This section does a bit of additional work with the learning
        # rate. It takes the log and replaces inf, -inf, nan values with
        # the max, min, and 0 values of the data frame
        df["learning_rate"] = np.log(df["learning_rate"])
        df = df.pivot(
            index="mouse_id", columns="session_id", values="learning_rate"
        )
        max_value = df.replace(np.inf, np.nan).max().max()
        min_value = df.replace(-1*np.inf, np.nan).min().min()
        df.replace(np.inf, max_value, inplace=True)
        df.replace(-1*np.inf, min_value, inplace=True)
        df.replace(np.nan, 0, inplace=True)
        vmin, vmax = df.min().min(), df.max().max()

        # Create the heatmap using Seaborn
        plt.figure(figsize=(10, 6))  # You can adjust the size to fit your needs
        sns.heatmap(
            df,
            annot=False,
            cmap="coolwarm",
            linewidths=0.5,
            vmin=vmin,
            vmax=vmax,
        )
        plt.title("Learning Rate Heatmap")
        plt.show()

        # Plots average learning rate across mice for the last set of sessions
        mean_learning_rate = df.mean(axis=0)
        plt.figure(figsize=(8, 6))
        plt.plot(mean_learning_rate.index, mean_learning_rate.values, marker="o", linestyle="-")
        plt.title("Average Learning Rate Across Mice")
        plt.xlabel("Session ID")
        plt.ylabel("Average Learning Rate")
        plt.grid(True)
        plt.xticks(range(1, len(mean_learning_rate.index) + 1))
        plt.show()

    def determine_significance(
        self,
        *,
        puff_map: dict,
        natural_logarithm: bool=False,
        drop_bad_rows: bool=True,
        metric_of_interest: str="z_learning_rate",
    ) -> None:
        learn = self.df.sort_values(by=["session_id", "mouse_id"])
        learn = learn[learn["mouse_id"].isin(list(puff_map.keys()))]
        print(f"Exploring significance between pre- and post-learning for '{metric_of_interest}'")
        learn = learn[
            [
                "mouse_id",
                "session_id",
                metric_of_interest,
            ]
        ]
        learn = learn.rename(
            columns={
                metric_of_interest: "learning_rate",
            },
        )

        # Use a date time for comparison with puff map
        learn["session_id"] = pd.to_datetime(learn["session_id"], format="%Y%m%d%H%M%S")

        # Data transformation options
        if natural_logarithm:
            learn["learning_rate"] = np.log(learn["learning_rate"])

        if drop_bad_rows:
            learn = learn.replace([np.inf, -np.inf], np.nan).dropna()
            learn = learn.pivot(
                index="mouse_id", columns="session_id", values="learning_rate"
            )
        else:
            learn = learn.pivot(
                index="mouse_id", columns="session_id", values="learning_rate"
            )
            max_value = learn.replace(np.inf, np.nan).max().max()
            min_value = learn.replace(-1*np.inf, np.nan).min().min()
            learn.replace(np.inf, max_value, inplace=True)
            learn.replace(-1*np.inf, min_value, inplace=True)
            learn.replace(np.nan, 0, inplace=True)

        # See if we can put each session learning rate into one of two buckets,
        # one pre-learning and one post-learning
        pre_learning_rates = set()
        post_learning_rates = set()
        for mouse_id in learn.index:
            for session_id in learn.columns:
                session_date = session_id.date()
                learning_rate = learn.at[mouse_id, session_id]
                if learning_rate == 0.0 or pd.isna(learning_rate):
                    continue

                for puff_day in puff_map[mouse_id]:
                    puff_date = puff_day.date()
                    puff_nearness = (session_date - puff_date).days
                    if puff_nearness in [-2, -1]:
                        pre_learning_rates.add(learning_rate)
                    if puff_nearness in [1, 2]:
                        post_learning_rates.add(learning_rate)

        alpha = 0.05
        x = list(pre_learning_rates)
        y = list(post_learning_rates)
        nx = len(x)
        ny = len(y)
        print(f"Found {nx} pre-learning sessions, {ny} post-learning")
        print(f"Pre-learning rates: {[round(xi, 3) for xi in x]}")
        print(f"Post-learning rates: {[round(yi, 3) for yi in y]}")
        mu_x = np.mean(x)
        mu_y = np.mean(y)
        sx = np.std(x, ddof=1)
        sy = np.std(y, ddof=1)
        t = (mu_x-mu_y)/np.sqrt(sx*sx/nx+sy*sy/ny)
        dof = nx+ny-2
        p = 2 * (1 - stats.t.cdf(abs(t), dof))

        if p < alpha:
            print(f"P-value {round(p, 2)} is less than {alpha}, significance!")
        else:
            print(f"P-value {round(p, 2)} is greater than alpha {alpha}, x and y are the same.")

    def update_session_id_options(self, *args, **kwargs) -> None:
        selected_mouse_id = self.mouse_id_widget.value
        session_ids = [
            int_session_id_to_date_string(d)
            for d in self.data[self.data["mouse_id"] == selected_mouse_id]["session_id"].unique()
        ]
        session_ids = sorted(list(set(session_ids)))
        self.session_id_widget.options = session_ids

    def interactive(self):
        display(
            widgets.interactive(
                self.interactive_session_display,
                data=self.data,
                mouse_id=self.mouse_id_widget,
                session_id=self.session_id_widget,
                plot_region=self.plot_region_widget,
            ),
        )

    def interactive_session_display(
        self,
        mouse_id: str,
        session_id: str,
        plot_region: str,
    ) -> None:
        """Plots the given session data

        Args:
            data: A Pandas `DataFrame` for the current analysis
            mouse_id: A string mouse ID
            session_id: A date-time string for the current session
            plot_region: Which region will the analysis plot?
        """
        date_id = session_id
        session_id = session_id.replace("-", "").replace("T", "").replace(":", "")

        # Filter the analysis data
        df = self.data
        df = df[df["mouse_id"] == mouse_id]
        df.loc[:, "session_id"] = df["session_id"].astype(str)
        df = df[df["session_id"].str.startswith(session_id)].copy()

        # Some data cleaning prior to plotting:
        #
        #   - Only consider once the session has started
        #   - Sort by session time
        #   - Add a `time` (based on session time) index for calculation
        #
        df = df[df["session_time"] > 0]
        df["session_time"] = df["session_time"] / 1000 / 60  # [min]
        df = df.sort_values(by="session_time")
        df = df[df["is_session"] == 1]
        df["time"] = pd.to_datetime(df["session_time"], unit="m")
        df.set_index("time", inplace=True)

        # Lick frequency calculation
        # The `window` is 1000ms (1s) in `session_time`
        df["lick_rate"] = df["lick"].rolling(window="1s", min_periods=1, center=True).sum()
        plt.figure(figsize=(15, 5))

        # Add background colors for whether it is a trial
        if plot_region == "is_trial":
            regions = []
            current_type = df["is_trial"].iloc[0]
            start_time = df["session_time"].iloc[0]
            for i in range(1, len(df)):
                if df["is_trial"].iloc[i] != current_type:
                    end_time = df["session_time"].iloc[i - 1]
                    regions.append((start_time, end_time, current_type))
                    start_time = df["session_time"].iloc[i]
                    current_type = df["is_trial"].iloc[i]
            end_time = df["session_time"].iloc[-1]
            regions.append((start_time, end_time, current_type))
            ax = plt.gca()
            for start_time, end_time, is_trial in regions:
                if is_trial == 0:
                    color = "lightgrey"
                elif is_trial == 1:
                    color = "lightblue"
                ax.axvspan(start_time, end_time, facecolor=color, alpha=0.5)
            legend_patches = [
                mpatches.Patch(color="lightgrey", alpha=0.5, label="I.T.I."),
                mpatches.Patch(color="lightblue", alpha=0.5, label="Trial"),
            ]

        # Add background colors for different trial types
        if plot_region == "trial_type":
            regions = []
            current_type = df["trial_type"].iloc[0]
            start_time = df["session_time"].iloc[0]
            for i in range(1, len(df)):
                if df["trial_type"].iloc[i] != current_type:
                    end_time = df["session_time"].iloc[i - 1]
                    regions.append((start_time, end_time, current_type))
                    start_time = df["session_time"].iloc[i]
                    current_type = df["trial_type"].iloc[i]
            end_time = df["session_time"].iloc[-1]
            regions.append((start_time, end_time, current_type))
            ax = plt.gca()
            for start_time, end_time, trial_type in regions:
                if trial_type == -1:
                    color = "lightgrey"
                elif trial_type == 0:
                    color = "lightcoral"
                elif trial_type == 1:
                    color = "lightblue"
                ax.axvspan(start_time, end_time, facecolor=color, alpha=0.5)
            legend_patches = [
                mpatches.Patch(color="lightgrey", alpha=0.5, label="I.T.I."),
                mpatches.Patch(color="lightcoral", alpha=0.5, label="Trial Type 0"),
                mpatches.Patch(color="lightblue", alpha=0.5, label="Trial Type 1"),
            ]

        plt.plot(
            df["session_time"],
            df["lick_rate"],
            label="Lick Rate",
            color="black",
            marker=".",
            linewidth=1,
        )
        plt.xlabel("Session Time [min]")
        plt.ylabel("Lick Rate [lick/s]")
        plt.title(f"Mouse: '{mouse_id}', Session: '{date_id}'")
        plt.legend(
            handles=legend_patches + [
                plt.Line2D([0], [0], color="black", label="Lick Rate")
            ],
            framealpha=1,
        )
        plt.grid(True)
        plt.show()

        trials = [0, 1, 2, 3, 4, 5]
        fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(15, 10))
        axes = axes.flatten()
        for trial in trials:
            trial_data = df[df["trial"] == trial]
            ax = axes[trial]
            ax.plot(
                trial_data["trial_time"],
                trial_data["lick_rate"],
                label="Lick Rate",
                color="black",
                marker=".",
                linewidth=1,
            )
            ax.set_xlabel("Trial Time [ms]")
            ax.set_ylabel("Lick Rate [lick/s]")
            ax.set_title(f"Trial: {trial+1}")
            if trial == 0:
                ax.legend(
                    handles=[plt.Line2D([0], [0], color="black", label="Lick Rate")],
                    framealpha=1,
                )
            ax.grid(True)
        plt.tight_layout()
        plt.show()
