"""Data class dealing with the preprocessed session data."""

import json
import os
from dataclasses import dataclass
from os.path import join
from pathlib import Path
from typing import Union

import numpy as np
import pandas as pd


@dataclass
class Session:
    """
    class for parsing json files that contain the preprocessed session data
    """

    session_path: Union[str, Path]

    def __post_init__(self):
        if isinstance(self.session_path, str):
            self.session_path = Path(self.session_path)

    def _load_json(self):
        with open(self.session_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    @property
    def session_header(self):
        return self._load_json()["header"]

    @property
    def session_mouse_ids(self):
        return self._load_json()["header"]["mouse_ids"]
