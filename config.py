from pathlib import Path
from datetime import datetime, timedelta, timezone

DELTA_T = timedelta(hours=4)
RUN1_START_TIME = datetime(2024, 12, 10, 0, 0, 0, tzinfo=timezone.utc)
RUN2_START_TIME = datetime(2025, 10, 16, 0, 0, 0, tzinfo=timezone.utc)

BASE_PATH = Path(__file__).resolve().parent
DATA_DIR = BASE_PATH / "data/"
DATA_CSV_DIR = BASE_PATH / "data_csv/"
PLOT_DIR = BASE_PATH / "plots/"

