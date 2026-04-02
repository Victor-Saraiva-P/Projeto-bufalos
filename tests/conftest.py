import os
import cv2  # noqa: F401

os.environ["BUFALOS_ENV"] = "test"
os.environ.pop("BUFALOS_CONFIG_PATH", None)
