"""Data class dealing with the preprocessed session data."""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Union

import numpy as np
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
