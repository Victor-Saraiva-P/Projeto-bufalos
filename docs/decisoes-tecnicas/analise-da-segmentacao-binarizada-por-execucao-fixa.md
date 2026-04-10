# Analise da segmentacao binarizada por execucao fixa

Este documento registra a decisao tecnica de analisar a segmentacao binarizada usando apenas uma execucao configuravel, em vez de agregar todas as execucoes disponiveis.

## Contexto

O pipeline preserva multiplas execucoes por imagem e por modelo porque isso continua sendo importante para a etapa de estabilidade da segmentacao bruta.

Essa decisao continua valida e esta descrita em:

- `docs/decisoes-tecnicas/execucoes-multiplas-para-avaliar-estabilidade.md`
- `docs/avaliacao/estabilidade-entre-execucoes.md`

Ao mesmo tempo, a analise da segmentacao binarizada passou a ter um problema pratico diferente: a combinacao de modelos, estrategias de binarizacao e execucoes aumenta muito o volume da base analitica e o custo dos testes estatisticos, sem trazer ganho proporcional de interpretacao.

## Evidencia usada

Os resultados de estabilidade da segmentacao bruta mostram variacao muito pequena entre execucoes.

Valores destacados em `docs/avaliacao/estabilidade-entre-execucoes.md`:

- em `AUPRC`, o maior `cv_execucoes` observado foi `0.000197` para `u2net`;
- em `Soft Dice`, o maior `cv_execucoes` observado foi `0.000052` para `u2net`;
- em `Brier Score`, o maior `cv_execucoes` observado foi `0.000069` para `silueta`.

Leitura tecnica:

- ha variacao residual entre execucoes;
- essa variacao existe, mas e muito pequena;
- para a analise da segmentacao binarizada, ela nao aparece como fator dominante frente ao custo combinatorio introduzido por manter todas as repeticoes.

## Explosao combinatoria

Com a configuracao atual do projeto:

- `14` modelos ativos;
- `8` estrategias de binarizacao;
- `3` execucoes;
- `3` metricas principais da segmentacao binarizada: `iou`, `precision` e `recall`.

Isso produz:

- `14 x 8 x 3 = 336` combinacoes de `modelo x estrategia x execucao` por imagem;
- se a analise usa apenas uma execucao, esse numero cai para `14 x 8 = 112` combinacoes por imagem;
- a reducao e de `224` combinacoes por imagem, ou `66,7%`.

Nos testes entre estrategias, o problema tambem cresce rapido:

- `8` estrategias geram `C(8, 2) = 28` comparacoes pareadas por metrica;
- com `3` metricas, isso ja significa `84` comparacoes globais;
- se abrir por `14` modelos, o total sobe para `84 x 14 = 1176` comparacoes;
- se ainda multiplicar a leitura por `3` execucoes, chega-se a `1176 x 3 = 3528` comparacoes.

Esse aumento torna:

- o notebook 06 mais lento, especialmente em bootstrap e testes nao parametricos;
- o notebook 07 mais carregado e menos legivel;
- a iteracao local mais cara em CPU, memoria e tempo.

## Decisao adotada

Para a analise da segmentacao binarizada:

- manter todas as execucoes armazenadas no pipeline e no SQLite;
- usar apenas uma execucao escolhida em `config.toml` para montar a base analitica dos notebooks 06 e 07;
- controlar essa escolha pela chave `[analysis.segmentacao_binarizada].execucao_escolhida`;
- deixar a discussao de estabilidade entre execucoes restrita ao fluxo de segmentacao bruta.

Exemplo:

```toml
[analysis.segmentacao_binarizada]
execucao_escolhida = 1
```

## Consequencias

- a analise binarizada deixa de misturar o problema de qualidade da binarizacao com o problema de estabilidade entre execucoes;
- o notebook 06 passa a trabalhar com uma base menor e mais barata de recalcular;
- o notebook 07 fica focado na pergunta principal: qual estrategia de binarizacao performa melhor;
- mudar a execucao analisada continua sendo possivel por configuracao, sem perder os artefatos das outras execucoes.

## Observacao importante

Essa decisao nao elimina as outras execucoes do projeto.

Ela apenas reduz a granularidade usada na analise estatistica da segmentacao binarizada, porque a evidencia atual aponta alta repetibilidade entre execucoes e porque o custo de carregar todas elas nessa etapa e desproporcional ao beneficio analitico.
