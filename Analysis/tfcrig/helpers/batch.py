import os
import pandas as pd
from typing import List
from tfcrig.classes import Session  # adjust import as needed


def compute_metrics_from_folder(folder_path: str) -> pd.DataFrame:
    """
    Loads all .json files from a folder, computes lick metrics for each,
    and returns a combined DataFrame.
    """
    all_metrics = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".json") and not filename.endswith("_raw.json"):
            full_path = os.path.join(folder_path, filename)

            try:
                session = Session(full_path)
                metrics = session.compute_lick_metrics_all_mice()
                metrics["source_file"] = filename  # Optional
                all_metrics.append(metrics)
            except Exception as e:
                print(f"Skipping {filename} due to error: {e}")

    return pd.concat(all_metrics, ignore_index=True) if all_metrics else pd.DataFrame()
