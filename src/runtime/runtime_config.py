import ctypes
import subprocess

import onnxruntime as ort


available_providers = ort.get_available_providers()


def nvidia_gpu_ativa() -> bool:
    try:
        result = subprocess.run(
            ["nvidia-smi", "-L"],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return False

    return result.returncode == 0 and bool(result.stdout.strip())


def cuda_libs_disponiveis() -> bool:
    try:
        ctypes.CDLL("libcublasLt.so.12")
        return True
    except OSError:
        return False


use_cuda = (
    "CUDAExecutionProvider" in available_providers
    and nvidia_gpu_ativa()
    and cuda_libs_disponiveis()
)

if use_cuda:
    ORT_PROVIDERS = ["CUDAExecutionProvider", "CPUExecutionProvider"]
else:
    ORT_PROVIDERS = ["CPUExecutionProvider"]


def resolver_providers(provider_config: str, nome_modelo: str) -> list[str]:
    if provider_config == "cpu":
        return ["CPUExecutionProvider"]

    if provider_config == "gpu":
        if use_cuda:
            return ["CUDAExecutionProvider", "CPUExecutionProvider"]

        print(
            f"[AVISO] Modelo {nome_modelo} configurado para GPU, "
            "mas GPU nao disponivel. Usando CPU."
        )
        return ["CPUExecutionProvider"]

    raise ValueError(f"Provider '{provider_config}' invalido. Use 'gpu' ou 'cpu'.")
