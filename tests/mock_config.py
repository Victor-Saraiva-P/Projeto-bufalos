from dataclasses import dataclass, field
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class MockDataConfig:
    """Configuracao da suite espelhando src/config.py, apontada para tests/."""

    tests_dir: Path = Path(__file__).resolve().parent
    _config: dict = field(init=False, repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "_config", self._carregar_config())

    def _carregar_config(self) -> dict:
        with self.config_path.open("rb") as config_file:
            return tomllib.load(config_file)

    @staticmethod
    def _resolver_caminho(base_dir: Path, *parts: str) -> Path:
        return base_dir.joinpath(*parts)

    @property
    def config_path(self) -> Path:
        return self.tests_dir / "config.toml"

    @property
    def base_dir(self) -> Path:
        return self.tests_dir

    @property
    def data_dir(self) -> Path:
        return self._resolver_caminho(self.base_dir, self._config["paths"]["data_dir"])

    @property
    def generated_dir(self) -> Path:
        return self._resolver_caminho(
            self.base_dir,
            self._config["paths"]["generated_dir"],
        )

    @property
    def indice_path(self) -> Path:
        return self._resolver_caminho(
            self.data_dir,
            self._config["paths"]["indice_file"],
        )

    @property
    def sqlite_path(self) -> Path:
        return self._resolver_caminho(
            self.generated_dir,
            self._config["paths"]["sqlite_file"],
        )

    @property
    def images_dir(self) -> Path:
        return self._resolver_caminho(
            self.data_dir,
            self._config["paths"]["images_dir"],
        )

    @property
    def ground_truth_raw_dir(self) -> Path:
        return self._resolver_caminho(
            self.data_dir,
            self._config["paths"]["ground_truth_raw_dir"],
        )

    @property
    def predicted_masks_dir(self) -> Path:
        return self._resolver_caminho(
            self.generated_dir,
            self._config["paths"]["predicted_masks_dir"],
        )

    @property
    def predicted_masks_binary_dir(self) -> Path:
        return self._resolver_caminho(
            self.generated_dir,
            self._config["paths"]["predicted_masks_binary_dir"],
        )

    @property
    def ground_truth_binary_dir(self) -> Path:
        return self._resolver_caminho(
            self.generated_dir,
            self._config["paths"]["ground_truth_binary_dir"],
        )

    @property
    def evaluation_dir(self) -> Path:
        return self._resolver_caminho(
            self.generated_dir,
            self._config["paths"]["evaluation_dir"],
        )

    @property
    def images_type(self) -> str:
        return self._config["file_types"]["images"]

    @property
    def rembg_image_type(self) -> str:
        return self._config["file_types"]["rembg"]

    @property
    def modelos_para_avaliacao(self) -> dict[str, str]:
        return dict(self._config["models"])
