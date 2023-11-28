"""This is a class for helper fuctions for processing behavior data.
11/28/23 adding header info to the class"""

import json
from dataclasses import dataclass, field

import matplotlib.pyplot as plt
import pandas as pd


@dataclass
class Processing:
    file: str
    header: dict = field(init=False)
    session_data: dict = field(init=False)
    trials: list = field(init=False)

    def __post_init__(self):
        self.header, self.session_data = self.load_data()
        self.trials = list(self.session_data.keys())

    def load_data(self):
        """
        Load data from a file.

        Returns:
            dict: The loaded data.
        """
        with open(self.file, "r", encoding="cp1252") as f:
            content = json.load(f)
            header = content.get("header", {})
            session_data = content.get("data", {})
        return header, session_data

    def prepropcess_trial(self, trial):
        """
        Preprocesses a trial by extracting relevant information from the trial data.

        Args:
            trial (str): The trial number as represented in `self.trials` (e.g.:"Trial_1").

        Returns:
            tuple: A tuple containing the preprocessed trial data (DataFrame) and the trial type (str).

        Raises:
            ValueError: If the trial type is not found in the trial data.
        """
        trial_df = pd.DataFrame.from_dict(self.session_data[trial])
        trial_type = None

        for message in trial_df["message"]:
            if "currentTrialType" in message:
                _, trial_type = message.split(":")
                trial_type = trial_type.strip()
                break

        if trial_type is None:
            raise ValueError("Trial type not found")

        trial_df["negative_signal_start"] = trial_df["message"].str.contains(
            "Negative signal start"
        )
        trial_df["negative_signal_end"] = trial_df["message"].str.contains(
            "Negative signal stop"
        )
        trial_df["positive_signal_start"] = trial_df["message"].str.contains(
            "Positive signal start"
        )
        trial_df["positive_signal_end"] = trial_df["message"].str.contains(
            "Positive signal stop"
        )
        trial_df["negative_signal"] = trial_df["message"].str.contains(
            "Negative signal start" or "Negative signal end"
        )
        trial_df["airpuff_start"] = trial_df["message"].str.contains("Puff start")
        trial_df["airpuff_end"] = trial_df["message"].str.contains("Puff stop")
        trial_df["lick"] = trial_df["message"].str.contains("Lick")
        trial_df["water"] = trial_df["message"].str.contains("Water on" or "Water off")
        trial_df["time"] = pd.to_datetime(trial_df["trial_millis"], unit="ms")
        trial_df.set_index("time", inplace=True)
        return trial_df, trial_type

    def plot_trial(self, trial, ax=None):
        """
        Plots the trial data.

        Parameters:
        - trial (str): The trial number as represented in `self.trials` (e.g.:"Trial_1").
        - ax (matplotlib.axes.Axes, optional): The axes to plot on. If not provided, a new figure and axes will be created.

        Returns:
        - ax (matplotlib.axes.Axes): The plotted axes.
        """
        if ax is None:
            _, ax = plt.subplots()
        trial_df, trial_type = self.prepropcess_trial(trial)
        # Identifying and plotting Negative Signal Periods
        negative_start_times = trial_df.index[trial_df["negative_signal_start"]]
        negative_end_times = trial_df.index[trial_df["negative_signal_end"]]
        air_puff_start_times = trial_df.index[trial_df["airpuff_start"]]
        air_puff_end_times = trial_df.index[trial_df["airpuff_end"]]

        trial_df["lick"].resample("1L").sum().plot(ax=ax)
        trial_df["water"].resample("1L").sum().plot(ax=ax, color="k")

        for start, end in zip(negative_start_times, negative_end_times):
            ax.fill_betweenx(y=[0, 1], x1=start, x2=end, color="red", alpha=0.2)

        for start, end in zip(air_puff_start_times, air_puff_end_times):
            ax.fill_betweenx(y=[0, 1], x1=start, x2=end, color="grey", alpha=0.5)

        ax.set_yticks([0, 1], ["No Lick", "Lick"])
        ax.set_ylabel("Event (1 if Lick/Water Present)")
        ax.set_xlabel("Time (s)")
        ax.set_title(f"Trial#: {trial}, Trial type: {trial_type}")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        return ax

    def plot_session(self):
        """
        Plot the session data.

        Returns:
            fig (matplotlib.figure.Figure): The generated figure object.
            axes (numpy.ndarray): The array of axes objects.
        """
        mouse_id = self.header["mouse_id"]
        start_time = self.header["Start_time"]
        fig, axes = plt.subplots(
            nrows=2, ncols=3, figsize=(15, 10), sharex=True, sharey=True
        )  # Adjust figsize as needed
        fig.suptitle(f"ID: {mouse_id}, Start time: {start_time}")

        # Flatten the axes array for easy iteration
        axes = axes.flatten()

        for i, trial in enumerate(self.trials, start=1):
            ax = axes[i - 1]
            self.plot_trial(trial, ax=ax)

        # Adjust layout to prevent overlapping
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)  # Adjust as needed for suptitle

        return fig, axes
