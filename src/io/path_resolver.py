from __future__ import annotations

from dataclasses import dataclass, replace
import os

from src.config import IMAGES_TYPE, REMBG_IMAGE_TYPE


@dataclass(frozen=True)
class PathResolver:
    data_dir: str
    generated_dir: str
    images_dir: str
    ground_truth_brutos_dir: str
    segmentacoes_brutas_dir: str
    segmentacoes_binarizadas_dir: str
    ground_truth_binarizada_dir: str
    evaluation_dir: str
    indice_path: str
    sqlite_path: str

    @classmethod
    def from_config(cls) -> "PathResolver":
        from src.config import (
            DATA_DIR,
            EVALUATION_DIR,
            GENERATED_DIR,
            GROUND_TRUTH_BINARIZADA_DIR,
            GROUND_TRUTH_BRUTOS_DIR,
            IMAGES_DIR,
            INDICE_PATH,
            SEGMENTACOES_BINARIZADAS_DIR,
            SEGMENTACOES_BRUTAS_DIR,
            SQLITE_PATH,
        )

        return cls(
            data_dir=DATA_DIR,
            generated_dir=GENERATED_DIR,
            images_dir=IMAGES_DIR,
            ground_truth_brutos_dir=GROUND_TRUTH_BRUTOS_DIR,
            segmentacoes_brutas_dir=SEGMENTACOES_BRUTAS_DIR,
            segmentacoes_binarizadas_dir=SEGMENTACOES_BINARIZADAS_DIR,
            ground_truth_binarizada_dir=GROUND_TRUTH_BINARIZADA_DIR,
            evaluation_dir=EVALUATION_DIR,
            indice_path=INDICE_PATH,
            sqlite_path=SQLITE_PATH,
        )

    def with_overrides(self, **overrides: str) -> "PathResolver":
        return replace(self, **overrides)

    def caminho_foto_original(self, nome_arquivo: str) -> str:
        return os.path.join(self.images_dir, f"{nome_arquivo}{IMAGES_TYPE}")

    def caminho_ground_truth_bruta(self, nome_arquivo: str) -> str:
        return os.path.join(self.ground_truth_brutos_dir, f"{nome_arquivo}{IMAGES_TYPE}")

    def caminho_ground_truth_binarizada(self, nome_arquivo: str) -> str:
        return os.path.join(
            self.ground_truth_binarizada_dir,
            f"{nome_arquivo}{REMBG_IMAGE_TYPE}",
        )

    @staticmethod
    def nome_pasta_execucao(execucao: int) -> str:
        return f"execucao_{execucao}"

    def caminho_segmentacao_bruta(
        self,
        nome_modelo: str,
        nome_arquivo: str,
        execucao: int,
    ) -> str:
        return os.path.join(
            self.segmentacoes_brutas_dir,
            self.nome_pasta_execucao(execucao),
            nome_modelo,
            f"{nome_arquivo}{REMBG_IMAGE_TYPE}",
        )

    def caminho_segmentacao_binarizada(
        self,
        nome_modelo: str,
        nome_arquivo: str,
        execucao: int,
        nome_binarizacao: str,
    ) -> str:
        return os.path.join(
            self.segmentacoes_binarizadas_dir,
            self.nome_pasta_execucao(execucao),
            nome_binarizacao,
            nome_modelo,
            f"{nome_arquivo}{REMBG_IMAGE_TYPE}",
        )

    def caminho_segmentacao_avaliacao(
        self,
        nome_modelo: str,
        nome_arquivo: str,
        execucao: int | None = None,
        nome_binarizacao: str | None = None,
    ) -> str:
        if nome_modelo == "ground_truth":
            return self.caminho_ground_truth_binarizada(nome_arquivo)

        if execucao is None:
            raise ValueError("execucao e obrigatoria para segmentacoes previstas.")
        if nome_binarizacao is None:
            raise ValueError(
                "nome_binarizacao e obrigatorio para segmentacoes previstas."
            )

        return self.caminho_segmentacao_binarizada(
            nome_modelo,
            nome_arquivo,
            execucao=execucao,
            nome_binarizacao=nome_binarizacao,
        )
