import os
import sys
import types

import numpy as np

os.environ["BUFALOS_ENV"] = "test"
os.environ.pop("BUFALOS_CONFIG_PATH", None)

try:
    import cv2  # noqa: F401
except ModuleNotFoundError:
    cv2_stub = types.ModuleType("cv2")
    cv2_stub.RETR_EXTERNAL = 0
    cv2_stub.CHAIN_APPROX_SIMPLE = 0
    cv2_stub.CHAIN_APPROX_NONE = 1

    def _fake_find_contours(mask: np.ndarray, _mode: int, _method: int):
        ys, xs = np.where(mask > 0)
        if xs.size == 0:
            return [], None

        x_min, x_max = int(xs.min()), int(xs.max())
        y_min, y_max = int(ys.min()), int(ys.max())
        contour = np.array(
            [
                [[x_min, y_min]],
                [[x_max, y_min]],
                [[x_max, y_max]],
                [[x_min, y_max]],
            ],
            dtype=np.int32,
        )
        return [contour], None

    def _fake_arc_length(contour: np.ndarray, closed: bool = True) -> float:
        pontos = contour.reshape(-1, 2)
        if len(pontos) < 2:
            return 0.0

        deslocamentos = pontos[1:] - pontos[:-1]
        perimetro = float(np.linalg.norm(deslocamentos, axis=1).sum())
        if closed:
            perimetro += float(np.linalg.norm(pontos[0] - pontos[-1]))
        return perimetro

    cv2_stub.findContours = _fake_find_contours
    cv2_stub.arcLength = _fake_arc_length
    sys.modules["cv2"] = cv2_stub
