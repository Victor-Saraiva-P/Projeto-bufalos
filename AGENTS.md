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

## Visao Geral

Este repositorio contem o projeto de avaliacao de modelos de remocao de fundo em imagens de bufalos.

O fluxo principal do projeto e:

1. gerar mascaras previstas com modelos de segmentacao;
2. binarizar mascaras previstas e mascaras de referencia;
3. calcular metricas por imagem e por modelo;
4. agregar os resultados;
5. produzir visualizacoes e ranking.

Os notebooks principais executam esse fluxo nesta ordem:

1. `notebooks/01_geracao_mascaras_e_segmentacao.ipynb`
2. `notebooks/02_binarizacao_mascaras.ipynb`
3. `notebooks/03_avaliacao_das_segmentacoes.ipynb`

## Estrutura Do Repositorio

Pastas principais:

- `src/`: codigo principal do projeto;
- `src/segmentacao/`: geracao de máscaras previstas, integracao com `rembg`, verificacoes de integridade e logging;
- `src/binarizacao/`: estrategias, pipeline e logs da binarizacao;
- `src/metricas/`: contratos compartilhados de metricas;
- `src/avaliacao/metricas/`: metricas concretas de avaliacao de segmentacao;
- `src/analysis/` e `src/visualization/`: agregacao, ranking e apresentacao;
- `src/tagging/`: anotadores manuais de tags de curadoria;
- `tests/`: suite automatizada;
- `notebooks/`: fluxo exploratorio e analitico do projeto;
- `docs/`: documentacao organizada por tema;
- `data/`: dados de entrada esperados pelo pipeline;
- `generated/`: artefatos gerados durante segmentacao, binarizacao e avaliacao.

Estrutura minima esperada em `data/`:

```text
data/
  ground_truth_raw/ # mascaras de referencia
  images/           # imagens originais de entrada
  Indice.xlsx       # planilha usada no tagging e no bootstrap inicial do SQLite
```

Saidas esperadas em `generated/`:

```text
generated/
  predicted_masks/         # mascaras geradas pelos modelos
  predicted_masks_binary/  # mascaras previstas apos binarizacao
  ground_truth_binary/     # mascaras manuais apos binarizacao
  evaluation/              # artefatos de avaliacao
  bufalos.sqlite3          # fonte de verdade do pipeline
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

Na etapa de binarizacao e analise de mascaras com score continuo, o projeto tambem passa a considerar `AUPRC` (`Area Under the Precision-Recall Curve`).

Arquivos relevantes:

- `src/metricas/metrica.py`: contrato base das metricas reutilizaveis na pipeline;
- `src/avaliacao/metricas/`: metricas concretas usadas na avaliacao das mascaras;
- `src/analysis/collector.py`: coleta as metricas para todas as imagens e modelos;
- `src/analysis/ranker.py`: transforma as metricas agregadas em ranking;
- `src/visualization/metric_plots.py`: gera graficos para inspecao das metricas;
- `src/visualization/image_grid.py`: monta grades visuais para comparar casos;
- `src/config.py`: define caminhos e pesos usados no ranking.

Saida gerada:

- `generated/bufalos.sqlite3`: banco SQLite usado como fonte de verdade da avaliacao.

Exemplo minimo para coletar metricas:

```python
from src.analysis import MetricsCollector

collector = MetricsCollector(force_recalculate=False)
df_metrics = collector.collect_all_metrics()
```

Exemplo minimo para gerar ranking:

```python
from src.analysis import ModelRanker
from src.config import RANKING_WEIGHTS

ranker = ModelRanker(df_metrics, weights=RANKING_WEIGHTS)
df_ranking = ranker.calculate_ranking()
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

- o calculo fica em `src/binarizacao/metricas/auprc.py`;
- a interface recebe `score_mask` continuo e `ground_truth_mask` binario;
- a metrica foi adicionada para o estagio de binarizacao, e nao como substituta direta das metricas agregadas finais do ranking de segmentacao.

Formulas:

```text
IoU = intersecao / uniao
|area_modelo - area_gt| / area_gt
|perimetro_modelo - perimetro_gt| / perimetro_gt
```

Ranking ponderado esperado em `src/config.py`:

```python
RANKING_WEIGHTS = {
    "iou": 0.70,
    "area_diff_rel": 0.15,
    "perimetro_diff_rel": 0.15,
}
```

Regra importante:

- a soma dos pesos deve ser `1.0`.

Persistencia:

- por padrao, a coleta usa o SQLite do projeto como fonte de verdade;
- para forcar recalcucao, use `MetricsCollector(force_recalculate=True)`;
- isso sobrescreve os registros de avaliacao no banco.

