from importlib import import_module

__all__ = [
    "AvaliacaoService",
    "SegmentacaoService",
    "BinarizacaoService",
    "ImagemService",
]


def __getattr__(name: str):
    if name == "AvaliacaoService":
        return import_module("src.services.avaliacao_service").AvaliacaoService
    if name == "SegmentacaoService":
        return import_module("src.services.segmentacao_service").SegmentacaoService
    if name == "BinarizacaoService":
        return import_module("src.services.binarizacao_service").BinarizacaoService
    if name == "ImagemService":
        return import_module("src.services.imagem_service").ImagemService
    raise AttributeError(name)
