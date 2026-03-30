from __future__ import annotations

from collections.abc import Iterable

from src.config import MODELOS_PARA_AVALIACAO
from src.io.mask_utils import carregar_mask_array_avaliacao
from src.io.path_resolver import PathResolver
from src.models import Imagem
from src.repositories import ImagemRepository
from src.services.avaliacao_service import AvaliacaoService


class AvaliacaoController:
    def __init__(
        self,
        sqlite_path: str | None = None,
        path_resolver: PathResolver | None = None,
        imagem_repository: ImagemRepository | None = None,
        avaliacao_service: AvaliacaoService | None = None,
    ):
        self.path_resolver = path_resolver or PathResolver.from_config()
        self.imagem_repository = imagem_repository or ImagemRepository(
            sqlite_path or self.path_resolver.sqlite_path
        )
        self.avaliacao_service = avaliacao_service or AvaliacaoService()

    def processar_imagem(
        self,
        imagem: Imagem,
        modelos_para_avaliacao: Iterable[str] | None = None,
    ) -> Imagem:
        nomes_modelo = list(modelos_para_avaliacao or MODELOS_PARA_AVALIACAO)
        ground_truth_mask = carregar_mask_array_avaliacao(
            imagem.nome_arquivo,
            "ground_truth",
            path_resolver=self.path_resolver,
        )
        mascaras_modelo = {
            nome_modelo: carregar_mask_array_avaliacao(
                imagem.nome_arquivo,
                nome_modelo,
                path_resolver=self.path_resolver,
            )
            for nome_modelo in nomes_modelo
        }

        imagem_avaliada = self.avaliacao_service.avaliar(
            imagem=imagem,
            ground_truth_mask=ground_truth_mask,
            mascaras_modelo=mascaras_modelo,
        )
        return self.imagem_repository.save(imagem_avaliada)
