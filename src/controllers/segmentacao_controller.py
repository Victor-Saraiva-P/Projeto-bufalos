from __future__ import annotations

from collections.abc import Iterable, Mapping

from src.config import MODELOS_PARA_AVALIACAO
from src.io.path_resolver import PathResolver
from src.logs import (
    EstatisticasProcessamentoComEta,
    imprimir_resumo_modelo,
    imprimir_status,
)
from src.models import Imagem
from src.repositories import ImagemRepository
from src.segmentacao.integracoes import obter_resolvedor_providers
from src.services.segmentacao_service import ResultadoSegmentacaoArquivo, SegmentacaoService


class SegmentacaoController:
    def __init__(
        self,
        sqlite_path: str | None = None,
        path_resolver: PathResolver | None = None,
        imagem_repository: ImagemRepository | None = None,
        segmentacao_service: SegmentacaoService | None = None,
    ):
        self.path_resolver = (
            path_resolver if path_resolver is not None else PathResolver.from_config()
        )
        sqlite_path_resolvido = (
            sqlite_path if sqlite_path is not None else self.path_resolver.sqlite_path
        )
        self.imagem_repository = (
            imagem_repository
            if imagem_repository is not None
            else ImagemRepository(sqlite_path_resolvido)
        )
        self.segmentacao_service = (
            segmentacao_service
            if segmentacao_service is not None
            else SegmentacaoService()
        )

    def processar_imagens(
        self,
        imagens: Iterable[Imagem] | None = None,
        modelos_para_avaliacao: Mapping[str, str] | None = None,
    ) -> dict[str, EstatisticasProcessamentoComEta]:
        linhas = (
            list(imagens)
            if imagens is not None
            else self.imagem_repository.list()
        )
        modelos = dict(modelos_para_avaliacao or MODELOS_PARA_AVALIACAO)
        total_previsto = len(modelos) * len(linhas)
        stats_geral = EstatisticasProcessamentoComEta(total=total_previsto)
        resumos_modelo: dict[str, EstatisticasProcessamentoComEta] = {}
        resolver_providers = obter_resolvedor_providers()

        for nome_modelo, provider_config in modelos.items():
            providers = resolver_providers(provider_config, nome_modelo)
            print(f"Iniciando modelo: {nome_modelo} (provider: {provider_config})")

            stats_modelo = EstatisticasProcessamentoComEta(total=len(linhas))
            resumos_modelo[nome_modelo] = stats_modelo
            rembg_session = self.segmentacao_service.criar_sessao_segmentacao(
                nome_modelo,
                providers,
            )

            for imagem in linhas:
                resultado = self.segmentacao_service.segmentar_arquivo(
                    nome_arquivo=imagem.nome_arquivo,
                    nome_modelo=nome_modelo,
                    original_path=self.path_resolver.caminho_foto_original(
                        imagem.nome_arquivo
                    ),
                    mascara_path=self.path_resolver.caminho_ground_truth(
                        imagem.nome_arquivo
                    ),
                    output_path=self.path_resolver.caminho_mascara_predita(
                        nome_modelo,
                        imagem.nome_arquivo,
                    ),
                    rembg_session=rembg_session,
                )
                self._registrar_resultado(stats_geral, stats_modelo, resultado)

                imprimir_status(stats_geral, stats_modelo, nome_modelo)

            imprimir_resumo_modelo(nome_modelo, stats_modelo)

        return resumos_modelo

    @staticmethod
    def _registrar_resultado(
        stats_geral: EstatisticasProcessamentoComEta,
        stats_modelo: EstatisticasProcessamentoComEta,
        resultado: ResultadoSegmentacaoArquivo,
    ) -> None:
        if resultado.status == "ok":
            duracao = resultado.duracao_inferencia or 0.0
            stats_geral.registrar_ok_com_duracao(duracao)
            stats_modelo.registrar_ok_com_duracao(duracao)
            return

        if resultado.status == "skip":
            stats_geral.registrar_skip()
            stats_modelo.registrar_skip()
            return

        stats_geral.registrar_erro()
        stats_modelo.registrar_erro()
