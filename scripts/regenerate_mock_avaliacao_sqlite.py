from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("BUFALOS_ENV", "test")
os.environ.pop("BUFALOS_CONFIG_PATH", None)

from src.controllers import AvaliacaoController
from src.io.indice_loader import carregar_indice_excel
from src.io.path_resolver import PathResolver
from src.repositories import (
    GroundTruthBinarizadaRepository,
    ImagemRepository,
    SegmentacaoBinarizadaRepository,
    SegmentacaoBrutaRepository,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SQLITE_FIXTURE_PATH = REPO_ROOT / "tests/mock_generated/bufalos-avaliacao.sqlite3"


def build_mock_generated_resolver() -> PathResolver:
    return PathResolver.from_config().with_overrides(
        segmentacoes_brutas_dir=str(REPO_ROOT / "tests/mock_generated/segmentacoes_brutas"),
        segmentacoes_binarizadas_dir=str(
            REPO_ROOT / "tests/mock_generated/segmentacoes_binarizadas"
        ),
        ground_truth_binarizada_dir=str(
            REPO_ROOT / "tests/mock_generated/ground_truth_binarizada"
        ),
        sqlite_path=str(SQLITE_FIXTURE_PATH),
    )


def main() -> None:
    resolver = build_mock_generated_resolver()

    SQLITE_FIXTURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQLITE_FIXTURE_PATH.unlink(missing_ok=True)

    imagens = carregar_indice_excel(resolver.indice_path)
    imagem_repository = ImagemRepository(resolver.sqlite_path)
    imagem_repository.replace_all(imagens)

    avaliacao_controller = AvaliacaoController(
        imagem_repository=imagem_repository,
        ground_truth_binarizada_repository=GroundTruthBinarizadaRepository(
            resolver.sqlite_path
        ),
        segmentacao_binarizada_repository=SegmentacaoBinarizadaRepository(
            resolver.sqlite_path
        ),
        segmentacao_bruta_repository=SegmentacaoBrutaRepository(resolver.sqlite_path),
    )
    avaliacao_controller.path_resolver = resolver

    linhas = imagem_repository.list()
    stats = avaliacao_controller.processar_imagens(imagens=linhas)

    print("Fixture SQLite regenerado com sucesso.")
    print(f"- arquivo: {SQLITE_FIXTURE_PATH}")
    print(f"- imagens: {len(linhas)}")
    print(f"- total previsto: {stats.total}")
    print(f"- ok: {stats.ok}")
    print(f"- erro: {stats.erro}")
    print(f"- skip: {stats.skip}")


if __name__ == "__main__":
    main()
