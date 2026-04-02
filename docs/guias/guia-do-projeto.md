# Guia do Projeto

Este documento concentra as instrucoes operacionais do projeto: ambiente, execucao, notebooks, GPU e convencoes gerais.

## Estrutura esperada dos dados

Estrutura minima na pasta `data`:

```text
data/
  ground_truth_brutos/ # mascaras de referencia (segmentacao manual)
  images/           # imagens originais de entrada
  Indice.xlsx       # planilha usada no tagging e no bootstrap inicial do SQLite
```

Saidas geradas pelo projeto:

```text
generated/
  segmentacoes_brutas/
    execucao_1/               # mascaras brutas geradas pelos modelos em cada execucao
  segmentacoes_binarizadas/
    execucao_1/               # mascaras apos binarizacao, agrupadas por estrategia e execucao
  ground_truth_binarizada/ # mascaras manuais apos binarizacao
  evaluation/              # artefatos de avaliacao
  bufalos.sqlite3          # fonte de verdade do pipeline
```

Organizacao do codigo em `src/`:

- `src/segmentacao/`: gera mascaras previstas e faz verificacoes de integridade;
- `src/binarizacao/`: binariza mascaras previstas e mascaras de referencia;
- `src/models/`: entidades persistidas do dominio e do banco SQLite;
- `src/repositories/`: persistencia CRUD baseada nas entidades de `src/models/`;
- `src/sqlite/`: infraestrutura de sessao, conexao e `Base` declarativa do SQLite;
- `src/controllers/` e `src/services/`: orquestracao dos fluxos e casos de uso do projeto;
- `src/logs/`: logging compartilhado entre segmentacao, binarizacao e verificacoes de integridade;
- `src/metricas/`: contratos compartilhados de metricas;
- `src/metricas/segmentacao_bruta/`: metricas sobre mascaras brutas com score continuo;
- `src/metricas/segmentacao_binarizada/`: metricas concretas da segmentacao binarizada;
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

O numero de repeticoes do pipeline fica em `config.toml`, na chave `[execution].num_execucoes`.

## Abordagem de desenvolvimento

O projeto adota TDD (`Test-Driven Development`) como abordagem preferencial de implementacao.

Sempre que o comportamento for coberto por teste automatizado, a expectativa e:

1. escrever primeiro o teste que descreve o comportamento desejado;
2. observar a falha inicial do teste;
3. fazer um commit contendo apenas testes e documentacao da etapa TDD;
4. implementar a menor mudanca necessaria para fazer o teste passar;
5. refatorar com a suite em estado verde.

Objetivo dessa regra:

- preservar um ponto claro no historico com o contrato original dos testes;
- permitir revisar depois se a implementacao respeitou os testes planejados;
- facilitar a identificacao de alteracoes posteriores nos testes e a avaliacao se elas realmente fizeram sentido.

Se, durante a implementacao, um teste precisar ser alterado apos esse commit, a mudanca deve ser rara, tecnicamente justificavel e facilmente identificavel no historico.

## Commits e pull requests

Convencoes esperadas:

- commits devem manter mensagens curtas e com um objetivo claro;
- pull requests devem ser abertos sempre como draft por padrao;
- titulo e corpo do pull request devem estar em portugues;
- o titulo do pull request deve abranger o conjunto real de mudancas introduzidas;
- o titulo do pull request nao deve usar prefixos como `[codex]`;
- o corpo do pull request deve resumir a mudanca, listar impacto relevante e registrar a validacao executada.

## Regra para mudancas no SQLite

O banco `generated/bufalos.sqlite3` e tratado como artefato descartavel do pipeline.

Por isso:

- nao e necessario criar arquivos de migracao;
- nao e necessario manter logica de migracao incremental de schema;
- quando o schema mudar, a pratica esperada e deletar o arquivo `.sqlite` e subir tudo de novo pelo fluxo normal do projeto.

Essa regra vale tanto para o banco principal em `generated/` quanto para bancos SQLite recriados em testes locais.

### Anotador manual de tags

O script `src/tagging/manual_tagger.py` abre uma interface grafica para revisar as imagens pendentes e preencher a coluna `tags` de `data/Indice.xlsx`.

Fora o tagging, o pipeline usa o SQLite em `generated/` para guardar o indice e os resultados completos de avaliacao. O notebook 01 inicializa esse banco a partir do Excel, e o progresso de segmentacao/binarizacao e inferido pelos arquivos gerados em `generated/`.

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

O fluxo de execucao do projeto esta organizado em quatro notebooks:

- `notebooks/01_geracao_mascaras_e_segmentacao.ipynb`: gera as segmentacoes brutas dos modelos em `generated/segmentacoes_brutas/execucao_N/`;
- `notebooks/02_binarizacao_mascaras.ipynb`: binariza as mascaras de referencia com a strategy configurada para ground truth e gera mascaras previstas em `generated/segmentacoes_binarizadas/execucao_N/` para todas as strategies configuradas;
- `notebooks/03_calculo_das_avaliacoes.ipynb`: calcula e persiste as metricas de avaliacao no SQLite para todas as strategies configuradas;
- `notebooks/04_analise_das_avaliacoes.ipynb`: agrega os resultados persistidos, gera visualizacoes e compara os modelos.

Nos notebooks 01 e 02, a execucao operacional acontece por meio dos controllers em `src/controllers/`.

Regra de responsabilidade:

- controllers podem ler `src/config.py` e resolver caminhos, modelos e estrategias configuradas;
- services nao devem depender de `config`; eles recebem esses dados ja resolvidos por parametro.

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
