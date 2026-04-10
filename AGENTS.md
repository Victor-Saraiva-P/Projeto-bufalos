# Projeto Bufalos: Contexto Consolidado Para Agentes

Este arquivo e a copia consolidada do contexto documental do repositorio.

Regra do projeto:

- `AGENTS.md` e a cópia em arquivo unico para uso de agentes de IA.
- `README.md` e a porta de entrada humana, com visao geral, comandos basicos e mapa da documentacao.
- `docs/` e a versao humana organizada por tema.
- Nenhum conhecimento operacional, conceitual ou normativo deve existir apenas em um dos lados.
- Se um tema for adicionado, alterado ou removido em `README.md` ou em `docs/`, a mesma informacao deve ser refletida em `AGENTS.md`.
- Se um tema for adicionado, alterado ou removido em `AGENTS.md`, a mesma informacao deve existir em `README.md` ou em algum arquivo de `docs/`.
- Durante o desenvolvimento, o trabalho deve acontecer em apenas um unico worktree por vez.
- Nunca mexer em mais de um worktree ao mesmo tempo.
- Se o usuario nao especificar qual worktree deve ser usado, e preciso perguntar antes de editar qualquer arquivo.
- Sempre que um novo `worktree` for criado, o setup local deve ser repetido dentro dele com `mise`, criacao de `.venv`, ativacao do ambiente e `pip install -e .`.
- Nunca assumir que a `.venv` de outro `worktree` serve para o atual.

## Visao Geral

Este repositorio contem o projeto de avaliacao de modelos de remocao de fundo em imagens de bufalos.

O fluxo principal do projeto e:

1. gerar mascaras previstas com modelos de segmentacao;
2. binarizar mascaras previstas e mascaras de referencia;
3. calcular metricas por imagem e por modelo;
4. materializar bases analiticas a partir do SQLite;
5. produzir visualizacoes para interpretacao dos resultados.

No estado atual deste worktree, os notebooks operacionais executam esse fluxo nesta ordem:

1. `notebooks/01_geracao_mascaras_e_segmentacao.ipynb`
2. `notebooks/02_binarizacao_mascaras.ipynb`
3. `notebooks/03_calculo_das_avaliacoes.ipynb`

Estado de transicao:

- o antigo `notebooks/04_analise_das_avaliacoes.ipynb` foi removido desta branch por estar acoplado ao ranking final pos-binarizacao;
- os novos notebooks 04 e 05 serao recriados para a etapa de analise estatistica e visualizacao da segmentacao bruta;
- o plano desta reestruturacao esta em `PLANO_REESTRUTURACAO_NOTEBOOKS_04_05.md`.

Observacao sobre o notebook 02:

- o ground truth usa uma estrategia dedicada e conservadora, `GroundTruthLimiarGlobal`;
- as segmentacoes previstas continuam usando as estrategias configuradas para os modelos, como `GaussianaOpening`.

## Estrutura Do Repositorio

Pastas principais:

- `src/`: codigo principal do projeto;
- `src/models/`: entidades persistidas do dominio (`Imagem`, `Segmentacao`, `Binarizacao`, `Tag`, etc.);
- `src/repositories/`: persistencia CRUD baseada nas entidades;
- `src/sqlite/`: infraestrutura de sessao, `Base` e configuracao do SQLite;
- `src/controllers/` e `src/services/`: orquestracao dos fluxos e casos de uso;
- `src/segmentacao/`: fachadas da etapa de segmentacao e verificacoes de integridade;
- `src/binarizacao/`: fachadas da etapa de binarizacao;
- `src/logs/`: logging compartilhado entre segmentacao, binarizacao e verificacoes de integridade;
- `src/metricas/`: contratos compartilhados de metricas;
- `src/metricas/segmentacao_binarizada/`: metricas concretas da segmentacao binarizada;
- `src/analysis/` e `src/visualization/`: coleta analitica, materializacao e apoio a visualizacao;
- `src/tagging/`: anotadores manuais de tags de curadoria;
- `tests/`: suite automatizada;
- `notebooks/`: fluxo exploratorio e analitico do projeto;
- `docs/`: documentacao organizada por tema;
- `data/`: dados de entrada esperados pelo pipeline;
- `generated/`: artefatos gerados durante segmentacao, binarizacao e avaliacao.

