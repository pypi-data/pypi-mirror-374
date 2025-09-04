from pathlib import Path

from autoclean import Pipeline

# Define paths - modify these to match your system
EXAMPLE_OUTPUT_DIR = Path(
    "C:/Users/Gam9LG/Documents/AutocleanDev"
)  # Where processed data will be stored
CONFIG_FILE = Path(
    "C:/Users/Gam9LG/Documents/Autoclean_testing/autoclean_config.yaml"
)  # Path to config relative to working directory OR absolute path

"""Example of processing a single EEG file."""
# Create pipeline instance
pipeline = Pipeline(
    output_dir=EXAMPLE_OUTPUT_DIR,
    verbose="INFO",  # Set to 'DEBUG' for more detailed logging
)

pipeline.start_autoclean_review()
