"""Data class dealing with the preprocessed session data.
"""
from dataclasses import dataclass
import json
from pathlib import Path
import os
from os.path import join
import pandas as pd
import numpy as np
from typing import Union

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
        with open(self.session_path, 'r') as f:
            data = json.load(f)
        return data