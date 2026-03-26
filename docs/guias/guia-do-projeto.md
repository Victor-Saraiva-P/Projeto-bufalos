# Guia do Projeto

Este documento concentra as instrucoes operacionais do projeto: ambiente, execucao, notebooks, GPU e convencoes gerais.

## Estrutura esperada dos dados

Estrutura minima na pasta `data`:

```text
data/
  ground_truth_raw/ # mascaras de referencia (segmentacao manual)
  images/           # imagens originais de entrada
  Indice.xlsx       # planilha usada no tagging e no bootstrap inicial do SQLite
```

Saidas geradas pelo projeto:

```text
generated/
  predicted_masks/         # mascaras geradas pelos modelos
  predicted_masks_binary/  # mascaras previstas apos binarizacao
  ground_truth_binary/     # mascaras manuais apos binarizacao
  evaluation/              # artefatos de avaliacao
  bufalos.sqlite3          # fonte de verdade do pipeline
```

Organizacao do codigo em `src/`:

- `src/segmentacao/`: gera mascaras previstas e faz verificacoes de integridade;
- `src/binarizacao/`: binariza mascaras previstas e mascaras de referencia;
- `src/metricas/`: contratos compartilhados de metricas;
- `src/avaliacao/metricas/`: metricas concretas de avaliacao de segmentacao;
- `src/analysis/` e `src/visualization/`: agregam, ranqueiam e apresentam os resultados;
- `src/tagging/`: concentra os anotadores manuais de curadoria.

## Configuracao do ambiente

### Requisitos

- Python 3.13 recomendado;
- o projeto requer Python `>= 3.12` e `< 3.14`;
- `tkinter` disponivel para rodar os anotadores manuais;
- GPU NVIDIA com CUDA e opcional.

Para evitar problemas no uso de `src/tagging/manual_tagger.py`, prefira Python 3.13.

### Instalacao

Crie o ambiente virtual:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

Instale o projeto:

```bash
pip install -e .
```

Essa instalacao cobre o runtime principal, o ambiente de desenvolvimento e a suite de testes.

### Instalacao com `mise`

Caminho recomendado:

```bash
mise exec python@3.13 -- python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Alternativa:

```bash
mise use python@3.13
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Como rodar o projeto

Todos os comandos abaixo assumem que voce esta na raiz do repositorio e com o ambiente ativado:

```bash
source .venv/bin/activate
```

## Abordagem de desenvolvimento

O projeto adota TDD (`Test-Driven Development`) como abordagem preferencial de implementacao.

Sempre que o comportamento for coberto por teste automatizado, a expectativa e:

1. escrever primeiro o teste que descreve o comportamento desejado;
2. observar a falha inicial do teste;
3. implementar a menor mudanca necessaria para fazer o teste passar;
4. refatorar com a suite em estado verde.

### Anotador manual de tags

O script `src/tagging/manual_tagger.py` abre uma interface grafica para revisar as imagens pendentes e preencher a coluna `tags` de `data/Indice.xlsx`.

Fora o tagging, o pipeline usa o SQLite em `generated/` como fonte de verdade. O notebook 01 inicializa esse banco a partir do Excel.

Comando recomendado:

```bash
python -m src.tagging.manual_tagger
```

Comando equivalente:

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

- na tela inicial, use `1` a `5` para escolher a tag-foco e `Enter` para confirmar;
- o app revisa apenas imagens que ainda nao possuem a tag-foco selecionada;
- durante a revisao, a tecla `1` alterna a marcacao da tag-foco para a imagem atual;
- `Enter` salva e avanca para a proxima imagem;
- se a celula ainda estiver vazia e nenhuma marcacao for feita, o fluxo grava `ok`;
- se a imagem ja tiver outras tags, elas sao preservadas.

As tags de curadoria estao definidas em `docs/avaliacao/tags-de-imagem.md`.

### Notebooks principais

O fluxo de execucao do projeto esta organizado em tres notebooks:

- `notebooks/01_geracao_mascaras_e_segmentacao.ipynb`: gera as mascaras previstas pelos modelos;
- `notebooks/02_binarizacao_mascaras.ipynb`: binariza mascaras previstas e mascaras de referencia;
- `notebooks/03_avaliacao_das_segmentacoes.ipynb`: calcula metricas e compara os modelos.

Para abrir o ambiente de notebooks:

```bash
jupyter notebook
```

Execute os notebooks na ordem acima.

## Configuracao de GPU

Esta secao e opcional. Ela so e necessaria se voce quiser executar os modelos com aceleracao em GPU.

Sem GPU, o projeto continua funcionando em CPU, mas a segmentacao tende a ser mais lenta.

### Passo 1: instalar CUDA 12.5

O `onnxruntime-gpu` requer CUDA 12.x. No Arch Linux:

```bash
yay -S cuda-12.5
```

Verifique:

```bash
/opt/cuda/bin/nvcc --version
```

### Passo 2: instalar cuDNN

```bash
yay -S cudnn9.3-cuda12.5
```

### Passo 3: garantir bibliotecas do sistema

As dependencias Python de GPU ja sao instaladas com `pip install -e .`. Nesta etapa, falta apenas garantir que CUDA e cuDNN estejam disponiveis no sistema.

### Passo 4: configurar kernel do Jupyter

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

Depois de configurar o kernel, execute o notebook de segmentacao usando esse ambiente.

Sinais esperados:

- a inferencia deve ocorrer sem erro de biblioteca ausente;
- o backend de GPU deve conseguir carregar `onnxruntime-gpu`;
- se houver falha de carregamento, revise o `LD_LIBRARY_PATH` e as versoes de CUDA/cuDNN.

## Convencao documental

As regras de sincronizacao entre `README.md`, `docs/` e `AGENTS.md` estao definidas em `docs/guias/documentacao-do-repositorio.md`.
