"""Example of how to load samples from path with the dataset class."""

from pathlib import Path

from environs import Env

import lightly_studio as ls

# Read environment variables
env = Env()
env.read_env()

# Define the path to the dataset directory
dataset_path = Path(env.path("DATASET_PATH", "/path/to/your/dataset"))
dataset_path = dataset_path.parent if dataset_path.is_file() else dataset_path

# Create a DatasetLoader from a path
dataset = ls.Dataset("clothing_small_test")
dataset.add_samples_from_path(path=dataset_path)

ls.start_gui()
