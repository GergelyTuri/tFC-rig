### want to have three levels of stats/analysis classes
# 1. at cohort level: could have methods to compare between cohorts to see comparisons between different protocols
# 2. within cohort at session level: methods for comparing different sessions within a cohort
# 3. within session at subject level: methods for comparing different subjects/conditions over trial
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
from scipy.stats import wilcoxon, mannwhitneyu

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

    def __init__(
        self, data: pd.DataFrame, metadata_df: pd.DataFrame = None, trial_filter=None
    ):
        unique_sessions = data["session_id"].unique()
        if len(unique_sessions) != 1:
            raise ValueError(f"Expected one session, found {unique_sessions}")

        self.session_id = unique_sessions[0]

        df = data.copy()

        if trial_filter is not None:
            if callable(trial_filter):
                df = df[df["trial_number"].apply(trial_filter)]
            else:
                df = df[df["trial_number"].isin(trial_filter)]

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

        df["pre_tone_lick_rate"] = df["pre_tone_licks"] / df["pre_tone_duration"]
        df["tone_lick_rate"] = df["tone_licks"] / df["tone_duration"]
        df["trace_lick_rate"] = df["trace_licks"] / df["trace_duration"]
        df["post_trace_lick_rate"] = df["post_trace_licks"] / df["post_trace_duration"]
        df["norm_tone_lick_rate"] = df["norm_tone_licks"] / df["tone_duration"]
        df["norm_trace_lick_rate"] = df["norm_trace_licks"] / df["trace_duration"]
        df["norm_post_trace_lick_rate"] = (
            df["norm_post_trace_licks"] / df["post_trace_duration"]
        )
        df["iti_lick_rate"] = df["iti_lick_count"] / df["iti_duration"]

        self.data = df
        self.subjects = self.data["mouse_id"].unique().tolist()
        self.trials = self.data["trial_number"].unique().tolist()

    def select_trials(self, trial_numbers):
        """
        Select specific trials based on trial numbers.
        """

        if isinstance(trial_numbers, int):
            trial_numbers = [trial_numbers]

        filtered_df = self.data[self.data["trial_number"].isin(trial_numbers)].copy()
        return filtered_df

    def plot_cohort_across_trials(
        self,
        x: str = "trial_number",
        y: str = "total_licks",
        hue: str = "tone",
        style: str = "age",
    ):
        """
        Plot cohort data across trials for a single session by age and tone groups.

        Args:
            x: x-axis variable (default is trial number)
            y: y-axis variable (default is total licks)
            hue: column name for hue grouping (default is tone)
            style: column name for style grouping (default is Age)
        """
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=self.data, x=x, y=y, hue=hue, style=style)
        plt.title(f"{y} over {x} in {self.session_id}")
        plt.ylabel(y)
        plt.xlabel(x)
        plt.legend(loc="upper right", ncol=2, title=hue + " x " + style)
        plt.tight_layout(rect=[0, 0, 0.85, 1])

    def plot_mouse_total_licks_across_trials(
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

    def plot_all_mice_metrics_over_trials(
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

    def plot_stage_boxplot_for_single_mouse(
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
        ylabel: str = "Lick Count",
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
            showfliers=False,
        )

        plt.title(title or f"Lick Distribution by Stage and Group ({self.session_id})")
        plt.xlabel("Stage")
        plt.ylabel(ylabel)
        plt.legend(
            title=" × ".join(group_vars), bbox_to_anchor=(1.05, 1), loc="upper left"
        )
        plt.tight_layout()
        # plt.yscale("log")
        # plt.ylim(0, 15)
        plt.show()

    def wilcoxon_test_for_condition(
        self,
        condition: str = "tone",
        filter_group: str = "age",
        select_group: str = "aged",
        testing_metrics: str = "norm_tone_licks",
    ):
        """
        Perform Wilcoxon signed rank test for comparing two conditions (e.g., cs+ vs cs-) within the same aged group (e.g., aged mice). within a session across all trials.

        Args:
            condition: column name indicationg the condition to compare
            filter_group: column name indicating the group to filter by
            select_group: specific value from filter_group to select (e.g., choose "aged" for "age")
            testing_metrics: column name indicating the metric to test
        """
        df = self.data.copy()
        df = df[df[filter_group] == select_group]
        condition1 = df[condition].unique()[0]
        condition2 = df[condition].unique()[1]
        df_group1 = df[df[condition] == condition1][testing_metrics]
        df_group2 = df[df[condition] == condition2][testing_metrics]
        result = wilcoxon(df_group1, df_group2)
        print(
            f"Wilcoxon test between {condition1} and {condition2} among {select_group} mice:"
        )
        print(f"Statistic: {result.statistic}, p-value: {result.pvalue}")

    def mann_whitney_test_for_age(
        self,
        condition: str = "age",
        filter_group: str = "tone",
        select_group: str = "cs+",
        testing_metrics: str = "norm_tone_licks",
    ):
        """
        Perform Mann-Whitney U test for comparing two age groups (e.g., aged vs young) within a specific condition (e.g., cs+).

        Args:
            condition: column name indicating the condition to compare
            filter_group: column name indicating the group to filter by
            select_group: specific value from filter_group to select (e.g., choose "cs+" for "tone")
            testing_metrics: column name indicating the metric to test
        """
        df = self.data.copy()
        df = df[df[filter_group] == select_group]
        condition1 = df[condition].unique()[0]
        condition2 = df[condition].unique()[1]
        df_group1 = df[df[condition] == condition1][testing_metrics]
        df_group2 = df[df[condition] == condition2][testing_metrics]
        result = mannwhitneyu(df_group1, df_group2)
        print(
            f"Mann-Whitney U test between {condition1} and {condition2} among {select_group} mice:"
        )
        print(f"Statistic: {result.statistic}, p-value: {result.pvalue}")

    def iti_comparison(
        self,
        stage_cols: dict = {
            "Tone Lick Rate": "tone_lick_rate",
            "ITI Lick Rate": "iti_lick_rate",
        },
        group_vars: str = "age",
        hue: str = "tone",
        hue_order: list = ["cs+", "cs-"],
        palette: dict = {"cs+": "#3c73a8", "cs-": "#acc2d9"},
        figsize: tuple = (12, 5),
        title: str = None,
        ylabel: str = "Lick Rate (licks/s)",
    ):
        """
        Plot horizontal subplots comparing lick rate metrics between two groups defined by a group variable,
        using hue to separate conditions (e.g., tone: cs+ vs cs-).
        """
        df = self.data.copy()
        unique_groups = df[group_vars].dropna().unique()

        if len(unique_groups) != 2:
            raise ValueError(
                f"Expected exactly two levels in '{group_vars}', got {unique_groups}"
            )

        fig, axes = plt.subplots(1, 2, figsize=figsize, sharey=True)

        for ax, group in zip(axes, unique_groups):
            sub_df = df[df[group_vars] == group].copy()

            # Reshape to long format
            long_df = []
            for stage, col in stage_cols.items():
                temp = sub_df[[col, hue]].copy()
                temp = temp.rename(columns={col: "licks"})
                temp["stage"] = stage
                long_df.append(temp)

            plot_df = pd.concat(long_df, ignore_index=True)

            sns.boxplot(
                data=plot_df,
                x="stage",
                y="licks",
                hue=hue,
                hue_order=hue_order,
                palette=palette,
                ax=ax,
                showfliers=False,
            )

            ax.set_title(f"{group_vars.capitalize()}: {group}")
            ax.set_xlabel("Stage")
            ax.set_ylabel(ylabel)
            ax.legend_.remove()

        if title:
            fig.suptitle(title, fontsize=14)

        # Add shared legend outside plot
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(
            handles,
            labels,
            title=hue.capitalize(),
            loc="upper right",
            bbox_to_anchor=(1.15, 1),
        )

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()

    def iti_test(
        self,
        compare_cols: list = [
            "tone_lick_rate",
            "trace_lick_rate",
            "post_trace_lick_rate",
        ],
        iti_col: str = "iti_lick_rate",
        filter_group: list = ["age", "tone"],
        select_group: list = ["aged", "cs+"],
    ):
        """
        Perform Mann_Whitney U Test to compare ITI lick rate with other lick rates

        Args:
            compare_cols: list of columns to compare with ITI lick rate
            iti_col: column name for ITI lick rate
            filter_group: list of columns to filter by (e.g., ['age', 'tone'])
            select_group: list of specific values from filter_group to select (e.g., ['aged', 'cs+'])

        Note: the order of filter_group and select_group should match
            e.g., filter_group[0] corresponds to select_group[0]
        """
        df = self.data.copy()
        df = df[
            (df[filter_group[0]] == select_group[0])
            & (df[filter_group[1]] == select_group[1])
        ]

        iti_data = df[iti_col].dropna()

        for col in compare_cols:
            stage_data = df[col].dropna()
            result = mannwhitneyu(stage_data, iti_data, alternative="two-sided")

            print(f"Comparison: {col} vs {iti_col} (group = {select_group})")
            print(f"Statistic: {result.statistic:.3f}, p-value: {result.pvalue:.5f}\n")


class Cohort:
    """
    class for dealing with data from single cohort,
    containing multiple sessions and all animals within cohort
    """

    def __init__(self, data: pd.DataFrame, metadata_df: pd.DataFrame = None):
        df = data.copy()
        if metadata_df is not None:
            df = df.merge(metadata_df, on="mouse_id", how="left")

        required = {"session_id", "mouse_id", "trial_number"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        df["pre_post_trace_licks"] = (
            df["pre_tone_licks"] + df["tone_licks"] + df["trace_licks"]
        )
        df["new_norm_post_trace_licks"] = (
            df["post_trace_licks"] / df["pre_post_trace_licks"]
        )

        self.data = df
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
        df = self.data.copy()
        grouped = df.groupby(groupby_cols)[reward_col]
        result = grouped.apply(lambda x: (x != 0).mean() * 100).reset_index(
            name=f"{reward_col}_success_rate"
        )
        return result

    def plot_reward_success_rate(
        self,
        reward_col: str = "post_trace_reward",
        groupby_cols: list = ["mouse_id", "session_id"],
        title: str = None,
        ylabel: str = None,
        figsize: tuple = (10, 6),
    ):
        """
        Plot the reward success rate for each mouse across sessions.

        Args:
            reward_col: column name indicating reward counts
            groupby_cols: columns to group by (default is ['mouse_id', 'session_id'])
            title: plot title
            ylabel: y-axis label
            figsize: figure size
        """
        df = self.data.copy()
        result = df.compute_reward_success_rate(reward_col, groupby_cols)

        plt.figure(figsize=figsize)
        sns.lineplot(
            data=result,
            x=groupby_cols[1],
            y=f"{reward_col}_success_rate",
            hue="mouse_id",
        )
        plt.title(title or f"Reward Success Rate by {groupby_cols[1]}")
        plt.ylabel(ylabel or f"{reward_col} Success Rate (%)")
        plt.xlabel(groupby_cols[1])
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", borderaxespad=0.0)
        plt.tight_layout()
        plt.show()

    def plot_metric_by_reindexed_trial(
        self,
        y_metric: str,
        # session_order: list,
        groupby_cols: list = ["mouse_id", "session_id"],
        hue: str = "mouse_id",
        title: str = None,
        ylabel: str = None,
        figsize: tuple = (10, 6),
    ):
        """
        Plot the given metric against reindexed trial numbers, with session continuity.

        Args:
            y_metric: the column name of the metric to plot on the y-axis
            session_order: list of session type prefixes in desired order
            hue: column to color lines by (default: "mouse_id")
            title: plot title
            ylabel: y-axis label
            figsize: figure size
        """

        df = self.data.copy()
        grouped = df.groupby(groupby_cols)[y_metric].mean().reset_index()

        plt.figure(figsize=figsize)
        sns.lineplot(
            data=grouped,
            x=groupby_cols[1],  # session_id
            y=y_metric,
            hue=hue,
            marker="o",
        )
        plt.title(title or f"{y_metric} by Session")
        plt.xlabel(groupby_cols[1])
        plt.ylabel(ylabel or y_metric.replace("_", " ").title())
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()
        plt.show()
