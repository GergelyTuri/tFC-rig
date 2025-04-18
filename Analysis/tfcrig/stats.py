### want to have three levels of stats/analysis classes
# 1. at cohort level: could have methods to compare between cohorts to see comparisons between different protocols
# 2. within cohort at session level: methods for comparing different sessions within a cohort
# 3. within session at subject level: methods for comparing different subjects/conditions over trial
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re

from tfcrig.google_drive import GoogleDrive


def load_metadata_from_google(
    sheet_id: str, sheet_name: str = "Sheet1"
) -> pd.DataFrame:
    gd = GoogleDrive()
    metadata_df = gd.get_sheet_as_df(sheet_id, sheet_name)
    metadata_df = metadata_df.dropna(subset=["mouse_id"])
    metadata_df["mouse_id"] = metadata_df["mouse_id"].astype(str)
    metadata_df.columns = map(str.lower, metadata_df.columns)
    return metadata_df


class Session:
    """
    class for dealing with data from single session,
    containing all trials and all animals within cohort
    """

    def __init__(self, data: pd.DataFrame, metadata_df: pd.DataFrame = None):
        unique_sessions = data["session_id"].unique()
        if len(unique_sessions) != 1:
            raise ValueError(f"Expected one session, found {unique_sessions}")

        self.session_id = unique_sessions[0]

        df = data.copy()
        parts = df["source_file"].str.split("_", expand=True)
        if parts.shape[1] == 6:
            df["session_date"] = parts[4]
        elif parts.shape[1] == 4:
            df["session_date"] = parts[2]

        if metadata_df is not None:
            df = df.merge(metadata_df, on=["mouse_id", "session_date"], how="left")
        df["norm_lick_rate"] = (df["tone_licks"] / df["tone_duration"]) / (
            np.where(df["pre_tone_licks"] == 0, 1, df["pre_tone_licks"])
            / df["pre_tone_duration"]
        )
        df["total_licks"] = (
            df["pre_tone_licks"]
            + df["tone_licks"]
            + df["trace_licks"]
            + df["post_trace_licks"]
        )
        self.data = df
        self.subjects = self.data["mouse_id"].unique().tolist()
        self.trials = self.data["trial_number"].unique().tolist()

    def plot_mouse_trials(
        self,
        mouse_id: str,
        y: str = "total_licks",
        x: str = "trial_number",
        title: str = None,
        ylabel: str = None,
        xlabel: str = None,
        figsize=(10, 6),
    ):
        """
        Line plot to visualize changes over trials for a single mouse.
        Highlights trials where y == 0 with a different color.
        """
        df_mouse = self.data[self.data["mouse_id"] == mouse_id].copy()
        df_zero = df_mouse[df_mouse[y] == 0]
        df_nonzero = df_mouse[df_mouse[y] != 0]

        plt.figure(figsize=figsize)

        # Plot non-zero points
        sns.lineplot(
            data=df_nonzero, x=x, y=y, marker="o", label="Non-zero", color="tab:blue"
        )

        # Overlay zero points in red
        if not df_zero.empty:
            sns.scatterplot(
                data=df_zero, x=x, y=y, color="red", label="Zero", marker="X", s=100
            )

        plt.title(title or f"{y} over {x} for {mouse_id}")
        plt.ylabel(ylabel or y)
        plt.xlabel(xlabel or x)
        plt.legend()
        plt.tight_layout()
        plt.show()

        # Optional: print trial numbers with y == 0
        if not df_zero.empty:
            print(f"Trials with {y} == 0 for {mouse_id}: {df_zero[x].tolist()}")

        print(df_zero[[x, y]])

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

    def plot_stage_boxplot_for_mouse(
        self,
        mouse_id: str,
        stage_cols: dict = {
            "Pre-tone": "pre_tone_licks",
            "Tone": "norm_tone_licks",
            "Trace": "norm_trace_licks",
            "Post-trace": "norm_post_trace_licks",
        },
        hue: str = "tone",
        hue_order: list = ["cs+", "cs-"],
        palette={"cs+": "#A1C9F4", "cs-": "#FFB482"},
        figsize: tuple = (8, 6),
        title: str = None,
    ):
        """
        Plot grouped boxplots (x = stage, hue = tone) for a single mouse.

        Args:
            mouse_id: ID of the mouse to filter
            stage_cols: dict mapping stage names to data columns
            palette: seaborn color palette
            figsize: overall figure size
            title: plot title
        """

        df = self.data[self.data["mouse_id"] == mouse_id].copy()

        # Reshape to long format
        long_df = []
        for stage, col in stage_cols.items():
            temp = df[[hue, col]].copy()
            temp = df[[hue, col]].copy()  # << include hue!
            temp = temp.rename(columns={col: "licks"})
            temp["stage"] = stage
            long_df.append(temp)

        plot_df = pd.concat(long_df)

        # Plot
        plt.figure(figsize=figsize)
        # Adjust hue_order to match actual data
        available_hues = plot_df[hue].unique()
        valid_hue_order = [h for h in hue_order if h in available_hues]

        sns.boxplot(
            data=plot_df,
            x="stage",
            y="licks",
            hue=hue,
            hue_order=valid_hue_order,
            palette=palette,
            showfliers=False,
        )

        plt.title(
            title
            or f"Lick Distribution by Stage and Tone for {mouse_id} ({self.session_id})"
        )
        plt.xlabel("Stage")
        plt.ylabel("Lick Count")
        plt.legend(title="Tone")
        sns.despine(offset=10, trim=True)
        plt.tight_layout()
        plt.show()

    def plot_stage_boxplot_by_group(
        self,
        stage_cols: dict = {
            "Pre-tone": "pre_tone_licks",
            "Tone": "norm_tone_licks",
            "Trace": "norm_trace_licks",
            "Post-trace": "norm_post_trace_licks",
        },
        group_vars: list = ["tone", "Age"],
        figsize: tuple = (8, 6),
        title: str = None,
    ):
        """
        Plot boxplots of lick metrics per stage, grouped by interaction of group variables across the cohort within a session.

        Args:
            stage_cols: dict mapping stage names to data columns
            group_vars: list of columns to group by (e.g., ['tone', 'Age'])
        """
        df = self.data.copy()

        # Create group labels by joining group_vars
        df["group"] = df[group_vars].astype(str).agg(" × ".join, axis=1)

        # Sort values for hue_order
        levels_1 = sorted(df[group_vars[0]].dropna().unique())
        levels_2 = sorted(df[group_vars[1]].dropna().unique())
        hue_order = [f"{l1} × {l2}" for l1 in levels_1 for l2 in levels_2]

        # Define color palette
        green_palette = sns.color_palette("Greens", n_colors=len(levels_2) + 1)[
            1:
        ]  # Skip very light
        blue_palette = sns.color_palette("Blues", n_colors=len(levels_2) + 1)[1:]

        palette = {}
        for i, l2 in enumerate(levels_2):
            palette[f"{levels_1[0]} × {l2}"] = green_palette[i]
            palette[f"{levels_1[1]} × {l2}"] = blue_palette[i]

        # Reshape to long format
        long_df = []
        for stage, col in stage_cols.items():
            temp = df[["group", col]].copy()
            temp = temp.rename(columns={col: "licks"})
            temp["stage"] = stage
            long_df.append(temp)

        plot_df = pd.concat(long_df)

        # Plot
        plt.figure(figsize=figsize)
        sns.boxplot(
            data=plot_df,
            x="stage",
            y="licks",
            hue="group",
            hue_order=hue_order,
            palette=palette,
        )

        plt.title(title or f"Lick Distribution by Stage and Group ({self.session_id})")
        plt.xlabel("Stage")
        plt.ylabel("Lick Count")
        plt.legend(
            title=" × ".join(group_vars), bbox_to_anchor=(1.05, 1), loc="upper left"
        )
        plt.tight_layout()
        # plt.ylim(0, 15)
        plt.show()


class Cohort:
    """
    class for dealing with data from single cohort,
    containing multiple sessions and all animals within cohort
    """

    def __init__(self, data: pd.DataFrame, metadata_df: pd.DataFrame = None):
        self.data = data.copy()
        if metadata_df is not None:
            self.data = self.data.merge(metadata_df, on="mouse_id", how="left")

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
