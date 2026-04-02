# E2E com saidas persistentes

Este documento registra a decisao tecnica de fazer os testes `e2e` escreverem
artefatos em um diretorio persistente dentro de `tests/`.

## Contexto

Os testes ponta a ponta do projeto representam uma execucao pequena da pipeline
real de segmentacao, binarizacao e avaliacao.

Antes, esses testes escreviam tudo em `tmp_path`. Isso isolava a execucao, mas
impedia inspecao manual posterior dos arquivos gerados.

Como o objetivo do `e2e` aqui nao e apenas validar a automacao, mas tambem
permitir auditoria visual da saida, o caminho temporario deixou de atender bem o
uso esperado.

## Decisao adotada

- criar um override dedicado em `config.e2e.toml`;
- fazer os testes `e2e` carregarem esse arquivo via `BUFALOS_CONFIG_PATH`;
- gravar os artefatos em `tests/e2e_generated/`;
- limpar esse diretorio no inicio de cada teste;
- preservar a ultima execucao no filesystem para verificacao manual.

## Motivo

- separar o `e2e` da configuracao da suite rapida;
- tornar a saida previsivel e facil de localizar;
- permitir conferir manualmente segmentacoes, binarizacoes, avaliacao e SQLite
  gerados pelo fluxo ponta a ponta;
- manter o `e2e` como uma representacao pequena, mas concreta, da pipeline real.

## Consequencias

- o `e2e` deixa de depender de `tmp_path` para os artefatos principais;
- a configuracao de `tests/e2e_generated/` passa a ser parte explicita da suite;
- a ultima execucao do `e2e` pode ser inspecionada manualmente ao fim do teste;
- o diretorio de saida do `e2e` deve permanecer ignorado pelo Git.
