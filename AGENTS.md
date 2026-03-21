# Repository Guidelines

## Objetivo do projeto

Este repositório visa avaliar modelos de remoção de fundo em imagens utilizando a biblioteca `rembg`.

## Como se orientar na documentacao

Em caso de duvida sobre onde encontrar contexto do projeto, consulte primeiro `README.md`.

O `README.md` da raiz funciona como guia rapido da documentacao e indica em que parte procurar:

- instrucoes de instalacao e execucao local;
- organizacao da suite de testes;
- fluxo de avaliacao;
- tags de curadoria;
- decisoes tecnicas;
- material de referencia.

Antes de sair procurando arquivos de forma ad hoc, use o `README.md` para localizar a secao ou o documento mais adequado ao contexto da tarefa.

## Regra para decisoes tecnicas

Sempre que uma decisao tecnica for tomada ou alterada, registre essa decisao em `docs/decisoes-tecnicas/`.

Essa regra vale para decisoes como:

- parametros de processamento;
- formatos de entrada ou saida;
- convencoes que afetem o pipeline;
- escolhas de implementacao que precisem ser preservadas para manutencao futura.

Tambem adicione um comentario no trecho de codigo ou configuracao onde essa decisao estiver materializada.

Esse comentario deve:

- apontar para o arquivo da documentacao correspondente;
- citar o caminho tomando `docs/` como raiz.

Exemplo de formato esperado no codigo:

```python
# Docs: decisoes-tecnicas/mascaras-do-rembg.md
```

Se a decisao estiver refletida em mais de um lugar, referencie a documentacao em todos os pontos relevantes.

## Docs

> A pasta `docs/` contém arquivos .md para detalhar aspectos específicos do projeto. Consulte:

- `guias/guia-do-projeto.md`: guia operacional do projeto.
- `guias/testes.md`: convencoes da suite automatizada.
- `guias/ci.md`: o que o workflow de CI executa hoje.
- `avaliacao/sistema-de-avaliacao.md`: visao geral do fluxo de avaliacao dos modelos.
- `avaliacao/tags-de-imagem.md`: taxonomia fechada das tags de curadoria de imagem; inclui `baixo_contraste` para casos em que o bufalo se confunde com o fundo por semelhanca de cor, luminosidade ou textura.
- `decisoes-tecnicas/`: pasta com as decisoes tecnicas que afetam o pipeline.
- `decisoes-tecnicas/u2net-cloth-seg.md`: decisao de manter o `u2net_cloth_seg` fora da configuracao ativa.
- `referencia/rembg/leia-me-do-rembg.md`: referência original do rembg cobrindo requisitos, instalação, subcomandos CLI, uso via
  docker e catálogo de modelos.
- `referencia/rembg/uso-do-rembg.md`: exemplos práticos de uso da função `remove` (sessões, alpha matting, somente máscara, bg
  customizado) para scripts Python.

## Rembg

> A pasta `rembg/` contém o repositório oficial do rembg clonado para referência.

> Caso a pasta não exista, clone o repositório oficial do rembg usando o github cli:
> ```bash
> gh repo clone danielgatis/rembg
> ```
