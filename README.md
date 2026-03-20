# Projeto Bufalos - Avaliacao de Modelos de Remocao de Fundo

Projeto para avaliar modelos de remocao de fundo em imagens de bufalos utilizando a biblioteca `rembg`.

## Estrutura esperada dos dados

Estrutura minima na pasta `data`:

```text
data/
  ground_truth_raw/ # mascaras de referencia (segmentacao manual)
  images/           # imagens originais de entrada
  Indice.xlsx       # planilha com indice das imagens
```

Saidas geradas pelo projeto:

```text
generated/
  predicted_masks/         # mascaras geradas pelos modelos
  predicted_masks_binary/  # mascaras previstas apos binarizacao
  ground_truth_binary/     # mascaras manuais apos binarizacao
  evaluation/              # caches e artefatos de avaliacao
```

## Configuracao do ambiente

### Requisitos

- Python 3.13 recomendado (o projeto requer Python >= 3.12 e < 3.14)
- Para evitar problemas no uso de `src/tagging/manual_tagger.py`, prefira Python 3.13
- `tkinter` disponivel no Python para rodar os anotadores manuais
- GPU NVIDIA com CUDA e opcional; o projeto tambem pode rodar em CPU

### Instalacao

1. Crie o ambiente virtual:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

2. Instale o projeto:

```bash
pip install -e .
```

Essa instalacao ja cobre o runtime principal do projeto, incluindo segmentacao com `rembg`, suporte a providers de GPU e visualizacao.

Essa instalacao tambem cobre o ambiente de desenvolvimento e a suite de testes.

### Instalacao com mise

Se voce usa `mise`, este e o caminho recomendado para criar o `.venv` com Python 3.13:

```bash
mise exec python@3.13 -- python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Como alternativa, voce pode fixar o Python 3.13 no projeto antes de criar o venv:

```bash
mise use python@3.13
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Como rodar o projeto

Todos os comandos abaixo assumem que voce esta na raiz do repositorio e com o ambiente virtual ativado:

```bash
source .venv/bin/activate
```

### Rodar o anotador manual de tags

O script `src/tagging/manual_tagger.py` abre uma interface grafica para revisar as imagens pendentes e preencher a coluna `tags` de `data/Indice.xlsx`.

Comando recomendado:

```bash
python -m src.tagging.manual_tagger
```

Comando equivalente:

```bash
python src/tagging/manual_tagger.py
```

Pre-requisitos:

- `data/Indice.xlsx` precisa existir
- a planilha precisa ter a coluna `nome do arquivo`
- as imagens precisam estar em `data/images/`
- o ambiente precisa ter suporte grafico e `tkinter`

Comportamento do fluxo:

- o app carrega apenas linhas ainda sem valor na coluna `tags`
- `1` a `5` alternam as tags disponiveis
- `Enter` salva a imagem atual e avanca
- `Enter` sem nenhuma tag marcada grava `ok`
- ao fechar a janela, o app salva a selecao atual se houver tags marcadas

Se o app abortar no Linux/Wayland com erro `xcb`, o problema pode estar no runtime `Python + Tk` usado para criar o `.venv`, e nao no codigo do projeto. Se isso acontecer, recrie o ambiente com outra instalacao de Python compativel e teste primeiro um exemplo minimo de `tkinter`.

### Rodar o anotador por foco

O script `src/tagging/focused_tagger.py` permite revisar uma tag por vez, mantendo as tags ja existentes da imagem.

Comando recomendado:

```bash
python -m src.tagging.focused_tagger
```

Comando equivalente:

```bash
python src/tagging/focused_tagger.py
```

Comportamento do fluxo:

- na tela inicial, use `1` a `5` para escolher a tag-foco e `Enter` para confirmar
- o app revisa apenas imagens que ainda nao possuem a tag-foco selecionada
- durante a revisao, a tecla `1` alterna a marcacao da tag-foco para a imagem atual
- `Enter` salva e avanca para a proxima imagem
- se a celula ainda estiver vazia e nenhuma marcacao for feita, o fluxo grava `ok`
- se a imagem ja tiver outras tags, elas sao preservadas

As tags de curadoria estao definidas em `docs/image-tags.md`.

### Rodar os notebooks principais

O fluxo de execucao do projeto esta organizado em tres notebooks:

- `notebooks/01_geracao_mascaras_e_segmentacao.ipynb`: gera as mascaras previstas pelos modelos
- `notebooks/02_binarizacao_mascaras.ipynb`: binariza mascaras previstas e mascaras de referencia
- `notebooks/03_avaliacao_das_segmentacoes.ipynb`: calcula metricas e compara os modelos

Para abrir o ambiente de notebooks:

```bash
jupyter notebook
```

Depois execute os notebooks na ordem acima.

## Configuracao de GPU (NVIDIA/CUDA)

Esta secao e opcional. Ela so e necessaria se voce quiser executar os modelos com aceleracao em GPU.

Sem GPU, o projeto continua funcionando em CPU, mas a segmentacao tende a ser mais lenta.

### Passo 1: Instalar CUDA 12.5

O `onnxruntime-gpu` requer CUDA 12.x. No Arch Linux, instale via AUR:

```bash
yay -S cuda-12.5
```

Verifique a instalacao:

```bash
/opt/cuda/bin/nvcc --version
```

### Passo 2: Instalar cuDNN

Instale o cuDNN compativel com CUDA 12.5:

```bash
yay -S cudnn9.3-cuda12.5
```

### Passo 3: Garantir bibliotecas do sistema para GPU

As dependencias Python de GPU ja sao instaladas com `pip install -e .`. Nesta etapa, falta apenas garantir que CUDA e cuDNN estejam disponiveis no sistema.

### Passo 4: Configurar kernel do Jupyter (opcional)

Para usar GPU no Jupyter, crie um kernel com `LD_LIBRARY_PATH` configurado:

```bash
pip install ipykernel
python -m ipykernel install --user --name=projeto-bufalos --display-name="Python 3.12 (projeto-bufalos)"
```

Edite `~/.local/share/jupyter/kernels/projeto-bufalos/kernel.json` para incluir:

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

### Verificar se a GPU esta funcionando

No Python ou Jupyter:

```python
import onnxruntime as ort
print(ort.get_available_providers())
# Deve incluir 'CUDAExecutionProvider'
```

Ou via CLI:

```bash
rembg p data/images generated/test -m u2net
# Deve processar usando GPU
```

## Modelos disponiveis para avaliacao

Os modelos configurados ficam em `src/config.py`, no dicionario `MODELOS_PARA_AVALIACAO`.

Observacao:

- o projeto pode ser executado sem GPU
- os providers configurados em `src/config.py` definem quais modelos tentam usar `gpu` e quais usam `cpu`
- modelos `birefnet-*` consomem muita VRAM
- em GPUs com 4 GB, como a GTX 1650, podem ocorrer erros de memoria com imagens grandes
- alguns modelos estao configurados para `cpu` por esse motivo

## Estrutura do projeto

```text
projeto-bufalos/
  data/                 # Dados de entrada
  docs/                 # Documentacao adicional
  generated/            # Saidas geradas
  notebooks/
    01_geracao_mascaras_e_segmentacao.ipynb
    02_binarizacao_mascaras.ipynb
    03_avaliacao_das_segmentacoes.ipynb
  src/
    config.py
    io/
    metrics/
    models/
    runtime/
    segmentacao/
    tagging/            # Anotacao manual das tags de curadoria
    visualization/
  pyproject.toml
```

## Documentacao adicional

- `docs/eval-types.md`: criterios de avaliacao dos modelos
- `docs/evaluation-system.md`: visao geral do sistema de avaliacao
- `docs/image-tags.md`: taxonomia das tags de curadoria
- `docs/CHOICES.md`: decisoes registradas do projeto
- `docs/testing.md`: convencoes e infraestrutura da suite de testes

## Suite de Testes

A suite automatizada fica em `tests/`.

### Estrutura

```text
tests/
  conftest.py
  config.toml
  mock_config.py
  mock_data/
  fixtures/
  unit/
    io/
  integration/
    io/
```

### Executar os testes

Na raiz do projeto:

```bash
pytest
```

Os imports `from src...` dependem da instalacao editavel do projeto, nao de ajustes manuais de `sys.path`.

### Convencoes

- Arquivos de teste devem seguir o padrao `test_*.py`
- Testes unitarios devem ficar em `tests/unit/` e espelhar `src/`
- Testes de integracao devem ficar em `tests/integration/`