Estrutura minima esperada em `data/`:

```text
data/
  ground_truth_brutos/ # mascaras de referencia
  images/              # imagens originais de entrada
  Indice.xlsx          # planilha usada no tagging e no bootstrap inicial do SQLite
```

Saidas esperadas em `generated/`:

```text
generated/
  segmentacoes_brutas/
    execucao_1/               # mascaras brutas geradas pelos modelos em cada execucao
  segmentacoes_binarizadas/
    execucao_1/               # mascaras apos binarizacao, agrupadas por estrategia e execucao
  ground_truth_binarizada/    # mascaras manuais apos binarizacao
  evaluation/                 # artefatos de avaliacao
  bufalos.sqlite3             # fonte de verdade do pipeline
```

## Setup E Execucao Local

Pre-requisitos:

- Python 3.13 recomendado;
- o projeto requer Python `>= 3.12` e `< 3.14`;
- `tkinter` disponivel no Python para rodar os anotadores manuais;
- Jupyter instalado no ambiente para executar os notebooks;
- GPU NVIDIA com CUDA e opcional.

Para evitar problemas no uso de `src/tagging/manual_tagger.py`, prefira Python 3.13.

Instalacao basica:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Instalacao com `mise`, caminho recomendado:

```bash
mise exec python@3.13 -- python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Regra para novo `worktree`:

- repetir esse fluxo em cada `worktree` novo;
- executar `pytest`, notebooks e scripts sempre com a `.venv` do `worktree` corrente ativada.

Alternativa com `mise use`:

```bash
mise use python@3.13
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Comandos basicos de desenvolvimento:

- `jupyter notebook`: abre o ambiente de notebooks;
- `pytest`: executa toda a suite automatizada;
- `pytest -m "not e2e"`: executa a suite rapida sem testes end-to-end;
- `pytest --cov=src --cov-report=term-missing`: executa a suite com coverage no terminal.

## Tagging Manual

### Anotador manual de tags

O script `src/tagging/manual_tagger.py` abre uma interface grafica para revisar imagens pendentes e preencher a coluna `tags` de `data/Indice.xlsx`.

Comandos:

```bash
python -m src.tagging.manual_tagger
```

```bash
python src/tagging/manual_tagger.py
```

Pre-requisitos:

- `data/Indice.xlsx` precisa existir;
- a planilha precisa ter a coluna `nome do arquivo`;
- as imagens precisam estar em `data/images/`;
- o ambiente precisa ter suporte grafico e `tkinter`.

Comportamento do fluxo:

- o app carrega apenas linhas ainda sem valor na coluna `tags`;
- `1` a `5` alternam as tags disponiveis;
- `Enter` salva a imagem atual e avanca;
- `Enter` sem nenhuma tag marcada grava `ok`;
- ao fechar a janela, o app salva a selecao atual se houver tags marcadas.

Se o app abortar no Linux ou Wayland com erro `xcb`, o problema pode estar no runtime `Python + Tk`, e nao no codigo do projeto.

### Anotador por foco

O script `src/tagging/focused_tagger.py` permite revisar uma tag por vez, preservando tags ja existentes.

Comandos:

```bash
python -m src.tagging.focused_tagger
```

```bash
python src/tagging/focused_tagger.py
```

Comportamento do fluxo:

- na tela inicial, use `1` a `5` para escolher a tag-foco e `Enter` para confirmar;
- o app revisa apenas imagens que ainda nao possuem a tag-foco selecionada;
- durante a revisao, a tecla `1` alterna a marcacao da tag-foco para a imagem atual;
- `Enter` salva e avanca para a proxima imagem;
- se a celula ainda estiver vazia e nenhuma marcacao for feita, o fluxo grava `ok`;
- se a imagem ja tiver outras tags, elas sao preservadas.

## Sistema De Avaliacao

O sistema avalia cada modelo comparando a mascara prevista com a mascara de referencia.

Metricas principais:

- `iou`: mede sobreposicao entre previsao e ground truth;
- `area_diff_rel`: mede o erro relativo de area;
- `perimetro_diff_rel`: mede o erro relativo de contorno.

