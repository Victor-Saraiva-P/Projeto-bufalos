import os
import sys
import types

os.environ["BUFALOS_ENV"] = "test"
os.environ.pop("BUFALOS_CONFIG_PATH", None)

try:
    import cv2  # noqa: F401
except ModuleNotFoundError:
    cv2_stub = types.ModuleType("cv2")
    cv2_stub.RETR_EXTERNAL = 0
    cv2_stub.CHAIN_APPROX_SIMPLE = 0

    def _cv2_indisponivel(*_args, **_kwargs):
        raise ModuleNotFoundError("cv2 nao esta instalado no ambiente de testes.")

    cv2_stub.findContours = _cv2_indisponivel
    cv2_stub.arcLength = _cv2_indisponivel
    sys.modules["cv2"] = cv2_stub
