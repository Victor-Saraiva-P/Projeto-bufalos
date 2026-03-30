from importlib import import_module

__all__ = [
    "AvaliacaoController",
    "SegmentacaoController",
    "BinarizacaoController",
    "ImagemController",
]


def __getattr__(name: str):
    if name == "AvaliacaoController":
        return import_module("src.controllers.avaliacao_controller").AvaliacaoController
    if name == "SegmentacaoController":
        return import_module("src.controllers.segmentacao_controller").SegmentacaoController
    if name == "BinarizacaoController":
        return import_module("src.controllers.binarizacao_controller").BinarizacaoController
    if name == "ImagemController":
        return import_module("src.controllers.imagem_controller").ImagemController
    raise AttributeError(name)
