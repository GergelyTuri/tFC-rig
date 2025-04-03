"""Data class dealing with the preprocessed session data."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd


@dataclass
class Session:
    """
    class for parsing json files that contain the preprocessed session data
    """

    session_path: Union[str, Path]
    _data: Dict[str, Any] = field(init=False, repr=False)

    def __post_init__(self):
        """
        Convert the session path to a Path object (if it's a string)
        and load JSON data into the _data attribute.
        """
        if isinstance(self.session_path, str):
            self.session_path = Path(self.session_path)
        self._data = self._load_json()

    def _load_json(self):
        """
        Read and parse the JSON file from the given path.
        """
        with open(self.session_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    @property
    def session_header(self) -> Dict[str, Any]:
        """
        Return the header of the session data.
        """
        return self._data["header"]

    @property
    def mouse_ids(self) -> List[str]:
        """
        Return the mouse IDs of the session data.
        """
        return self._data["header"]["mouse_ids"]

    @property
    def session_data(self) -> Dict[str, Any]:
        """
        Return the 'data' section of the JSON file.
        """
        return self._load_json()["data"]

    def get_mouse_session_data(self, mouse_id: str) -> Dict[str, Any]:
        """
        Return the session data for a specific mouse ID.

        :param mouse_id: A valid mouse ID found in self.mouse_ids.
        :return: A dictionary of session data for the specified mouse.
        """
        return self._data["data"][mouse_id]

    def get_session_metadata(self, mouse_id: str) -> Dict[str, Any]:
        """
        Collect metadata from the session events for a given mouse.
        This method will parse messages until it encounters a line that
        includes 'Session has started', at which point it will stop.

        :param mouse_id: A valid mouse ID present in self.mouse_ids.
        :return: A dictionary where keys and values are parsed from each message.
        """
        session_events = self.get_mouse_session_data(mouse_id)
        metadata = {}

        always_string_keys = {
            "trialTypesChar"
        }  # this/these will have to stay as string to prevent losing information

        for event in session_events:
            message = event.get("message", "")

            # If we've reached "Session has started", stop collecting metadata
            if "Session has started" in message:
                break

            # Example messages look like: "0: 141840: 0: BAUD_RATE: 9600"
            # We'll split by ": " and capture the last two parts as key/value.
            parts = message.split(": ")
            if len(parts) >= 4:
                # The second-to-last chunk is the key, and the last chunk is the value
                key = parts[-2].strip()  # e.g., "BAUD_RATE"
                value_str = parts[-1].strip()  # e.g., "9600"

                # Try converting the value to int or float if it's numeric
                value: Any
                if key in always_string_keys:
                    value = value_str
                else:
                    try:
                        value = int(value_str)
                    except ValueError:
                        try:
                            value = float(value_str)
                        except ValueError:
                            # If it can't be converted to a number, leave as string
                            value = value_str

                metadata[key] = value

        return metadata

    def get_post_start_events(
        self, mouse_id: str, events_of_interest: List[str] = None
    ) -> pd.DataFrame:
        """
        Return a DataFrame of selected time-stamped events that appear
        after the line 'Session has started'.

        :param mouse_id: Mouse ID for which to parse event data.
        :param events_of_interest: A list of events to filter on. If not provided,
                                a default list is used.
        :return: A pandas DataFrame with columns [mouse_id, port, absolute_time, event].
        """
        # Default events if none provided
        if events_of_interest is None:
            events_of_interest = [
                "Lick",
                "Water on",
                "Water off",
                "Negative signal start",
                "Negative signal stop",
                "Positive signal start",
                "Positive signal stop",
                "Trial has started",
                "Trial has ended",
            ]

        session_events = self.get_mouse_session_data(mouse_id)

        # We'll start collecting once we see the "Session has started" message
        start_collecting = False

        # This will store our rows before we make a DataFrame
        records = []

        for event in session_events:
            message = event.get("message", "")

            # Check if we've reached the "Session has started"
            if "Session has started" in message:
                # Once this message is encountered, begin collecting subsequent events
                start_collecting = True
                continue

            # If we haven't seen "Session has started" yet, skip
            if not start_collecting:
                continue

            # Now parse events after "Session has started"
            # Messages typically look like "0: 145804: 2418: Lick"
            # The final colon-separated part is usually the event description
            parts = message.split(": ")

            # We only care about the events from `events_of_interest`
            if len(parts) >= 4:
                event_name = parts[-1].strip()

                if event_name in events_of_interest:
                    # Build a record with relevant fields
                    records.append(
                        {
                            "mouse_id": event.get("mouse_id"),
                            "port": event.get("port"),
                            "absolute_time": event.get("absolute_time"),
                            "event": event_name,
                        }
                    )

        # Convert our collected records into a DataFrame for easy manipulation
        df = pd.DataFrame(
            records, columns=["mouse_id", "port", "absolute_time", "event"]
        )
        return df

    def get_trial_events(self, mouse_id: str) -> pd.DataFrame:
        """
        Parse the session data at the trial level for a given mouse.
        Returns a DataFrame with columns:
            ["mouse_id", "trial_number", "absolute_time",
            "trial_time", "event", "trial_type"].

        We look for lines containing:
        - 'Trial has started'
        - 'Trial has ended'
        and anything in between. We also look for 'currentTrialType: X'
        to capture the trial type.

        :param mouse_id: The mouse ID to parse.
        :return: A pandas DataFrame of trial-level events.
        """
        session_events = self.get_mouse_session_data(mouse_id)

        # This will hold our final rows for ALL trials
        all_records: List[Dict[str, Any]] = []

        # Temporary structure to hold the current trial data
        # until we see 'Trial has ended'
        current_trial = (
            None  # Will be a dict with keys: trial_number, trial_type, events
        )

        for event in session_events:
            msg = event.get("message", "")
            parts = msg.split(": ")

            # We expect something like: "6: 584376: 0: Trial has started"
            # parts = ["6", "584376", "0", "Trial has started"] (or more if there's a colon in the last chunk)
            if len(parts) < 4:
                # Doesn't match the expected "trial_number: session_ms: trial_ms: event"
                continue

            trial_number_str, session_ms_str, trial_ms_str = (
                parts[0],
                parts[1],
                parts[2],
            )

            # Join anything beyond the 3rd chunk to form the event string
            # E.g., "Trial has started" or "currentTrialType: 2"
            event_text = ": ".join(parts[3:]).strip()

            # Attempt to convert those first three parts to integers
            try:
                trial_number = int(trial_number_str)
                session_ms = int(session_ms_str)
                trial_ms = int(trial_ms_str)
            except ValueError:
                # If they don't parse as integers, skip
                continue

            # -- Check for "Trial has started" --
            if event_text == "Trial has started":
                # If we were already in a trial, we close it out first
                # (in case the data is malformed; else we can ignore it)
                if current_trial is not None:
                    # This would be unusual, but you can decide how to handle
                    self._finalize_trial(current_trial, all_records, mouse_id)

                # Begin a new trial
                current_trial = {
                    "trial_number": trial_number,
                    "trial_type": None,  # Will fill in later if we see "currentTrialType"
                    "events": [],
                }

                # Store the 'Trial has started' event itself
                current_trial["events"].append(
                    {
                        "absolute_time": event["absolute_time"],
                        "trial_time": trial_ms,
                        "event": "Trial has started",
                    }
                )
                continue

            # If we're not currently in a trial, ignore events until next "Trial has started"
            if current_trial is None:
                continue

            # -- Check for "currentTrialType: X" --
            if event_text.startswith("currentTrialType: "):
                # E.g., "currentTrialType: 2"
                trial_type_str = event_text.split("currentTrialType: ")[1].strip()
                try:
                    current_trial["trial_type"] = int(trial_type_str)
                except ValueError:
                    # If it can't parse to int, store it as string
                    current_trial["trial_type"] = trial_type_str

                # Optionally store the "currentTrialType" as an event row, if desired:
                current_trial["events"].append(
                    {
                        "absolute_time": event["absolute_time"],
                        "trial_time": trial_ms,
                        "event": f"currentTrialType: {trial_type_str}",
                    }
                )
                continue

            # -- Check for "Trial has ended" --
            if event_text == "Trial has ended":
                # Record the 'Trial has ended' event
                current_trial["events"].append(
                    {
                        "absolute_time": event["absolute_time"],
                        "trial_time": trial_ms,
                        "event": "Trial has ended",
                    }
                )
                # Finalize this trial: store all events with known trial_number, trial_type, etc.
                self._finalize_trial(current_trial, all_records, mouse_id)
                current_trial = None  # reset for the next trial
                continue

            # -- Otherwise, it's a normal event (Lick, Water on, Water off, etc.) --
            current_trial["events"].append(
                {
                    "absolute_time": event["absolute_time"],
                    "trial_time": trial_ms,
                    "event": event_text,
                }
            )

        # If the file ends but a trial never ended,
        # you can decide if you want to finalize it anyway:
        if current_trial is not None:
            self._finalize_trial(current_trial, all_records, mouse_id)

        # Build a DataFrame
        df = pd.DataFrame(
            all_records,
            columns=[
                "mouse_id",
                "trial_number",
                "absolute_time",
                "trial_time",
                "event",
                "trial_type",
            ],
        )
        return df

    def compute_lick_metrics_all_mice(self) -> pd.DataFrame:
        """
        Computes lick metrics for all mice in the session.

        Returns:
            A DataFrame where each row is a trial,
            with licks metrics and associated mouse id
        """
        all_results = []

        for mouse_id in self.mouse_ids:
            # get trial events
            trial_df = self.get_trial_events(mouse_id)

            # get metadata
            metadata = self.get_session_metadata(mouse_id)

            # compute metrics
            trial_obj = Trial(trial_df, metadata)
            metrics_df = trial_obj.compute_lick_metrics()

            # add mouse_id
            metrics_df["mouse_id"] = mouse_id
            all_results.append(metrics_df)

        return pd.concat(all_results, ignore_index=True)

    @staticmethod
    def _finalize_trial(
        trial_dict: Dict[str, Any],
        master_list: List[Dict[str, Any]],
        mouse_id: str,
    ) -> None:
        """
        Helper function to dump the events of a single trial into the master record list.
        """
        trial_number = trial_dict["trial_number"]
        trial_type = trial_dict["trial_type"]

        for evt in trial_dict["events"]:
            master_list.append(
                {
                    "mouse_id": mouse_id,
                    "trial_number": trial_number,
                    "absolute_time": evt["absolute_time"],
                    "trial_time": evt["trial_time"],
                    "event": evt["event"],
                    "trial_type": trial_type,
                }
            )


@dataclass
class Trial:
    """
    class for dealing with the trial data.
    """

    trial_df: pd.DataFrame = field(repr=False)
    _session_metadata: Dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        """
        Ensures tha the input DataFrame contains the required columns
        """

        required_columns = {
            "mouse_id",
            "absolute_time",
            "event",
            "trial_number",
            "trial_time",
            "trial_type",
        }

        missing_cols = required_columns - set(self.trial_df.columns)

        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        self.trial_df = self.trial_df.sort_values(
            by=["mouse_id", "trial_number", "trial_time"]
        ).reset_index(drop=True)

    def set_metadata(self, session_metadata: Dict[str, Any]):
        self._session_metadata = session_metadata

    @property
    def pre_tone_duration(self) -> int:
        """
        Return the duration of the pre-tone period in milliseconds.
        """
        return self._session_metadata.get("AUDITORY_START", 0)

    @property
    def tone_duration(self) -> int:
        return max(
            0, self._session_metadata.get("AUDITORY_STOP", 0) - self.pre_tone_duration
        )

    @property
    def trace_duration(self) -> int:
        return max(
            0,
            self._session_metadata.get("AIR_PUFF_START_TIME", 0)
            - self._session_metadata.get("AUDITORY_STOP", 0),
        )

    @property
    def post_trace_duration(self) -> int:
        return max(0, self._session_metadata.get("AIR_PUFF_TOTAL_TIME", 0))

    def get_absolute_licks_per_trial(self) -> pd.DataFrame:
        """
        Return a DataFrame with the total lick times for each trial.
        """
        return (
            self.trial_df[self.trial_df["event"] == "Lick"]
            .groupby("trial_number")
            .size()
        )

    def get_average_licks_per_trial(self) -> float:
        """
        Returns the average number of licks per trial.
        """
        lick_counts = self.get_absolute_licks_per_trial()
        return lick_counts.mean() if not lick_counts.empty else 0.0

    def get_lick_rate_per_trial(self) -> pd.DataFrame:
        """
        Return a DataFrame with the lick rate for each trial.
        """
        lick_counts = self.get_absolute_licks_per_trial()
        trial_duration = self.trial_df.groupby("trial_number")["trial_time"].max()
        return (lick_counts / trial_duration).fillna(0)

    def get_avg_interlick_interval(self) -> pd.Series:
        """
        Returns the average interlick interval (ms) for each trial.
        Interlick Interval (ILI) = time difference between consecutive "Lick"
        """
        lick_events = self.trial_df[self.trial_df["event"] == "Lick"].copy()
        # get trail specific interlick intervals
        lick_events["interlick_interval"] = lick_events.groupby("trial_number")[
            "trial_time"
        ].diff()
        # calculate average interlick interval
        return (
            lick_events.groupby("trial_number")["interlick_interval"].mean().fillna(0)
        )

    def get_first_lick_time(self) -> pd.Series:
        """
        Returns the time of the first lick (ms) in each trial.
        """
        lick_events = self.trial_df[self.trial_df["event"] == "Lick"].copy()

        return lick_events.groupby("trial_number")["trial_time"].first()

    def compute_lick_metrics(self) -> pd.DataFrame:
        """
        Computes lick counts, normalized licks,
        and durations for each trial period:
        'pre-tone', 'tone', 'trace', and 'post_trace'.

        Normalization method:
        Licks in each period are divided by the licks in the 'pre-tone' period.

        Duration calculation:
        - 'pre-tone': AUDITORY_START
        - 'tone': AUDITORY_STOP - AUDITORY_START
        - 'trace': AIR_PUFF_START_TIME - AUDITORY_STOP
        - 'post_trace': AIR_PUFF_TOTAL_TIME

        :return: DataFrame where each row represents a trial
                 with lick counts, normalized licks, and durations.
        """

        # # Extract timing information from session metadata
        # pre_tone_duration = session_metadata.get("AUDITORY_START", 0)
        # tone_duration = session_metadata.get("AUDITORY_STOP", 0) - pre_tone_duration
        # trace_duration = session_metadata.get(
        #     "AIR_PUFF_START_TIME", 0
        # ) - session_metadata.get("AUDITORY_STOP", 0)
        # post_trace_duration = session_metadata.get("AIR_PUFF_TOTAL_TIME", 0)

        # # Ensure no negative durations
        # tone_duration = max(0, tone_duration)
        # trace_duration = max(0, trace_duration)
        # post_trace_duration = max(0, post_trace_duration)

        # Extract timing information
        pre_tone_duration = self.pre_tone_duration
        tone_duration = self.tone_duration
        trace_duration = self.trace_duration
        post_trace_duration = self.post_trace_duration

        # get time stamps
        pre_tone_end = pre_tone_duration
        tone_end = pre_tone_end + tone_duration
        trace_end = tone_end + trace_duration

        # Store results for each trial
        trial_results = []

        # Iterate over trials
        for trial_number, trial_data in self.trial_df.groupby("trial_number"):

            trial_data = trial_data.sort_values("trial_time").reset_index(drop=True)

            trial_type = trial_data["trial_type"].iloc[0]

            # Count licks in each period based on `trial_time`
            pre_tone_licks = (
                (trial_data["event"] == "Lick")
                & (trial_data["trial_time"] < pre_tone_end)
            ).sum()

            tone_licks = (
                (trial_data["event"] == "Lick")
                & (trial_data["trial_time"] >= pre_tone_end)
                & (trial_data["trial_time"] < tone_end)
            ).sum()

            trace_licks = (
                (trial_data["event"] == "Lick")
                & (trial_data["trial_time"] >= tone_end)
                & (trial_data["trial_time"] < trace_end)
            ).sum()

            post_trace_licks = (
                (trial_data["event"] == "Lick")
                & (trial_data["trial_time"] >= trace_end)
            ).sum()

            rewards = []
            current_reward = None
            trial_duration = self._session_metadata.get("TRIAL_DURATION", 0)
            water_dispense_time = self._session_metadata.get("WATER_DISPENSE_TIME", 0)

            # Find all rewards in the trial
            for _, row in trial_data.iterrows():
                if row["event"] == "Water on":
                    current_reward = row["trial_time"]
                elif row["event"] == "Water off" and current_reward is not None:
                    rewards.append((current_reward, row["trial_time"]))
                    current_reward = None

            if current_reward is not None:
                expected_off = current_reward + water_dispense_time
                if expected_off > trial_duration:
                    rewards.append((current_reward, min(expected_off, trial_duration)))

            pre_tone_rewards = sum(1 for start, end in rewards if start < pre_tone_end)
            tone_rewards = sum(
                1 for start, end in rewards if pre_tone_end <= start < tone_end
            )
            trace_rewards = sum(
                1 for start, end in rewards if tone_end <= start < trace_end
            )
            post_trace_rewards = sum(1 for start, end in rewards if trace_end <= start)

            # Count rewarded licks (licks between Water on and Water off, these are raw counts)
            pre_tone_rewarded_licks = tone_rewarded_licks = 0
            trace_rewarded_licks = post_trace_rewarded_licks = 0

            for _, row in trial_data.iterrows():
                if row["event"] == "Lick":
                    for water_on, water_off in rewards:
                        if water_on < row["trial_time"] < water_off:
                            if row["trial_time"] < pre_tone_end:
                                pre_tone_rewarded_licks += 1
                            elif row["trial_time"] < tone_end:
                                tone_rewarded_licks += 1
                            elif row["trial_time"] < trace_end:
                                trace_rewarded_licks += 1
                            else:
                                post_trace_rewarded_licks += 1
                            break

            # Normalize licks by pre-tone licks (avoid division by zero)
            ## Avoid division by zero
            norm_factor = pre_tone_licks if pre_tone_licks > 0 else 1
            if pre_tone_licks == 0:
                print(
                    f"""
                      Warning: Trial {trial_number} has 0 pre-tone licks! Normalizing with 1 instead.
                      """
                )
            normalized_tone_licks = tone_licks / norm_factor
            normalized_trace_licks = trace_licks / norm_factor
            normalized_post_trace_licks = post_trace_licks / norm_factor

            tone = (
                "cs+"
                if trial_type in [1, 2]
                else "cs-" if trial_type in [0, 3] else "no_signal"
            )
            puff = "puff" if trial_type in [1, 3] else "no_puff"

            # Append results
            trial_results.append(
                {
                    "trial_number": trial_number,
                    "tone": tone,
                    "airpuff": puff,
                    "pre_tone_licks": pre_tone_licks,
                    "tone_licks": tone_licks,
                    "trace_licks": trace_licks,
                    "post_trace_licks": post_trace_licks,
                    "norm_tone_licks": normalized_tone_licks,
                    "norm_trace_licks": normalized_trace_licks,
                    "norm_post_trace_licks": normalized_post_trace_licks,
                    "pre_tone_duration": pre_tone_duration / 1000,
                    "tone_duration": tone_duration / 1000,
                    "trace_duration": trace_duration / 1000,
                    "post_trace_duration": post_trace_duration / 1000,
                    "pre_tone_rewards": pre_tone_rewards,
                    "tone_rewards": tone_rewards,
                    "trace_rewards": trace_rewards,
                    "post_trace_rewards": post_trace_rewards,
                    "pre_tone_rewarded_licks": pre_tone_rewarded_licks,
                    "tone_rewarded_licks": tone_rewarded_licks,
                    "trace_rewarded_licks": trace_rewarded_licks,
                    "post_trace_rewarded_licks": post_trace_rewarded_licks,
                }
            )

        # Convert results into a DataFrame
        return pd.DataFrame(trial_results)

    def compute_lick_delays(self) -> pd.DataFrame:
        """
        Computes the delay (latency) of the first lick in each trial period
            ('pre-tone', 'tone', 'trace', 'post_trace').

        - 'delay_from_trial_start':
                    Time of the first lick relative to the trial start.
        - 'delay_from_period_start':
                    Time of the first lick relative to the period start.

        :return: DataFrame where each row represents
                        a trial with lick delays for each period.
        """

        # # Extract timing information
        # pre_tone_start = 0  # Always starts at 0
        # pre_tone_duration = session_metadata.get("AUDITORY_START", 0)
        # tone_start = pre_tone_duration
        # tone_duration = session_metadata.get("AUDITORY_STOP", 0) - tone_start
        # trace_start = session_metadata.get("AUDITORY_STOP", 0)
        # trace_duration = session_metadata.get(
        #     "AIR_PUFF_START_TIME", 0
        # ) - session_metadata.get("AUDITORY_STOP", 0)
        # post_trace_start = session_metadata.get("AIR_PUFF_START_TIME", 0)
        # post_trace_duration = session_metadata.get("AIR_PUFF_TOTAL_TIME", 0)

        # # Ensure no negative durations
        # tone_duration = max(0, tone_duration)
        # trace_duration = max(0, trace_duration)
        # post_trace_duration = max(0, post_trace_duration)

        pre_tone_start = 0  # Always starts at 0
        pre_tone_duration = self.pre_tone_duration
        tone_start = pre_tone_duration
        tone_duration = self.tone_duration
        trace_start = tone_start + tone_duration
        trace_duration = self.trace_duration
        post_trace_start = trace_start + trace_duration
        post_trace_duration = self.post_trace_duration

        # Store results per trial
        trial_results = []

        for trial_number, trial_data in self.trial_df.groupby("trial_number"):
            # Find first lick time in each period
            pre_tone_first_lick = trial_data.loc[
                (trial_data["event"] == "Lick")
                & (trial_data["trial_time"] < pre_tone_duration),
                "trial_time",
            ].min()

            tone_first_lick = trial_data.loc[
                (trial_data["event"] == "Lick")
                & (trial_data["trial_time"] >= tone_start)
                & (trial_data["trial_time"] < tone_start + tone_duration),
                "trial_time",
            ].min()

            trace_first_lick = trial_data.loc[
                (trial_data["event"] == "Lick")
                & (trial_data["trial_time"] >= trace_start)
                & (trial_data["trial_time"] < trace_start + trace_duration),
                "trial_time",
            ].min()

            post_trace_first_lick = trial_data.loc[
                (trial_data["event"] == "Lick")
                & (trial_data["trial_time"] >= post_trace_start),
                "trial_time",
            ].min()

            # Compute delay from trial start
            pre_tone_delay_from_trial_start = (
                pre_tone_first_lick if pd.notna(pre_tone_first_lick) else None
            )

            tone_delay_from_trial_start = (
                tone_first_lick if pd.notna(tone_first_lick) else None
            )

            trace_delay_from_trial_start = (
                trace_first_lick if pd.notna(trace_first_lick) else None
            )

            post_trace_delay_from_trial_start = (
                post_trace_first_lick if pd.notna(post_trace_first_lick) else None
            )

            # Compute delay from period start
            pre_tone_delay_from_period_start = pre_tone_delay_from_trial_start

            tone_delay_from_period_start = (
                (tone_first_lick - tone_start) if pd.notna(tone_first_lick) else None
            )

            trace_delay_from_period_start = (
                (trace_first_lick - trace_start) if pd.notna(trace_first_lick) else None
            )

            post_trace_delay_from_period_start = (
                (post_trace_first_lick - post_trace_start)
                if pd.notna(post_trace_first_lick)
                else None
            )

            # Append results
            trial_results.append(
                {
                    "trial_number": trial_number,
                    "pre_tone_delay_from_trial_start": pre_tone_delay_from_trial_start,
                    "tone_delay_from_trial_start": tone_delay_from_trial_start,
                    "trace_delay_from_trial_start": trace_delay_from_trial_start,
                    "post_trace_delay_from_trial_start": post_trace_delay_from_trial_start,
                    "pre_tone_delay_from_period_start": pre_tone_delay_from_period_start,
                    "tone_delay_from_period_start": tone_delay_from_period_start,
                    "trace_delay_from_period_start": trace_delay_from_period_start,
                    "post_trace_delay_from_period_start": post_trace_delay_from_period_start,
                }
            )

        return pd.DataFrame(trial_results)

    # the class should have methods for calculating the following:
    # - different filters for the trials e.g., more than 5 licks, less then 5 licks etc.
    # - methods for plotting the lick data