Na etapa de binarizacao e analise de mascaras com score continuo, o projeto ja
usa `AUPRC` (`Area Under the Precision-Recall Curve`), `Soft Dice` e
`Brier Score`.

Arquivos relevantes:

- `src/metricas/metrica_base.py`: contrato base das metricas reutilizaveis na pipeline;
- `src/metricas/segmentacao_binarizada/`: metricas concretas usadas na avaliacao das mascaras binarizadas;
- `src/models/`: entidades persistidas do SQLite e do dominio analitico (`Imagem`, `Segmentacao`, `Binarizacao`, `GroundTruthBinarizada`, `Tag`);
- `src/repositories/`: leitura e gravacao de entidades no banco;
- `src/controllers/segmentacao_controller.py`: coordena a geracao de mascaras e grava os arquivos previstos em `generated/`;
- `src/services/segmentacao_service.py`: executa a inferencia sem persistir entidades metricas parciais;
- `src/controllers/binarizacao_controller.py`: coordena a binarizacao e grava os artefatos binarios em `generated/`;
- `src/services/binarizacao_service.py`: executa a binarizacao sem criar entidades metricas incompletas no SQLite;
- `src/controllers/avaliacao_controller.py`: coordena o processamento e persistencia de uma imagem;
- `src/services/avaliacao_service.py`: calcula as metricas e preenche `Segmentacao` e `GroundTruthBinarizada`;
- `src/analysis/collector.py`: coleta as metricas para todas as imagens e modelos;
- `src/analysis/ranker.py`: transforma as metricas agregadas em ranking;
- `src/visualization/metric_plots.py`: gera graficos para inspecao das metricas;
- `src/visualization/image_grid.py`: monta grades visuais para comparar casos;
- `src/config.py`: define caminhos e pesos usados no ranking.

Saida gerada:

- `generated/bufalos.sqlite3`: banco SQLite usado como fonte de verdade da avaliacao.

Regra para mudancas de schema no SQLite:

- o arquivo `generated/bufalos.sqlite3` e tratado como artefato descartavel;
- nao e necessario criar arquivos de migracao;
- nao e necessario manter logica de migracao incremental de schema;
- quando o schema mudar, a pratica esperada e apagar o `.sqlite` e subir tudo de novo pelo fluxo normal do projeto.

Regra de responsabilidade entre camadas:

- notebooks 01 e 02 executam o pipeline por meio dos controllers em `src/controllers/`;
- controllers podem ler `src/config.py` e resolver caminhos, modelos e estrategias configuradas;
- services nao devem depender de `config`; eles recebem esses dados ja resolvidos por parametro.
- `Segmentacao`, `GroundTruthBinarizada` e `Binarizacao` so devem nascer quando as metricas completas forem calculadas.

Exemplo minimo para coletar metricas:

```python
from src.analysis import MetricsCollector

collector = MetricsCollector(force_recalculate=False)
df_metrics = collector.collect_all_metrics()
```

Interpretação das metricas:

- `iou`: varia entre `0` e `1`; quanto maior, melhor;
- `area_diff_rel`: quanto menor, melhor; ajuda a detectar excesso ou falta de area segmentada;
- `perimetro_diff_rel`: quanto menor, melhor; ajuda a medir a qualidade do contorno.

Interpretacao da `AUPRC`:

- mede quao bem um mapa de score da mascara separa pixels de bufalo dos pixels de fundo ao longo de varios limiares;
- valor proximo de `1.0`: os pixels positivos aparecem consistentemente com scores mais altos;
- valor proximo de `0.0`: o modelo nao ordena bem os pixels de bufalo acima do fundo;
- quanto maior a `AUPRC`, melhor a separacao entre bufalo e fundo.

Quando usar `AUPRC`:

- quando a classe positiva e rara;
- quando o fundo domina a maior parte da imagem;
- quando a analise precisa considerar o score bruto da mascara, sem depender de um unico threshold.

Implementacao no projeto:

- o calculo fica em `src/metricas/segmentacao_bruta/auprc.py`;
- a interface recebe `score_mask` continuo e `ground_truth_mask` binario;
- a metrica foi adicionada para o estagio de analise da segmentacao bruta, sem depender de um ranking final unico.

