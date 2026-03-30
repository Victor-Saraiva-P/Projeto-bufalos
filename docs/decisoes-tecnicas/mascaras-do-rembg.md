# Mascaras do `rembg`

Este documento registra a decisao tecnica sobre como as mascaras sao geradas na etapa de segmentacao com `rembg`.

## Implementacao relacionada

- `src/controllers/segmentacao_controller.py`
- `src/services/segmentacao_service.py`
- `config.toml`

## Comportamento atual no codigo

Na geracao das mascaras previstas, o codigo atual usa:

```python
remove(
    input_rembg,
    only_mask=True,
    session=rembg_session,
)
```

Isso significa que a saida gerada nessa etapa e uma mascara em escala de cinza, salva em `generated/predicted_masks_raw/<modelo>/`.

O formato de arquivo configurado para essa saida e `PNG`, conforme `config.toml`.

## Decisao adotada

- manter a etapa de geracao do `rembg` produzindo mascaras em escala de cinza com `only_mask=True`;
- fazer a conversao para mascara binaria apenas na etapa posterior de binarizacao.

## Motivo

- separa a inferencia da etapa de pos-processamento;
- preserva a saida original do modelo antes da binarizacao;
- permite reavaliar a binarizacao sem rerodar a inferencia da segmentacao.
