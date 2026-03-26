# Documentacao do Repositorio

Este documento define a regra de sincronizacao entre `README.md`, `docs/` e `AGENTS.md`.

## Objetivo

Manter duas formas de acesso ao mesmo conhecimento do repositorio:

- uma forma humana, organizada e dividida entre `README.md` e `docs/`;
- uma forma consolidada em arquivo unico para agentes, em `AGENTS.md`.

## Papel de cada arquivo

- `README.md`: entrada rapida para humanos, com visao geral, comandos basicos e mapa da documentacao;
- `docs/`: documentacao detalhada, organizada por tema;
- `AGENTS.md`: copia consolidada do contexto do repositorio em um unico arquivo.

## Regra de sincronizacao

- Todo conhecimento operacional, conceitual ou normativo documentado em `README.md` ou em `docs/` tambem deve existir em `AGENTS.md`.
- Nada relevante deve existir apenas em `AGENTS.md`.
- Se um tema novo for documentado em `AGENTS.md`, ele precisa aparecer tambem em `README.md` ou em algum arquivo de `docs/`.
- Se um tema for alterado ou removido em um lado, o outro lado tambem deve ser atualizado.

## Criterio pratico

Ao editar a documentacao, confirme sempre:

1. a versao humana foi atualizada em `README.md` ou `docs/`;
2. a versao consolidada foi atualizada em `AGENTS.md`;
3. os caminhos e comandos citados continuam corretos.

## Quando usar cada lugar

- use `README.md` para onboarding rapido e comandos basicos;
- use `docs/` para explicacoes detalhadas, decisoes tecnicas, guias e referencias;
- use `AGENTS.md` quando um agente precisar ler o contexto inteiro do repositorio sem navegar por varios arquivos.

## Regra de worktree

Durante o desenvolvimento, o trabalho deve acontecer em apenas um unico worktree por vez.

Regras operacionais:

- nunca mexer em mais de um worktree ao mesmo tempo;
- se o usuario nao especificar em qual worktree a mudanca deve ser feita, e preciso perguntar antes de editar qualquer arquivo;
- so depois de o worktree estar explicitamente definido o desenvolvimento deve comecar.
