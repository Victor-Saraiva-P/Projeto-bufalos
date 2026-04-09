# Plano de Reestruturacao dos Notebooks 04 e 05

## Objetivo desta etapa

Esta etapa substitui o notebook `notebooks/04_analise_das_avaliacoes.ipynb`, que hoje esta orientado a ranking final de modelos apos binarizacao, por uma nova estrutura voltada a responder uma pergunta anterior no pipeline:

- qual a melhor forma de avaliar e comparar a segmentacao bruta, antes da binarizacao.

O foco imediato nao e escolher o melhor modelo final e nem a melhor binarizacao. O foco imediato e:

- consolidar as metricas ja existentes de segmentacao bruta;
- montar uma camada estatistica confiavel em cima dessas metricas;
- identificar quais modelos e quais caracteristicas de imagem tendem a produzir segmentacoes piores ou melhores;
- usar as tags como variaveis explicativas para entender por que uma segmentacao falha.

## Decisao de produto para os notebooks

### Notebook 04

O novo `04` sera o notebook de calculo estatistico e consolidacao analitica.

Responsabilidades:

- carregar os dados persistidos no SQLite;
- materializar uma base analitica unica para segmentacao bruta;
- validar consistencia dos dados;
- calcular estatisticas descritivas;
- calcular comparacoes entre modelos;
- calcular comparacoes por grupo de tags;
- estimar estabilidade entre execucoes;
- produzir tabelas de resultado persistiveis para reutilizacao posterior;
- preparar saidas que alimentarao o notebook 05.

Ele nao deve:

- gerar a maior parte dos graficos finais;
- depender de cache em `.csv` ou `.xlsx`;
- misturar analise de segmentacao bruta com analise de binarizacao;
- tentar decidir o melhor modelo final do projeto inteiro.

### Notebook 05

O novo `05` sera o notebook de visualizacao da segmentacao bruta.

Responsabilidades:

- consumir as tabelas analiticas produzidas pelo notebook 04;
- gerar graficos comparativos por modelo;
- gerar graficos por tag;
- mostrar distribuicoes, dispersoes, intervalos de confianca e estabilidade;
- destacar casos problematicos e padroes relevantes;
- apoiar a leitura qualitativa dos resultados estatisticos.

Ele nao deve:

- recalcular toda a camada estatistica pesada;
- reimplementar consolidacao de dados;
- introduzir regras de negocio analiticas divergentes do notebook 04.

## O que sera removido ou aposentado

### Notebook atual 04

O `notebooks/04_analise_das_avaliacoes.ipynb` atual deve ser considerado obsoleto.

Motivos:

- ele esta orientado ao ranking final de modelos;
- ele mistura a etapa de analise com conclusoes que ainda nao queremos tirar;
- ele depende de metricas binarizadas como `iou`, `area_similarity` e `perimetro_similarity`;
- ele nao trata tags como eixo explicativo principal;
- ele nao organiza a analise em blocos reutilizaveis para as proximas etapas do projeto.

Na execucao futura da tarefa, a intencao deve ser:

- apagar o notebook atual;
- substituir por um novo `04_analise_estatistica_segmentacao_bruta.ipynb` ou manter o mesmo nome `04_analise_das_avaliacoes.ipynb` com conteudo totalmente novo.

Eu recomendo manter a numeracao `04`, mas atualizar o titulo interno e a finalidade do arquivo para deixar claro que ele trata apenas da analise estatistica da segmentacao bruta.

### Cache em arquivo

Qualquer cache analitico em `.csv` ou `.xlsx` usado por esse fluxo deve ser removido desta etapa.

Diretriz:

- a fonte de verdade deve continuar sendo o SQLite;
- se for necessario persistir resultados intermediarios, isso deve acontecer em tabelas SQLite dedicadas;
- o notebook 05 deve ler essas tabelas, e nao arquivos soltos.

## Estado atual do projeto que precisa ser respeitado

O repositorio ja possui:

- persistencia central em SQLite;
- entidades para `Imagem`, `Tag`, `SegmentacaoBruta`, `SegmentacaoBinarizada` e `GroundTruthBinarizada`;
- tags normalizadas no banco via relacionamento `imagem_tag`;
- metricas de segmentacao bruta ja persistidas em `SegmentacaoBruta`:
  - `auprc`
  - `soft_dice`
  - `brier_score`
- metricas de segmentacao binarizada persistidas em `SegmentacaoBinarizada`:
  - `iou`
  - `area`
  - `perimetro`

Logo, a primeira reestruturacao deve aproveitar o que ja existe, em vez de reinventar um pipeline paralelo.

## Perguntas analiticas que o novo Notebook 04 precisa responder

Nesta fase, o notebook 04 deve responder pelo menos estas perguntas:

1. Quais modelos apresentam melhor desempenho medio na segmentacao bruta?
2. Quais modelos sao mais estaveis entre execucoes?
3. Quais metricas contam historias consistentes entre si, e quais entram em conflito?
4. Quais tags estao associadas a pior desempenho?
5. Quais combinacoes de tags tendem a degradar mais os resultados?
6. Existe diferenca estatisticamente defensavel entre modelos, ou a diferenca observada e pequena demais?
7. Quais modelos sao mais sensiveis a casos dificeis, como `multi_bufalos`, `ocluido` ou `baixo_contraste`?

## Base analitica que deve ser montada

O notebook 04 deve montar uma tabela analitica primaria em nivel de:

- imagem
- modelo
- execucao

Essa tabela deve conter, no minimo:

- `nome_arquivo`
- `fazenda`
- `peso`
- `modelo`
- `execucao`
- `auprc`
- `soft_dice`
- `brier_score`
- indicadores de tag por imagem
- lista textual de tags da imagem
- quantidade de tags por imagem
- flag para `ok`
- flags binarias para cada tag relevante

### Enriquecimento com tags

Como uma imagem pode ter mais de uma tag, a materializacao deve gerar colunas derivadas como:

- `tag_ok`
- `tag_multi_bufalos`
- `tag_cortado`
- `tag_angulo_extremo`
- `tag_baixo_contraste`
- `tag_ocluido`
- `num_tags_problema`

Tambem vale gerar colunas auxiliares:

- `tem_tag_problema`
- `tags_sem_ok`
- `grupo_dificuldade`

`grupo_dificuldade` pode ser uma classificacao derivada, por exemplo:

- `ok`
- `1_problema`
- `2_ou_mais_problemas`

Isso ajuda a enxergar rapidamente gradiente de dificuldade.

## Persistencia recomendada no SQLite

Para eliminar caches em arquivo e permitir reuso pelo notebook 05, a proposta e criar uma camada analitica persistida no SQLite.

### Tabelas recomendadas

#### `analise_segmentacao_bruta_base`

Tabela materializada com uma linha por `imagem + modelo + execucao`.

Finalidade:

- servir de base unica para analise estatistica;
- alimentar diretamente o notebook 05;
- permitir auditoria e reproducao.

#### `analise_segmentacao_bruta_resumo_modelo`

Resumo agregado por modelo.

Colunas esperadas:

- metricas medias
- medianas
- desvio padrao
- intervalo interquartil
- quantidade de amostras
- intervalo de confianca

#### `analise_segmentacao_bruta_resumo_tag`

Resumo agregado por tag e por modelo.

Finalidade:

- medir impacto marginal de cada tag;
- comparar como cada modelo reage a cada dificuldade.

#### `analise_segmentacao_bruta_testes`

Tabela com resultados dos testes estatisticos.

Colunas esperadas:

- conjunto comparado
- metrica
- teste usado
- hipotese nula
- estatistica
- `p_value`
- ajuste para multiplas comparacoes
- tamanho de efeito
- interpretacao resumida

#### `analise_segmentacao_bruta_estabilidade`

