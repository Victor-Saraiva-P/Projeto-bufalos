# Projeto Bufalos - Avaliacao de Modelos de Remocao de Fundo

Projeto para avaliar modelos de remocao de fundo em imagens de bufalos utilizando a biblioteca `rembg`.

## Estrutura esperada dos dados

Estrutura minima na pasta `data`:

```text
data/
  ground_truth/     # mascaras de referencia (segmentacao manual)
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

- Python 3.12 (o `rembg` requer Python < 3.14)
- `tkinter` disponivel no Python para rodar o anotador manual
- (opcional) GPU NVIDIA com CUDA; o projeto tambem pode rodar em CPU

### Instalacao

1. Crie o ambiente virtual:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

Observacao:

- a instalacao acima permite rodar o projeto em CPU
- para acelerar a execucao com GPU, siga a secao de configuracao de CUDA abaixo

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

Se aparecer erro como `ModuleNotFoundError`, confirme antes que o ambiente virtual do projeto esta ativado:

```bash
source .venv/bin/activate
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

### Passo 3: Instalar rembg com suporte a GPU

```bash
pip install "rembg[gpu,cli]"
```

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
    logs/
    metrics/
    models/
    runtime/
    tagging/            # Anotacao manual das tags de curadoria
    visualization/
  requirements.txt
```

## Documentacao adicional

- `docs/eval-types.md`: criterios de avaliacao dos modelos
- `docs/evaluation-system.md`: visao geral do sistema de avaliacao
- `docs/image-tags.md`: taxonomia das tags de curadoria
- `docs/CHOICES.md`: decisoes registradas do projeto
- `docs/rembg/rembg-readme.md`: README original do rembg
- `docs/rembg/rembg-usage.md`: exemplos de uso do rembg em Python
