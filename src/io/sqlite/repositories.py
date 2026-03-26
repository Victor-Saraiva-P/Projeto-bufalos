from __future__ import annotations

from decimal import Decimal

import pandas as pd
from sqlalchemy import delete, select

from src.config import (
    FAZENDA_COL,
    INDICE_PATH,
    NOME_COL,
    PESO_COL,
    SQLITE_PATH,
    TAGS_COL,
)
from src.io.sqlite.database import criar_sessionmaker_sqlite, criar_tabelas_sqlite
from src.io.sqlite.models import AvaliacaoImagemORM, AvaliacaoModeloORM, IndiceORM
from src.models.indice_linha import IndiceLinha, normalizar_tags


class IndiceSQLiteRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def sincronizar_do_excel(self, indice_path: str = INDICE_PATH) -> None:
        indice_df = pd.read_excel(indice_path)
        colunas = {c.strip().lower(): c for c in indice_df.columns}

        nome_col = colunas.get(NOME_COL)
        fazenda_col = colunas.get(FAZENDA_COL)
        peso_col = colunas.get(PESO_COL)
        tags_col = colunas.get(TAGS_COL)

        if not nome_col or not fazenda_col or not peso_col:
            raise ValueError(
                "Alguma das colunas esperadas nao foi encontrada no arquivo Excel."
            )

        with self.sessionmaker() as session:
            session.execute(delete(AvaliacaoModeloORM))
            session.execute(delete(AvaliacaoImagemORM))
            session.execute(delete(IndiceORM))

            for _, row in indice_df.iterrows():
                indice = IndiceORM(
                    nome_arquivo=str(row[nome_col]),
                    fazenda=str(row[fazenda_col]),
                    peso=float(row[peso_col]),
                    tags=str(row[tags_col]).strip() if tags_col and pd.notna(row[tags_col]) else None,
                )
                session.add(indice)

            session.commit()

    def listar(self) -> list[IndiceLinha]:
        with self.sessionmaker() as session:
            registros = session.scalars(
                select(IndiceORM).order_by(IndiceORM.nome_arquivo)
            ).all()

        return [
            IndiceLinha(
                nome_arquivo=registro.nome_arquivo,
                fazenda=registro.fazenda,
                peso=Decimal(str(registro.peso)),
                tags=normalizar_tags(registro.tags),
            )
            for registro in registros
        ]


class AvaliacaoSQLiteRepository:
    def __init__(self, sqlite_path: str = SQLITE_PATH):
        self.sqlite_path = sqlite_path
        criar_tabelas_sqlite(sqlite_path)
        self.sessionmaker = criar_sessionmaker_sqlite(sqlite_path)

    def salvar_avaliacao(self, avaliacao) -> None:
        with self.sessionmaker() as session:
            avaliacao_imagem = session.get(AvaliacaoImagemORM, avaliacao.nome_arquivo)
            if avaliacao_imagem is None:
                avaliacao_imagem = AvaliacaoImagemORM(nome_arquivo=avaliacao.nome_arquivo)
                session.add(avaliacao_imagem)

            avaliacao_imagem.area_ground_truth = (
                float(avaliacao.ground_truth.area)
                if avaliacao.ground_truth.area is not None
                else None
            )
            avaliacao_imagem.perimetro_ground_truth = (
                float(avaliacao.ground_truth.perimetro)
                if avaliacao.ground_truth.perimetro is not None
                else None
            )

            existentes = {
                registro.modelo: registro
                for registro in session.scalars(
                    select(AvaliacaoModeloORM).where(
                        AvaliacaoModeloORM.nome_arquivo == avaliacao.nome_arquivo
                    )
                )
            }

            for modelo_avaliado in avaliacao.modelos.values():
                registro_modelo = existentes.get(modelo_avaliado.modelo)
                if registro_modelo is None:
                    registro_modelo = AvaliacaoModeloORM(
                        nome_arquivo=avaliacao.nome_arquivo,
                        modelo=modelo_avaliado.modelo,
                    )
                    session.add(registro_modelo)

                registro_modelo.area = (
                    float(modelo_avaliado.area)
                    if modelo_avaliado.area is not None
                    else None
                )
                registro_modelo.perimetro = (
                    float(modelo_avaliado.perimetro)
                    if modelo_avaliado.perimetro is not None
                    else None
                )
                registro_modelo.iou = (
                    float(modelo_avaliado.iou)
                    if modelo_avaliado.iou is not None
                    else None
                )

            session.commit()

    def carregar_metricas_dataframe(self) -> pd.DataFrame:
        with self.sessionmaker() as session:
            rows = session.execute(
                select(
                    AvaliacaoImagemORM.nome_arquivo,
                    AvaliacaoModeloORM.modelo,
                    AvaliacaoModeloORM.area,
                    AvaliacaoModeloORM.perimetro,
                    AvaliacaoModeloORM.iou,
                    AvaliacaoImagemORM.area_ground_truth,
                    AvaliacaoImagemORM.perimetro_ground_truth,
                ).join(
                    AvaliacaoModeloORM,
                    AvaliacaoModeloORM.nome_arquivo == AvaliacaoImagemORM.nome_arquivo,
                )
            ).all()

        if not rows:
            return pd.DataFrame()

        registros: list[dict[str, float | str]] = []
        for row in rows:
            area = row.area
            perimetro = row.perimetro
            iou = row.iou
            area_gt = row.area_ground_truth
            perimetro_gt = row.perimetro_ground_truth

            if (
                area is None
                or perimetro is None
                or iou is None
                or area_gt is None
                or perimetro_gt is None
            ):
                continue

            area_diff_abs = abs(area - area_gt)
            perimetro_diff_abs = abs(perimetro - perimetro_gt)
            area_similarity = 1.0 - (area_diff_abs / area_gt) if area_gt > 0 else 0.0
            perimetro_similarity = (
                1.0 - (perimetro_diff_abs / perimetro_gt)
                if perimetro_gt > 0
                else 0.0
            )

            registros.append(
                {
                    "nome_arquivo": row.nome_arquivo,
                    "modelo": row.modelo,
                    "area": area,
                    "perimetro": perimetro,
                    "iou": iou,
                    "area_gt": area_gt,
                    "perimetro_gt": perimetro_gt,
                    "area_diff_abs": area_diff_abs,
                    "area_similarity": max(0.0, area_similarity),
                    "perimetro_diff_abs": perimetro_diff_abs,
                    "perimetro_similarity": max(0.0, perimetro_similarity),
                }
            )

        return pd.DataFrame(registros)
