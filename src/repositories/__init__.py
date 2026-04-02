from src.repositories.imagem_repository import ImagemRepository
from src.repositories.ground_truth_binarizada_repository import (
    GroundTruthBinarizadaRepository,
)
from src.repositories.segmentacao_repository import (
    SegmentacaoBrutaRepository,
)
from src.repositories.binarizacao_repository import (
    SegmentacaoBinarizadaRepository,
)
from src.repositories.tag_repository import TagRepository
from src.repositories.imagem_tag_repository import ImagemTagRepository

__all__ = [
    "GroundTruthBinarizadaRepository",
    "ImagemRepository",
    "ImagemTagRepository",
    "SegmentacaoBinarizadaRepository",
    "SegmentacaoBrutaRepository",
    "TagRepository",
]