Tabela focada em estabilidade entre execucoes.

Colunas esperadas:

- modelo
- metrica
- media
- desvio padrao entre execucoes
- coeficiente de variacao
- amplitude
- ranking por estabilidade

## Metricas foco desta etapa

Nesta etapa, o foco deve ser exclusivamente nas metricas de segmentacao bruta:

- `auprc`
- `soft_dice`
- `brier_score`

### Papel de cada metrica

#### `AUPRC`

Usar como medida principal de separacao entre foreground e background ao longo dos limiares.

Interpretacao:

- maior e melhor;
- especialmente util quando o problema e desbalanceado em pixels.

#### `Soft Dice`

Usar como medida complementar de sobreposicao suave sem binarizacao.

Interpretacao:

- maior e melhor;
- ajuda a medir concentracao de probabilidade sobre a regiao correta.

#### `Brier Score`

Usar como medida de erro probabilistico.

Interpretacao:

- menor e melhor;
- deve ser invertido ou tratado separadamente quando houver agregacao comparativa.

## Estrategia estatistica proposta

### 1. Analise descritiva inicial

Para cada modelo e para cada metrica:

- media
- mediana
- desvio padrao
- minimo
- maximo
- quartis
- intervalo interquartil
- intervalo de confianca por bootstrap

Objetivo:

- entender centro, dispersao e assimetria;
- evitar conclusao baseada apenas em media.

### 2. Analise de estabilidade entre execucoes

Como existem multiplas execucoes por modelo, esta etapa deve medir estabilidade.

Calculos recomendados:

- media por execucao;
- desvio padrao entre execucoes;
- coeficiente de variacao;
- diferenca entre melhor e pior execucao;
- consistencia da ordem dos modelos entre execucoes.

Objetivo:

- distinguir modelo bom de modelo confiavel;
- evitar escolher um modelo que so parece bom em uma execucao isolada.

### 3. Comparacao entre modelos

Comparar modelos para cada metrica, inicialmente sem misturar tags.

Abordagem recomendada:

- verificar distribuicao empirica por modelo;
- preferir testes nao parametricos se a normalidade nao for defensavel;
- usar comparacao global e depois comparacoes pareadas.

Sugestao pratica:

- teste global: `Kruskal-Wallis`;
- pos-hoc: `Dunn` com correcao de Holm ou Benjamini-Hochberg;
- para efeito tamanho: `Cliff's Delta` ou equivalente nao parametrico.

Se o desenho por imagem permitir emparelhamento forte entre modelos na mesma imagem, avaliar tambem:

- `Friedman` para comparacao global emparelhada;
- `Wilcoxon signed-rank` nos pares.

Objetivo:

- dizer nao apenas quem tem media maior, mas se a diferenca e estatisticamente defensavel.

### 4. Impacto das tags

As tags precisam deixar de ser apenas metadado e passar a ser parte central da analise.

Analises recomendadas:

- comparar distribuicao das metricas entre imagens com e sem cada tag;
- comparar desempenho por numero de problemas na imagem;
- medir se determinado modelo perde mais desempenho que outros quando uma tag aparece.

Exemplos:

- impacto de `multi_bufalos` em `auprc`;
- impacto de `baixo_contraste` em `soft_dice`;
- impacto de `ocluido` em `brier_score`;
- efeito acumulado de `2_ou_mais_problemas`.

Testes recomendados:

- `Mann-Whitney U` para grupos independentes simples;
- `Kruskal-Wallis` para mais de dois grupos;
- regressao com variaveis indicadoras de tags, quando a base estiver suficientemente estavel.

### 5. Interacoes entre modelo e dificuldade

Depois da leitura por tag isolada, analisar interacao:

- quais modelos sofrem mais com `multi_bufalos`;
- quais modelos degradam mais em `baixo_contraste`;
- quais modelos sao mais robustos a `ocluido`.

Abordagem recomendada:

- delta de desempenho entre grupo `sem tag` e `com tag`;
- ranking de robustez por tag;
- modelos lineares simples ou modelos mistos em fase posterior, se necessario.

### 6. Analise de correlacao entre metricas

Antes de usar qualquer score agregado no futuro, verificar se as metricas contam historias redundantes ou complementares.

Calculos recomendados:

- correlacao de Spearman entre `auprc`, `soft_dice` e `brier_score`;
- matriz de correlacao global;
- correlacao por modelo;
- correlacao por subgrupo de dificuldade.

Objetivo:

- entender se uma metrica pode estar dominando a interpretacao;
- evitar score composto prematuro.

## O que nao fazer agora

Nesta etapa, evitar:

- ranking final unico do projeto;
- mistura com metricas de binarizacao;
- escolha definitiva da melhor estrategia de threshold;
- score agregado arbitrario sem validacao estatistica;
- graficos pesados dentro do notebook 04;
- conclusoes causais fortes demais baseadas apenas em correlacao.

## Estrutura sugerida para o novo Notebook 04

### Bloco 1. Escopo e criterio da analise

Definir claramente:

- foco apenas em segmentacao bruta;
- metricas utilizadas;
- papel das tags;
- o que fica fora desta etapa.

### Bloco 2. Carregamento da base

- leitura do SQLite;
- materializacao da base analitica;
- validacoes de integridade;
- contagem de imagens, modelos e execucoes.

### Bloco 3. Persistencia da base analitica

- gravar `analise_segmentacao_bruta_base`;
- registrar timestamp e parametros da execucao.

### Bloco 4. Estatistica descritiva

- resumo global por modelo;
- resumo por execucao;
- resumo por tag;
- persistencia dos resumos.

### Bloco 5. Testes estatisticos

- testes globais entre modelos;
- testes pareados;
- comparacoes por tag;
- tamanhos de efeito;
- correcoes de multiplas comparacoes;
- persistencia dos resultados.

### Bloco 6. Estabilidade

- analise por execucao;
- dispersao intra-modelo;
- consistencia de ranking por metrica;
- persistencia da tabela de estabilidade.

### Bloco 7. Correlacoes e conclusoes tecnicas

- correlacoes entre metricas;
- pontos de cautela;
- perguntas abertas para o notebook 05 e para a futura etapa de binarizacao.

## Estrutura sugerida para o novo Notebook 05

### Bloco 1. Leitura das tabelas prontas

- carregar as tabelas analiticas do SQLite;
- nao recalcular a camada pesada.

### Bloco 2. Graficos globais por modelo

Sugestoes:

- boxplot
- violin plot
- raincloud plot se o stack permitir
- barras com intervalo de confianca

### Bloco 3. Graficos de estabilidade

Sugestoes:

- linha por execucao
- erro padrao por modelo
- heatmap de ranking por execucao

### Bloco 4. Graficos por tag

Sugestoes:

- boxplots por tag e modelo
- slope charts mostrando perda de desempenho com tag
- forest plots de efeito por tag

### Bloco 5. Casos mais representativos

Sugestoes:

- tabelas dos piores grupos por tag;
- selecao de imagens exemplares para futuras inspecoes visuais;
- cruzamento entre resultado ruim e combinacao de tags.

## Implementacao recomendada no codigo Python

Para a execucao futura da tarefa, eu recomendo criar uma camada analitica explicita em `src/analysis/`, em vez de concentrar toda a logica dentro do notebook.

### Modulos sugeridos

- `src/analysis/segmentacao_bruta_base.py`
- `src/analysis/segmentacao_bruta_stats.py`
- `src/analysis/segmentacao_bruta_tests.py`
- `src/analysis/segmentacao_bruta_persistence.py`

### Responsabilidade de cada modulo

`segmentacao_bruta_base.py`

- construir DataFrame base a partir do SQLite;
- explodir tags e gerar features derivadas;
- padronizar nomes de colunas.

`segmentacao_bruta_stats.py`