Metricas de segmentacao bruta com score continuo:

- `AUPRC`: avalia ranking de scores entre pixels de bufalo e fundo;
- `Soft Dice`: avalia cobertura e concentracao da massa de score em cima do
  ground truth;
- `Brier Score`: avalia erro probabilistico medio entre score previsto e ground
  truth binario.

Contrato atual dessas metricas:

- recebem `score_mask` normalizado em `[0, 1]`;
- recebem `ground_truth_mask` binario;
- sao persistidas em `SegmentacaoBruta` como `auprc`, `soft_dice` e
  `brier_score`;
- sao expostas pelo coletor analitico para uso em notebooks e futuras tabelas analiticas.

Formulas:

```text
IoU = intersecao / uniao
|area_modelo - area_gt| / area_gt
|perimetro_modelo - perimetro_gt| / perimetro_gt
```

Persistencia:

- por padrao, a coleta usa o SQLite do projeto como fonte de verdade;
- para forcar recalcucao, use `MetricsCollector(force_recalculate=True)`;
- isso sobrescreve os registros de avaliacao no banco.

Ao analisar resultados, normalmente vale olhar:

- distribuicao das metricas por modelo;
- top `N` e bottom `N` por imagem;
- estabilidade entre execucoes;
- comportamento por tags de curadoria.

## Tags De Curadoria

Objetivo das tags:

- agrupar casos que tendem a afetar a qualidade da segmentacao.

Decisao adotada:

- manter uma taxonomia fechada de tags para reduzir ambiguidade durante a curadoria.

Regras gerais:

- uma imagem pode receber mais de uma tag;
- a tag `ok` so deve ser usada quando nenhuma tag de problema se aplica;
- ausencia de tag significa `nao_revisada`, e nao imagem aprovada;
- as tags descrevem dificuldade de leitura visual da imagem, nao o desempenho final do modelo.

Conjunto de tags:

- `ok`
- `multi_bufalos`
- `cortado`
- `angulo_extremo`
- `baixo_contraste`
- `ocluido`

Definicoes:

- `ok`: imagem adequada para analise, sem ressalvas relevantes;
- `multi_bufalos`: mais de um bufalo visivel na cena com presenca relevante para a leitura da imagem;
- `cortado`: parte relevante do corpo ficou fora do enquadramento;
- `angulo_extremo`: o angulo dificulta comparar volume corporal ou contorno;
- `baixo_contraste`: o contorno do bufalo se mistura ao fundo por semelhanca de cor, luminosidade ou textura, incluindo casos de baixa iluminacao, coloracao parecida com elementos do fundo, outros bufalos ao fundo visualmente semelhantes ao sujeito principal e patas enlameadas se confundindo com chao lamacento; se esses outros bufalos tambem tiverem presenca relevante na cena, combine com `multi_bufalos`;
- `ocluido`: parte relevante do corpo esta na imagem, mas foi encoberta.

Distincoes importantes:

- `cortado` x `ocluido`: em `cortado`, a parte do corpo ficou fora da imagem; em `ocluido`, ela esta na imagem, mas escondida;
- `ocluido` x `baixo_contraste`: em `ocluido`, existe um elemento entre a camera e o animal; em `baixo_contraste`, o corpo esta visivel, mas se confunde com o fundo.

Convencao de uso:

- marque `ok` apenas quando nao houver nenhuma observacao relevante;
- se houver problema, marque somente as tags aplicaveis;
- nao crie variacoes fora desse conjunto sem atualizar a documentacao.

## Decisoes Tecnicas

### Binarizacao do ground truth com threshold global

Decisao:

- usar `GroundTruthLimiarGlobal` apenas para as mascaras de ground truth;
- converter a imagem para grayscale, aplicar threshold global fixo e salvar a saida em `.png`;
- nao aplicar blur gaussiano nem morfologia nessa etapa;
- manter `GaussianaOpening` nas segmentacoes previstas dos modelos.

Motivo:

- as mascaras manuais de ground truth ja chegam visualmente quase binarias;
- os artefatos residuais do JPEG aparecem sobretudo nas bordas e sob ampliacao;
- um threshold global simples faz a quantizacao final sem alterar o contorno mais do que o necessario.