Ao analisar resultados, normalmente vale olhar:

- distribuicao das metricas por modelo;
- top `N` e bottom `N` por imagem;
- consistencia entre score agregado e inspecao visual.

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
- `multi_bufalos`: mais de um bufalo visivel na cena;
- `cortado`: parte relevante do corpo ficou fora do enquadramento;
- `angulo_extremo`: o angulo dificulta comparar volume corporal ou contorno;
- `baixo_contraste`: o contorno do bufalo se mistura ao fundo;
- `ocluido`: parte relevante do corpo esta na imagem, mas foi encoberta.

Distincoes importantes:

- `cortado` x `ocluido`: em `cortado`, a parte do corpo ficou fora da imagem; em `ocluido`, ela esta na imagem, mas escondida;
- `ocluido` x `baixo_contraste`: em `ocluido`, existe um elemento entre a camera e o animal; em `baixo_contraste`, o corpo esta visivel, mas se confunde com o fundo.

Convencao de uso:

- marque `ok` apenas quando nao houver nenhuma observacao relevante;
- se houver problema, marque somente as tags aplicaveis;
- nao crie variacoes fora desse conjunto sem atualizar a documentacao.

## Decisoes Tecnicas

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

### Mascaras do `rembg`

Implementacao relacionada:

- `src/segmentacao/geracao_mascaras.py`
- `src/config.toml`

Comportamento atual:

```python
remove(
    input_rembg,
    only_mask=True,
    session=rembg_session,
)
```

Isso faz a etapa de segmentacao gerar uma mascara em escala de cinza, salva em `generated/predicted_masks/<modelo>/`, com formato `PNG`.

Decisao:

- manter `only_mask=True` na geracao pelo `rembg`;
- fazer a conversao para mascara binaria apenas na etapa posterior de binarizacao.

Motivo:

- separa inferencia e pos-processamento;
- preserva a saida original do modelo antes da binarizacao;
- permite reavaliar a binarizacao sem rerodar a segmentacao.

### Modelo `u2net_cloth_seg`

Implementacao relacionada:

- `src/config.toml`

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
- o fluxo esperado e escrever primeiro o teste, confirmar a falha inicial, implementar a menor mudanca necessaria e refatorar com a suite verde;
- essa diretriz vale para novas funcionalidades e correcoes de bug quando o comportamento puder ser coberto por teste automatizado.

Estrutura principal:

```text
tests/
  config.toml
  conftest.py
  mock_config.py
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

Exemplo correto:

```python
from mock_config import MockDataConfig
```

Exemplo a evitar:

```python
from tests.mock_config import MockDataConfig
```

Dataset reduzido:

- fica em `tests/mock_data/`;
- replica a estrutura minima para exercitar leitura de planilha, nomes de arquivo e integracoes sem depender de `data/`.

Artefatos versionados:

- ficam em `tests/mock_generated/`;
- guardam saidas intermediarias e finais estaveis para testes de integracao.

Configuracao da suite:

- fica em `tests/config.toml`;
- `tests/mock_config.py` le o TOML e expoe caminhos resolvidos.

Caminhos esperados:

- `mock_data_dir`
- `indice_path`
- `images_dir`
- `ground_truth_raw_dir`

Trecho esperado de configuracao:

```toml
[paths]
mock_data_dir = "mock_data"
indice_file = "Indice.xlsx"
images_dir = "images"
ground_truth_raw_dir = "ground_truth_raw"
lock_file = ".~lock.Indice.xlsx#"
```

Fluxo local recomendado:

- `pip install -e .`
- `pytest`
- `pytest -m "not e2e"`
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
- em `src/segmentacao/logging/` e `src/binarizacao/logging/`, modulos de logging devem comecar com `logs_`;
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

- mensagens curtas no imperativo;
- um objetivo claro por commit.

Exemplos:

- `Refatora pipeline de binarizacao e logging`
- `Remove modulo legado de logs de segmentacao`

Pull requests devem:

- resumir a mudanca de comportamento;
- listar os modulos afetados;
- mencionar atualizacoes de documentacao;
- incluir evidencia de teste, como `pytest ...`;
- explicar o motivo se notebooks ou artefatos gerados forem alterados.

## Mapa Da Documentacao Humana

Leitura recomendada:

1. `docs/guias/guia-do-projeto.md`
2. `docs/guias/documentacao-do-repositorio.md`
3. `docs/avaliacao/sistema-de-avaliacao.md`
4. `docs/avaliacao/tags-de-imagem.md`
5. `docs/guias/testes.md`
6. `docs/guias/ci.md`
7. `docs/decisoes-tecnicas/`
8. `docs/metricas/`
9. `docs/referencia/rembg/`
