# Projeto Bufalos - Avaliacao de Modelos de Remocao de Fundo

Projeto para avaliar modelos de remocao de fundo em imagens de bufalos utilizando a biblioteca `rembg`.

## Setup inicial

Estrutura esperada na pasta `data`:

```
data/
  ground_truth/     # mascaras de referencia (segmentacao manual)
  images/           # imagens originais de entrada
  Indice.xlsx       # planilha com indice das imagens
```

## Configuracao do Ambiente

### Requisitos

- Python 3.12 (rembg requer Python < 3.14)
- NVIDIA GPU com suporte CUDA (testado com GTX 1650)

### Instalacao

1. Crie o ambiente virtual com Python 3.12:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

2. Instale o projeto:

```bash
pip install -e .
```

Para desenvolvimento e execucao da suite de testes, instale tambem o extra de testes:

```bash
pip install -e .[test]
```

Para executar o sistema com o conjunto completo de dependencias de runtime:

```bash
pip install -e .[runtime]
```

### Instalacao com mise

Se voce usa `mise`, pode criar o ambiente com Python 3.12 explicitamente assim:

```bash
mise exec python@3.12 -- python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
pip install -e .[runtime]
```

Esse fluxo cria um ambiente de desenvolvimento completo:

- `.[test]` instala as dependencias da suite de testes
- `.[runtime]` instala as dependencias completas de execucao do sistema

Como alternativa, voce pode fixar o Python 3.12 no projeto com `mise` antes de criar o venv:

```bash
mise use python@3.12
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
pip install -e .[runtime]
```

## Configuracao de GPU (NVIDIA/CUDA)

Para utilizar a GPU com o rembg, e necessario configurar CUDA e cuDNN corretamente.

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

### Passo 4: Configurar Jupyter Kernel (opcional)

Para usar GPU no Jupyter, crie um kernel com o `LD_LIBRARY_PATH` configurado:

```bash
# Instale o ipykernel no ambiente virtual
pip install ipykernel

# Crie o kernel
python -m ipykernel install --user --name=projeto-bufalos --display-name="Python 3.12 (projeto-bufalos)"
```

Edite o arquivo do kernel para adicionar o `LD_LIBRARY_PATH`:

```bash
# Localizacao: ~/.local/share/jupyter/kernels/projeto-bufalos/kernel.json
```

Conteudo do `kernel.json`:

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

### Verificar se GPU esta funcionando

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

## Modelos Disponiveis para Avaliacao

```python
MODELOS_PARA_AVALIACAO = [
    'u2net',
    'u2netp',
    'u2net_human_seg',
    'silueta',
    'isnet-general-use',
    'isnet-anime',
    'sam',
    'birefnet-general',
    'birefnet-general-lite',
    'birefnet-portrait',
    'birefnet-dis',
    'birefnet-hrsod',
    'birefnet-cod',
    'birefnet-massive'
]
```

**Nota:** Modelos `birefnet-*` consomem muita VRAM. Em GPUs com 4GB (como GTX 1650), podem causar erros de memoria com imagens grandes.

## Estrutura do Projeto

```
projeto-bufalos/
  data/                 # Dados de entrada
  docs/                 # Documentacao adicional
  generated/            # Saidas geradas (mascaras segmentadas)
  notebooks/            # Notebooks do projeto
    script.ipynb        # Notebook principal de segmentacao
    avaliar.ipynb       # Notebook de avaliacao
  src/                  # Codigo Python do projeto
    config.py
    io/
    logs/
    models/
    runtime/
  rembg/                # Repositorio do rembg clonado (referencia)
  pyproject.toml        # Configuracao do projeto e extras de dependencia
```

## Documentacao Adicional

- `docs/eval-types.md`: Criterios de avaliacao dos modelos
- `docs/rembg/rembg-readme.md`: README original do rembg
- `docs/rembg/rembg-usage.md`: Exemplos de uso do rembg em Python

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