### Formato das mascaras

Decisao:

- manter `PNG` como formato padrao para mascaras intermediarias e finais.

Motivo:

- `PNG` nao tem perda;
- preserva os contornos;
- evita alteracao de pixels por compressao com perdas.

Relacao entre formatos:

- imagens originais de entrada continuam em `.jpg`;
- mascaras de saida sao salvas em `.png`;
- essa diferenca e intencional: fotografia de entrada pode ficar em `.jpg`, mascara deve preservar valores exatos.

### Escolha da metrica AUPRC

Decisao:

- adotar `AUPRC` como uma das metricas de avaliacao para o estagio de binarizacao e para a analise de mascaras com score continuo.

Contexto:

- no projeto, os pixels de bufalo ocupam uma parcela pequena da imagem;
- o fundo ocupa a maior parte do espaco;
- esse desbalanceamento pode tornar metricas menos sensiveis a classe positiva rara excessivamente otimistas;
- na binarizacao, tambem ha interesse em avaliar a qualidade do score da mascara antes de fixar um threshold.

Motivo:

- `AUPRC` e especialmente util quando a classe positiva e rara;
- ela mede quao bem o modelo separa bufalo vs fundo usando o score continuo da mascara;
- isso evita depender de um threshold unico e arbitrario logo no inicio da avaliacao.

Consequencias:

- a avaliacao fica mais alinhada ao desbalanceamento real entre bufalo e fundo;
- o score continuo da mascara passa a ser aproveitado diretamente;
- comparacoes entre estrategias de binarizacao podem considerar a qualidade da ordenacao dos pixels, e nao apenas a saida final apos threshold.

### Escolha da metrica Soft Dice

Decisao:

- adotar `Soft Dice` como metrica de segmentacao bruta do projeto;
- manter a leitura complementar entre ranking de scores, cobertura espacial e
  erro probabilistico.

Contexto:

- as mascaras brutas carregam score continuo por pixel;
- o projeto precisa diferenciar incerteza localizada na borda de vazamento de
  confianca para o fundo;
- tambem ha interesse em avaliar cobertura do animal antes de escolher um
  threshold fixo.

Motivo:

- `Soft Dice` mede se a massa de score esta concentrada dentro do ground truth;
- ele penaliza score alto no fundo;
- ele penaliza cobertura incompleta do bufalo;
- ele complementa a `AUPRC`, que mede melhor ranking de scores do que cobertura
  espacial;
- ele cria uma ponte util com a etapa binaria porque mascaras com bom `Soft
  Dice` tendem a ser mais faceis de binarizar.

Consequencias:

- a entrada deve usar `score_mask` normalizado em `[0, 1]`;
- o `ground_truth_mask` continua binario;
- a leitura recomendada dos resultados e por imagem, com agregacao por mediana
  e IQR, ou media e desvio padrao;
- a metrica nao substitui analises de contorno na etapa binarizada;
- comparacoes entre modelos devem seguir o mesmo protocolo de normalizacao.

### Escolha da metrica Brier Score

Decisao:

- adotar `Brier Score` como metrica de segmentacao bruta em paralelo a
  `AUPRC` e `Soft Dice`.

Contexto:

- `AUPRC` mede separacao entre pixels positivos e negativos;
- `Soft Dice` mede cobertura e concentracao do score;
- ainda faltava uma leitura de erro probabilistico da intensidade numerica da
  confianca por pixel.

Motivo:

- `Brier Score` mede erro quadratico medio entre score previsto e ground truth
  binario;
- ele penaliza score alto no fundo e score baixo dentro do bufalo;
- ele complementa as outras metricas de segmentacao bruta sem substitui-las.

Consequencias:

- a avaliacao de segmentacao bruta passa a usar `AUPRC`, `Soft Dice` e
  `Brier Score`;
- `score_mask` deve seguir normalizado em `[0, 1]`;
- `SegmentacaoBruta` persiste `brier_score`;
- o coletor analitico expõe a coluna `brier_score`.

### Mascaras do `rembg`

Implementacao relacionada:

- `src/controllers/segmentacao_controller.py`
- `src/services/segmentacao_service.py`
- `config.toml`

Comportamento atual:

```python
remove(
    input_rembg,
    only_mask=True,
    session=rembg_session,
)
```

Isso faz a etapa de segmentacao gerar uma mascara em escala de cinza, salva em `generated/segmentacoes_brutas/execucao_N/<modelo>/`, com formato `PNG`.

Decisao:

- manter `only_mask=True` na geracao pelo `rembg`;
- fazer a conversao para mascara binaria apenas na etapa posterior de binarizacao.

Motivo:

- separa inferencia e pos-processamento;
- preserva a saida original do modelo antes da binarizacao;
- permite reavaliar a binarizacao sem rerodar a segmentacao.

### Modelo `u2net_cloth_seg`

Implementacao relacionada:

- `config.toml`

Decisao:

- nao incluir `u2net_cloth_seg` entre os modelos ativos;
- manter o identificador apenas comentado, com referencia para a documentacao.

Motivo:

- esse modelo foi treinado para segmentacao de roupas em pessoas;
- em imagens de bufalos, ele tende a gerar mascaras muito conservadoras ou quase totalmente pretas;
- isso compromete contorno, area segmentada e comparabilidade com os demais modelos.

## Suite De Testes

A suite automatizada existe para validar comportamento sem depender do dataset completo do projeto.

Principios:

- usar dataset reduzido e controlado;
- desenvolver novas funcionalidades e correcoes usando TDD sempre que pratico;
- separar testes por tipo;
- manter imports do pacote `src` via instalacao do projeto;
- evitar acoplamento desnecessario com caminhos do ambiente real.

Abordagem de desenvolvimento:

- o projeto adota TDD (`Test-Driven Development`) como abordagem preferencial de implementacao;
- o fluxo esperado e escrever primeiro o teste, confirmar a falha inicial, fazer um commit contendo apenas testes e documentacao da etapa TDD, implementar a menor mudanca necessaria e refatorar com a suite verde;
- essa diretriz vale para novas funcionalidades e correcoes de bug quando o comportamento puder ser coberto por teste automatizado.
- depois do commit da etapa vermelha, os testes nao devem ser alterados durante a implementacao, exceto quando houver erro real no contrato ou ajuste de escopo;
- se um teste precisar mudar apos esse commit, a alteracao deve ser intencional, tecnicamente justificavel e facil de identificar no historico.

Estrutura principal:

```text
config.toml
config.test.toml
config.e2e.toml
tests/
  conftest.py
  mock_data/
  mock_generated/
  fixtures/
  unit/
    analysis/
    avaliacao/
    binarizacao/
    io/
    logs/
    metricas/
    models/
    runtime/
    segmentacao/
    visualization/
  integration/
    analysis/
    io/
    pipeline/
  e2e/
```

Convencao de nomes:

- testes unitarios usam prefixo `unit_test_`;
- testes de integracao usam prefixo `integration_test_`;
- testes end-to-end usam prefixo `e2e_test_`.

Convencoes de import:

- evite imports com prefixo `tests.`;
- use imports locais da propria suite quando necessario;
- mantenha imports com prefixo `src.` para o codigo do projeto.

Exemplo preferido:

```python
from src.config import INDICE_PATH, MODELOS_PARA_AVALIACAO
```

Dataset reduzido:

- fica em `tests/mock_data/`;
- replica a estrutura minima para exercitar leitura de planilha, nomes de arquivo e integracoes sem depender de `data/`.

Artefatos versionados:

- ficam em `tests/mock_generated/`;
- guardam saidas intermediarias e finais estaveis para testes de integracao;
- incluem o fixture `tests/mock_generated/bufalos-avaliacao.sqlite3` para cenarios de leitura analitica.

Configuracao da suite:

- a base fica em `config.toml`;
- o override da suite fica em `config.test.toml`;
- `tests/conftest.py` define `BUFALOS_ENV=test` antes dos imports de `src.config`;
- `config.test.toml` sobrescreve apenas paths e o subconjunto de modelos usados na suite.

Configuracao do `e2e`:

- o `e2e` usa um override proprio em `config.e2e.toml`;
- os testes `e2e` carregam esse arquivo via `BUFALOS_CONFIG_PATH`;
- a saida persistente fica em `tests/e2e_generated/`;
- o diretorio e limpo no inicio de cada teste e mantido ao final para inspecao manual;
- a intencao e que o `e2e` represente uma pequena execucao real da pipeline, auditavel tambem fora do `pytest`.

