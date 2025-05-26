# RecycleLog.py
from datetime import datetime
# This file will be used for logging mis-handled data from data migration process for later handling.
class RecycleLogger():
    def __init__(self, fpath):
        self.fpath = fpath

    def log(self, recycle_to="", value="", came_from="", can_be_recycle=False, missing=""):
        with open(self.fpath, "a") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')},{recycle_to},{value},{came_from},{can_be_recycle},{missing}\n")
