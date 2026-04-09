from src.repositories.analysis_segmentacao_bruta_base_repository import (
    AnaliseSegmentacaoBrutaBaseRepository,
)
from src.repositories.analysis_segmentacao_bruta_resumo_modelo_repository import (
    AnaliseSegmentacaoBrutaResumoModeloRepository,
)
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
    "AnaliseSegmentacaoBrutaBaseRepository",
    "AnaliseSegmentacaoBrutaResumoModeloRepository",
    "GroundTruthBinarizadaRepository",
    "ImagemRepository",
    "ImagemTagRepository",
    "SegmentacaoBinarizadaRepository",
    "SegmentacaoBrutaRepository",
    "TagRepository",
]