Trecho esperado de configuracao:

```toml
[paths]
data_dir = "tests/mock_data"
generated_dir = "tests/generated"
images_dir = "tests/mock_data/images"
ground_truth_brutos_dir = "tests/mock_data/ground_truth_brutos"
segmentacoes_brutas_dir = "tests/generated/segmentacoes_brutas"
segmentacoes_binarizadas_dir = "tests/generated/segmentacoes_binarizadas"
ground_truth_binarizada_dir = "tests/generated/ground_truth_binarizada"
evaluation_dir = "tests/generated/evaluation"
indice_file = "tests/mock_data/Indice.xlsx"
sqlite_file = "tests/mock_generated/bufalos-testes.sqlite3"

[execution]
num_execucoes = 3

[binarization]
ground_truth_strategy = "GroundTruthLimiarGlobal"
segmentacao_strategies = ["GaussianaOpening"]

[models]
u2netp = "cpu"
```

Observacao:

- o `config.test.toml` aponta para `tests/mock_generated/bufalos-testes.sqlite3`;
- testes que escrevem no banco devem sobrescrever `sqlite_path` para `tmp_path`;
- o fixture versionado da avaliacao fica em `tests/mock_generated/bufalos-avaliacao.sqlite3`.

Fluxo local recomendado:

- `pip install -e .`
- `pytest`
- `pytest -m "not e2e"`
- `pytest tests/e2e/e2e_test_notebooks.py -m e2e`
- `pytest --cov=src --cov-report=term-missing`
- `pytest --cov=src --cov-report=html`

## CI

O workflow de integracao continua valido hoje em `.github/workflows/ci.yml`.

Objetivo do CI:

- verificar rapidamente se o projeto instala corretamente;
- verificar se a suite automatizada principal continua passando.

Configuracao atual:

- gatilhos: `pull_request` e `workflow_dispatch`;
- ambiente: `ubuntu-latest`;
- Python: `3.13`.

Instalacao no CI:

```bash
python -m pip install .[test]
```

Comando executado:

```bash
python -m pytest -q -m "not e2e" --cov=src --cov-report=html
```

Efeitos:

- exclui testes marcados como `e2e`;
- mede coverage do pacote `src`;
- gera relatorio HTML em `htmlcov/`.

Artifact publicado:

- nome: `coverage-html`.

Para inspecionar o coverage:

1. abra a execucao do workflow no GitHub Actions;
2. baixe o artifact `coverage-html`;
3. extraia o arquivo;
4. abra `htmlcov/index.html`.

## GPU

Esta secao e opcional e so vale para execucao com aceleracao em GPU.

Sem GPU, o projeto continua funcionando em CPU, mas a segmentacao tende a ser mais lenta.

Passos documentados para Arch Linux:

1. instalar CUDA 12.5 com `yay -S cuda-12.5`;
2. verificar com `/opt/cuda/bin/nvcc --version`;
3. instalar cuDNN com `yay -S cudnn9.3-cuda12.5`;
4. instalar e registrar um kernel Jupyter com `ipykernel`;
5. ajustar `LD_LIBRARY_PATH` no `kernel.json` para `/opt/cuda/lib64`.

Exemplo de registro de kernel:

```bash
pip install ipykernel
python -m ipykernel install --user --name=projeto-bufalos --display-name="Python 3.12 (projeto-bufalos)"
```

Exemplo de `kernel.json`:

```json
{
  "argv": [
    "/home/SEU_USUARIO/Projects/projeto-bufalos/.venv/bin/python",
    "-m",
    "ipykernel_launcher",
    "-f",
    "{connection_file}"
  ],
  "display_name": "Python 3.12 (projeto-bufalos)",
  "language": "python",
  "env": {
    "LD_LIBRARY_PATH": "/opt/cuda/lib64"
  }
}
```

Verificacao esperada:

- a GPU deve ficar disponivel ao executar a segmentacao no ambiente configurado;
- se houver falha de biblioteca, revise o `LD_LIBRARY_PATH` do kernel do Jupyter.

