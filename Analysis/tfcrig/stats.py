### want to have three levels of stats/analysis classes
# 1. at cohort level: could have methods to compare between cohorts to see comparisons between different protocols
# 2. within cohort at session level: methods for comparing different sessions within a cohort
# 3. within session at subject level: methods for comparing different subjects/conditions over trial
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re


class Session:
    """
    class for dealing with data from single session,
    containing all trials and all animals within cohort
    """

    def __init__(self, data: pd.DataFrame):
        unique_sessions = data["session_id"].unique()
        if len(unique_sessions) != 1:
            raise ValueError(f"Expected one session, found {unique_sessions}")

        self.session_id = unique_sessions[0]

        df = data.copy()
        df["norm_lick_rate"] = (df["tone_licks"] / df["tone_duration"]) / (
            np.where(df["pre_tone_licks"] == 0, 1, df["pre_tone_licks"])
            / df["pre_tone_duration"]
        )
        self.data = df
        self.subjects = self.data["mouse_id"].unique().tolist()
        self.trials = self.data["trial_number"].unique().tolist()

    def plot_over_trials(
        self,
        y: str,
        x: str = "trial_number",
        hue: str = "mouse_id",
        title: str = None,
        ylabel: str = None,
        figsize=(10, 6),
    ):
        """
        Line plot to visualize changes over trials

        :param y: y-axis variable
        :param x: x-axis variable (default is trial number)
        """

        plt.figure(figsize=figsize)
        sns.lineplot(data=self.data, x=x, y=y, hue=hue)
        plt.title(title or f"{y} over {x} in {self.session_id}")
        plt.ylabel(ylabel or y)
        plt.xlabel(x)
        plt.legend(loc="lower left", bbox_to_anchor=(1.0, 0.5), ncol=2, title=hue)
        plt.tight_layout(rect=[0, 0, 0.85, 1])  # leaves space for legend on the right
        plt.show()

    def plot_trial_stages(
        self,
        stage_vars: dict,
        hue: str = "mouse_id",
        ylabel: str = "Lick Metric",
        title: str = None,
        agg: str = "mean",
        figsize=(8, 5),
    ):
        """
        Plot behavior across different trial stages (e.g., pre_tone, tone, trace, post_trace)

        Args:
            stage_vars: dict mapping stage names (x-axis) to column names in data
                e.g., {'Pre-tone': 'norm_pre_tone_licks', 'Tone': 'norm_tone_licks', ...}
            hue: column used to color/group lines (e.g., 'mouse_id', 'tone')
            ylabel: label for y-axis
            title: plot title
            agg: aggregation method ('mean' or 'median')
            figsize: figure size
        """

        long_df = []
        for stage, col in stage_vars.items():
            temp = self.data[[hue, col]].copy()
            temp = temp.rename(columns={col: "value"})
            temp["stage"] = stage
            long_df.append(temp)
        long_df = pd.concat(long_df)

        grouped = long_df.groupby([hue, "stage"])["value"]
        if agg == "mean":
            long_df = grouped.mean().reset_index()
        elif agg == "median":
            long_df = grouped.median().reset_index()
        else:
            raise ValueError("Only 'mean' and 'median' aggregations are supported.")

        plt.figure(figsize=figsize)
        sns.lineplot(
            data=long_df,
            x="stage",
            y="value",
            hue=hue,
            marker="o",
            err_style="bars",
            errorbar=("se", 2),
        )
        plt.ylabel(ylabel)
        plt.title(
            title or f"{agg.capitalize()} {ylabel} per Stage in {self.session_id}"
        )
        plt.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), ncol=2, title=hue)
        plt.tight_layout(rect=[0, 0, 0.85, 1])
        plt.show()


class Cohort:
    """
    class for dealing with data from single cohort,
    containing multiple sessions and all animals within cohort
    """

    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()

        required = {"session_id", "mouse_id", "trial_number"}
        missing = required - set(data.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        self.sessions = self.data["session_id"].unique().tolist()
        self.subjects = self.data["mouse_id"].unique().tolist()

    def realign_trials_by_session_order(self, session_order: list):
        """
        Adjusts trial_number across sessions to ensure continuous indexing
        based on defined session order.

        Args:
            session_order: list of session type prefixes in desired order
                e.g., ['lick_training', 'pre_learning', 'learning', 'post_learning']
        """

        df = self.data.copy()
        df["original_trial_number"] = df["trial_number"].astype(int)

        # Helper: extract base session type and day
        def parse_session(s):
            for idx, prefix in enumerate(session_order):
                if s.startswith(prefix):
                    match = re.search(r"d(\d+)", s)
                    day = int(match.group(1)) if match else 0
                    return (idx, day)
            return (len(session_order), 0)

        session_sort_keys = {s: parse_session(s) for s in df["session_id"].unique()}

        # Sort session_id values by order + day
        sorted_sessions = sorted(
            session_sort_keys.keys(), key=lambda x: session_sort_keys[x]
        )

        # Apply trial reindexing
        new_df_parts = []
        trial_offset = 0
        for sess_id in sorted_sessions:
            sess_df = df[df["session_id"] == sess_id].copy()
            sess_df["trial_number"] = sess_df["original_trial_number"] + trial_offset
            trial_offset += (
                sess_df["original_trial_number"].max() + 1
            )  # ensure no overlaps
            new_df_parts.append(sess_df)

        self.data = pd.concat(new_df_parts, ignore_index=True)

    def get_mouse(self, mouse_id: str) -> pd.DataFrame:
        """return all session data fpr a single or a set of mice"""
        return self.data[self.data["mouse_id"] == mouse_id]

    def compute_reward_success_rate(
        self,
        reward_col: str = "post_trace_reward",
        groupby_cols: list = ["mouse_id", "session_id"],
    ) -> pd.DataFrame:
        """
        Computes the percent of trials where a reward was delivered (non-zero)
        for each mouse for each group defined by 'groupby_cols'.

        Args:
            reward_col: column name indicating reward counts
            groupby_cols: columns to group by (default is ['mouse_id', 'session_id'])

        Returns:
            DataFrame with columns: groupby_cols + ['reward_success_rate']
        """
        grouped = self.data.groupby(groupby_cols)[reward_col]
        result = grouped.apply(lambda x: (x != 0).mean() * 100).reset_index(
            name=f"{reward_col}_success_rate"
        )
        return result
