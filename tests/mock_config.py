from dataclasses import dataclass
from pathlib import Path
import tomllib


@dataclass(frozen=True)
class MockDataConfig:
    """Configuracao exclusiva da suite para acessar o dataset reduzido."""

    tests_dir: Path = Path(__file__).resolve().parent

    def __post_init__(self) -> None:
        object.__setattr__(self, "_config", self._carregar_config())

    def _carregar_config(self) -> dict:
        with self.config_path.open("rb") as config_file:
            return tomllib.load(config_file)

    @property
    def config_path(self) -> Path:
        return self.tests_dir / "config.toml"

    @property
    def mock_data_dir(self) -> Path:
        return self.tests_dir / self._config["paths"]["mock_data_dir"]

    @property
    def indice_path(self) -> Path:
        return self.mock_data_dir / self._config["paths"]["indice_file"]

    @property
    def images_dir(self) -> Path:
        return self.mock_data_dir / self._config["paths"]["images_dir"]

    @property
    def ground_truth_raw_dir(self) -> Path:
        return self.mock_data_dir / self._config["paths"]["ground_truth_raw_dir"]
