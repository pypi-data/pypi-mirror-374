"""
Constants
=========

This module defines the constants used throughout the rest of the package.

"""
from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import TypeAlias

import yaml
from dotenv import load_dotenv
from platformdirs import user_data_path


# : environment
load_dotenv()


# : type aliases
PathLike: TypeAlias = os.PathLike


# ─── helper functions ───────────────────────────────────────────────────────────── ✦ ─
def load_acquisition_config() -> yaml.YAMLObject:
    """
    Load `acquisition.yaml` from repository root.

    Returns
    -------
    A `YAMLObject` representation of the repository's `acquisition.yaml`
    configuration file.

    """
    current_directory = Path.cwd()

    for parent in [current_directory] + list(current_directory.parents):
        targets_path = parent / "acquisition.yaml"
        if targets_path.exists():
            with open(targets_path, "r") as f:
                 return yaml.safe_load(f)

    raise FileNotFoundError("`acquisition.yaml` not found in any parent directory.")


# : constants
DATA_DIR: PathLike = user_data_path(__package__, ensure_exists=True)


# : re-export configuration options
ACQUISITION_CONFIG = load_acquisition_config()  # data acquisition
EMAIL: str = ACQUISITION_CONFIG["email"]
TARGETS: list[str] = ACQUISITION_CONFIG["targets"]          # reference sequences
USER_AGENT: str = ACQUISITION_CONFIG["user_agent"]          # requests user agent string
