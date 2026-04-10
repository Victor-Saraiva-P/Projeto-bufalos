# Execucoes multiplas para avaliar estabilidade

Este documento registra a decisao tecnica de preservar multiplas execucoes da mesma inferencia no pipeline.

## Contexto

Os modelos de segmentacao usados no projeto sao modelos externos. Mesmo quando a qualidade media de segmentacao e boa, existe interesse em verificar depois se a mesma imagem produz saidas uniformes entre repeticoes da inferencia.

Para isso, o projeto precisa guardar cada repeticao como um artefato distinto, em vez de sobrescrever a mascara anterior.

## Decisao adotada

- introduzir `execucao` como dimensao estrutural do pipeline;
- controlar a quantidade de execucoes por `num_execucoes` em `config.toml`;
- salvar segmentacoes brutas em `generated/segmentacoes_brutas/execucao_N/<modelo>/`;
- salvar segmentacoes binarizadas em `generated/segmentacoes_binarizadas/execucao_N/<estrategia>/<modelo>/`;
- persistir `execucao` nas tabelas `segmentacao_bruta` e `segmentacao_binarizada`;
- manter `ground_truth_binarizada` fora dessa dimensao, porque a referencia manual nao muda entre execucoes.

## Motivo

- evita perder informacao quando a mesma imagem e processada mais de uma vez;
- permite rastrear exatamente de qual execucao veio cada artefato e cada avaliacao;
- prepara o banco e o filesystem para futuras analises de estabilidade sem misturar isso com a implementacao atual do pipeline;
- preserva o fluxo existente de segmentar, binarizar e avaliar, mudando apenas a estrutura de armazenamento.

## Consequencias

- a chave composta das segmentacoes passa a incluir `execucao`;
- os controllers precisam iterar de `1` ate `num_execucoes`;
- o criterio de `skip` passa a considerar a execucao;
- analises estatisticas entre execucoes ficam para uma etapa posterior.

## Estado atual da analise

A etapa posterior de analise de estabilidade ja passou a existir neste worktree.

Para a leitura dos resultados observados nos graficos do notebook 05, consulte:

- `docs/avaliacao/estabilidade-entre-execucoes.md`

Para a decisao complementar de usar apenas uma execucao configurada na analise da segmentacao binarizada, consulte:

- `docs/decisoes-tecnicas/analise-da-segmentacao-binarizada-por-execucao-fixa.md`