- calcular resumos por modelo, execucao e tag;
- calcular intervalos de confianca;
- medir estabilidade.

`segmentacao_bruta_tests.py`

- centralizar testes estatisticos;
- aplicar correcoes de multiplas comparacoes;
- calcular tamanhos de efeito;
- devolver saidas tabulares.

`segmentacao_bruta_persistence.py`

- salvar DataFrames analiticos no SQLite;
- versionar tabelas ou sobrescrever de forma controlada;
- expor funcoes de leitura para o notebook 05.

## Dependencias estatisticas que podem ser necessarias

Dependendo do stack atual do projeto, pode valer incorporar:

- `scipy`
- `statsmodels`
- `scikit-posthocs`

Se alguma delas ainda nao estiver no projeto, a tarefa futura deve decidir entre:

- adicionar a dependencia;
- ou implementar uma primeira versao mais enxuta usando apenas o que ja existe.

Minha recomendacao e:

- usar `scipy` para testes base;
- usar `statsmodels` para ajuste de `p-value`;
- usar `scikit-posthocs` apenas se realmente simplificar o pos-hoc.

## Sequencia de execucao da tarefa futura

1. Apagar o conteudo atual do notebook 04.
2. Definir se o nome do arquivo `04` sera mantido ou renomeado.
3. Criar a camada Python de analise estatistica em `src/analysis/`.
4. Materializar a base analitica de segmentacao bruta a partir do SQLite.
5. Criar tabelas analiticas persistidas no SQLite.
6. Reescrever o notebook 04 como notebook de calculo estatistico.
7. Criar o notebook 05 apenas para visualizacao.
8. Ajustar ou criar testes automatizados para a nova camada analitica.
9. Atualizar `README.md`, `docs/` e `AGENTS.md` para refletir o novo fluxo.

## Riscos e cuidados

### Mistura de granularidade

Um erro facil aqui e misturar:

- linha por imagem;
- linha por imagem + modelo;
- linha por imagem + modelo + execucao.

A granularidade padrao desta etapa deve ser:

- `imagem + modelo + execucao`

Os agregados devem sempre deixar explicito de onde vieram.

### Tags multiplas

Como uma imagem pode ter varias tags, a analise por grupo precisa deixar claro:

- se o grupo e inclusivo, por exemplo "tem `multi_bufalos`";
- ou se e exclusivo, por exemplo "somente `multi_bufalos`".

Minha recomendacao e começar pelo criterio inclusivo, por ser mais util e mais robusto com base pequena.

### Dependencia entre observacoes

Como a mesma imagem aparece em varios modelos e execucoes, parte da analise tem dependencia estrutural.

Consequencia:

- testes que assumem independencia total podem distorcer a leitura;
- por isso, sempre que viavel, usar comparacoes emparelhadas por imagem.

### Conclusoes excessivas

O objetivo do notebook 04 nao e provar causalidade.

O objetivo e:

- detectar padroes;
- quantificar diferencas;
- mostrar sinais consistentes;
- priorizar proximas decisoes do pipeline.

## Resultado esperado desta reestruturacao

Ao final dessa entrega, o projeto deve passar a ter:

- um notebook 04 focado em estatistica da segmentacao bruta;
- um notebook 05 focado em graficos da segmentacao bruta;
- uma base analitica persistida no SQLite, sem cache solto em arquivo;
- uma leitura clara do impacto das tags sobre a qualidade da segmentacao;
- base tecnica para, depois, repetir o mesmo desenho para binarizacao no futuro notebook 06.

## Recomendacao final

Minha recomendacao de implementacao e atacar esta reestruturacao em duas camadas:

1. primeiro construir a base analitica persistida e os testes estatisticos em codigo Python reutilizavel;
2. depois usar os notebooks apenas como interface de execucao, leitura e visualizacao.

Isso reduz retrabalho, evita logica escondida em notebook e deixa a analise preparada para crescer quando o projeto entrar na etapa de binarizacao.