## Referencia Do `rembg`

O projeto usa `rembg` como biblioteca de remocao de fundo e geracao de mascaras.

Conhecimentos relevantes de referencia:

- `rembg` suporta instalacao base, CPU, GPU NVIDIA/CUDA e ROCm;
- a CLI oferece subcomandos `i`, `p`, `s` e `b`;
- `rembg i -om` gera apenas a mascara;
- na API Python, `remove(input, only_mask=True)` devolve apenas a mascara;
- `new_session(model_name)` permite reaproveitar a sessao para varios arquivos;
- `alpha_matting`, `post_process_mask` e `bgcolor` sao parametros de pos-processamento;
- argumentos como `input_points` e `input_labels` existem para modelos como `sam`.

Exemplo minimo em Python:

```python
from PIL import Image
from rembg import new_session, remove

input_image = Image.open("input.png")
session = new_session("u2netp")
output = remove(input_image, only_mask=True, session=session)
output.save("output.png")
```

Exemplos uteis de CLI:

```bash
rembg i path/to/input.png path/to/output.png
rembg i -m u2netp path/to/input.png path/to/output.png
rembg i -om path/to/input.png path/to/output.png
rembg p path/to/input path/to/output
```

## Convencoes De Codigo

Use Python com indentacao de 4 espacos e imports explicitos.

Convencoes principais:

- prefira modulos pequenos e coesos;
- mantenha notebooks finos, movendo logica reutilizavel para `src/`;
- arquivos e funcoes usam `snake_case`;
- classes usam `PascalCase`;
- em `src/logs/`, modulos de logging devem refletir claramente o dominio atendido, como `segmentacao.py`, `binarizacao.py` e `integridade.py`;
- em `src/binarizacao/estrategias/`, abstracoes base devem usar nomes de dominio claros, como `binarizacao_base.py`.

Quando uma decisao tecnica impactar o pipeline:

- registre-a em `docs/decisoes-tecnicas/`;
- reflita a mesma informacao em `AGENTS.md`;
- quando fizer sentido, referencie no codigo com comentarios como:

```python
# Docs: decisoes-tecnicas/mascaras-do-rembg.md
```

## Commits E Pull Requests

Padrao recente do historico:

- mensagens em portugues;
- verbo de acao curto no inicio, como `Adiciona`, `Atualiza`, `Ajusta`, `Integra`, `Mantem`, `Sincroniza` ou `Refina`;
- mensagens curtas;
- um objetivo claro por commit.

Regra operacional:

- novos commits devem seguir o padrao observado nos ultimos commits da branch principal;
- nao usar prefixes artificiais como `feat:`, `fix:`, `docs:` ou equivalentes.

Exemplos:

- `Adiciona execucoes ao pipeline e ajusta testes`
- `Integra execucoes aos logs do pipeline`
- `Atualiza notebook 03 de avaliacao`

Pull requests devem:

- resumir a mudanca de comportamento;
- listar os modulos afetados;
- mencionar atualizacoes de documentacao;
- incluir evidencia de teste, como `pytest ...`;
- explicar o motivo se notebooks ou artefatos gerados forem alterados.
- ser abertos sempre como draft por padrao;
- usar titulo e corpo em portugues;
- usar um titulo que abranja o conjunto real de mudancas do PR;
- nao usar prefixos como `[codex]` no titulo.

## Mapa Da Documentacao Humana

Leitura recomendada:

1. `docs/guias/guia-do-projeto.md`
2. `docs/guias/documentacao-do-repositorio.md`
3. `docs/avaliacao/sistema-de-avaliacao.md`
4. `docs/metricas/auprc.md`
5. `docs/metricas/soft-dice.md`
6. `docs/metricas/brier-score.md`
7. `docs/decisoes-tecnicas/escolha-da-metrica-auprc.md`
8. `docs/decisoes-tecnicas/escolha-da-metrica-soft-dice.md`
9. `docs/decisoes-tecnicas/escolha-da-metrica-brier-score.md`
10. `docs/avaliacao/tags-de-imagem.md`
11. `docs/guias/testes.md`
12. `docs/guias/ci.md`
13. `docs/decisoes-tecnicas/`
14. `docs/referencia/rembg/`
