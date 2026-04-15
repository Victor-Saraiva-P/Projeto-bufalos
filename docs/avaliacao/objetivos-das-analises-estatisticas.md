# Objetivos das Analises Estatisticas

Este documento registra quais perguntas cada etapa analitica do projeto precisa responder e como essas perguntas se conectam com os notebooks 04 a 08.

## Segmentacao bruta

A analise estatistica da segmentacao bruta existe para responder quatro perguntas principais:

1. qual modelo produz a melhor mascara continua no agregado;
2. se os resultados entre execucoes sao estaveis o suficiente para permitir decisoes metodologicas posteriores;
3. quais tags de curadoria impactam negativamente as metricas;
4. como o melhor modelo muda quando o dataset e observado em cenarios diferentes.

### Melhor modelo na segmentacao bruta

O ranking da segmentacao bruta usa apenas as metricas calculadas sobre a mascara continua:

- `auprc`;
- `soft_dice`;
- `brier_score`.

O objetivo aqui e descobrir qual modelo entrega a melhor base antes da binarizacao. Isso evita misturar a qualidade intrinseca da mascara continua com o efeito posterior da estrategia de binarizacao.

Na leitura atual do worktree, esse ranking por cenario nao agrega mais as tres execucoes ao mesmo tempo. Como a estabilidade entre execucoes ja e medida separadamente, o ranking final da segmentacao bruta passa a usar uma execucao fixa configuravel, preferencialmente a mesma execucao usada na segmentacao binarizada.

Essa configuracao fica em:

- `analysis.segmentacao_bruta.execucao_escolhida`

Se ela nao for declarada, a analise bruta herda a mesma execucao definida para a segmentacao binarizada.

### Estabilidade entre execucoes

Como a segmentacao bruta tem menos combinacoes do que a segmentacao binarizada, ela e o lugar apropriado para medir estabilidade entre execucoes.

Essa leitura usa:

- resumos por `modelo + execucao`;
- coeficiente de variacao entre execucoes;
- amplitude entre melhor e pior execucao.

Se a estabilidade for alta, a analise da segmentacao binarizada pode ser reduzida para uma execucao configuravel sem perda interpretativa relevante.

Pelo mesmo motivo, o ranking por cenario da segmentacao bruta tambem pode ser lido a partir de uma execucao fixa, desde que a estabilidade continue sendo reportada separadamente com todas as execucoes.

### Tags que impactam negativamente

A segmentacao bruta tambem identifica quais tags de curadoria pioram as metricas de forma consistente.

Essa leitura nao serve apenas para descrever dificuldade. Ela tambem alimenta a construcao dos cenarios analiticos usados no ranking.

### Tres cenarios para o melhor modelo

O melhor modelo da segmentacao bruta deve ser observado em tres recortes:

- `dataset_completo`: todas as imagens, inclusive as com tags de dificuldade;
- `cenario_ideal`: imagens `ok` e imagens com apenas tags de dificuldade que foram consideradas neutras para essa analise;
- `apenas_ok`: somente imagens classificadas como `ok`.

Esses tres cenarios evitam uma conclusao unica e simplificada demais. Um modelo pode ser o melhor no conjunto completo, mas deixar de ser o melhor quando o ruido das tags negativas e removido.

#### Como o `cenario_ideal` e definido

O `cenario_ideal` nao deve mais ser montado automaticamente a partir de todas as tags que nao apareceram como negativas no agregado.

Motivo:

- a leitura mais confiavel sobre neutralidade vem da secao `Interacao entre modelo e dificuldade`;
- uma tag pode parecer neutra no agregado e ainda assim degradar um subconjunto importante de modelos;
- o recorte ideal precisa ser uma decisao analitica explicita e revisavel.

Por isso, a segmentacao bruta usa uma lista declarativa no `config.toml`:

- `analysis.segmentacao_bruta.cenario_ideal_tags_permitidas`

Essa lista deve conter apenas as tags de problema que continuam aceitas no `cenario_ideal` apos a leitura da interacao modelo x dificuldade. A tag `ok` nao precisa entrar nessa lista.

#### Criterio de decisao para incluir tags no `cenario_ideal`

A inclusao de uma tag de problema no `cenario_ideal` da segmentacao bruta deve seguir este criterio:

- a tag precisa permanecer neutra ou favoravel na leitura conjunta de `auprc`, `soft_dice` e `brier_score`;
- a leitura deve priorizar os modelos competitivos, e nao ganhos pontuais em modelos claramente fracos;
- se a tag piorar de forma recorrente as metricas principais nos modelos fortes, ela deve ficar fora do `cenario_ideal`;
- se a tag aparecer como mista no agregado, a secao de interacao continua tendo precedencia sobre qualquer resumo simplificado.

Em outras palavras, o `cenario_ideal` nao significa "sem dificuldade". Ele significa "sem dificuldades que, nesta analise, continuaram associadas a degradacao relevante dos resultados".

#### Leitura atual da segmentacao bruta

Na leitura atual dos heatmaps de `Interacao entre modelo e dificuldade`, as tags ficaram assim:

- incluir no `cenario_ideal`: `angulo_extremo`, `cortado`;
- excluir do `cenario_ideal`: `baixo_contraste`, `multi_bufalos`, `ocluido`.

Resumo da decisao:

- `angulo_extremo` permaneceu majoritariamente neutra ou levemente favoravel nas tres metricas;
- `cortado` tambem se manteve neutra ou favoravel, sem piora recorrente nos modelos competitivos;
- `baixo_contraste` mostrou piora consistente, especialmente em `auprc` e `brier_score`;
- `multi_bufalos` continuou associado a queda relevante nos modelos fortes;
- `ocluido` apresentou deterioracao visivel nas metricas principais e por isso nao entrou no recorte ideal.

## Segmentacao binarizada

A analise estatistica da segmentacao binarizada existe para responder quatro perguntas principais:

1. qual e a melhor estrategia de binarizacao para cada modelo;
2. como as melhores combinacoes `modelo + estrategia` se relacionam com os melhores modelos da segmentacao bruta;
3. quais tags impactam negativamente a binarizacao e se esse padrao repete a segmentacao bruta;
4. como o melhor resultado muda nos mesmos tres cenarios analiticos.

### Melhor forma de binarizacao por modelo

O ranking principal da segmentacao binarizada nao deve mais ser lido primeiro no agregado por estrategia. A pergunta central agora e: qual estrategia funciona melhor para cada modelo.

As metricas centrais sao:

- `iou`;
- `precision`;
- `recall`;
- `area_similarity`;
- `perimetro_similarity`.

O objetivo e descobrir qual forma de binarizacao produz melhor equilibrio entre sobreposicao, cobertura e preservacao geometrica da mascara final para cada distribuicao de scores gerada pelos modelos.

Consequencia pratica:

- o notebook 07 passa a mostrar heatmaps `modelo x estrategia`, com rank interno por modelo;
- o top 15 `modelo + estrategia` entra como leitura complementar para verificar se as melhores combinacoes finais continuam concentradas nos modelos fortes da segmentacao bruta;
- o ranking agregado global por estrategia deixa de ser a resposta principal, porque ele dilui o efeito do modelo e pode esconder combinacoes fortes.

### Comparacao entre bruto e binarizado

A comparacao entre segmentacao bruta e segmentacao binarizada continua sendo uma pergunta importante do projeto:

- se o melhor resultado bruto nao coincide com o melhor resultado binarizado, o gargalo pode estar na estrategia de binarizacao e nao na mascara continua original.

Mas essa comparacao nao deve ser codificada como recorte automatico dentro dos notebooks 06 e 07.

Regra adotada:

- os notebooks da segmentacao binarizada analisam apenas dados da propria binarizacao;
- a confrontacao com o melhor modelo bruto deve ser feita pela interpretacao conjunta dos artefatos finais dos notebooks 05 e 07;
- isso evita carregar para a analise binarizada uma decisao derivada de outra analise e preserva a leitura interpretativa dos resultados.

### Por que nao testar execucoes na segmentacao binarizada

Se a segmentacao bruta mostrar alta estabilidade entre execucoes, a segmentacao binarizada nao deve repetir essa mesma leitura.

Motivo:

- a combinacao `modelo x estrategia x execucao` cresce muito rapido;
- isso encarece bootstrap, testes nao parametricos e visualizacoes;
- o ganho interpretativo tende a ser baixo quando a estabilidade ja foi comprovada antes.

Por isso, os notebooks 06 e 07 usam uma execucao fixa configurada em `config.toml`.

### Tags negativas e cenarios na segmentacao binarizada

A segmentacao binarizada reutiliza a mesma logica dos tres cenarios:

- `dataset_completo`;
- `cenario_ideal`;
- `apenas_ok`.

Aqui tambem o `cenario_ideal` e declarativo. A lista de tags de problema aceitas nesse recorte fica em:

- `analysis.segmentacao_binarizada.cenario_ideal_tags_permitidas`

Essa lista deve ser montada a partir da leitura da secao `Interacao entre estrategia e dificuldade`. Ela nao deve ser compartilhada com a segmentacao bruta, porque uma tag pode ser neutra para os modelos brutos e ainda assim prejudicar a binarizacao, ou o contrario.

#### Criterio de decisao para incluir tags no `cenario_ideal`

Na segmentacao binarizada, a leitura deve priorizar o equilibrio final da mascara. Por isso, o criterio de inclusao no `cenario_ideal` e:

- a tag precisa permanecer neutra ou favoravel no conjunto principal de metricas (`iou`, `precision`, `recall` e `area_similarity`);
- `perimetro_similarity` entra como complemento geometrico, nao como criterio isolado para liberar uma tag;
- se a tag piorar de forma recorrente `iou` ou `area_similarity`, ela deve ficar fora do `cenario_ideal`, mesmo que melhore `recall` ou `perimetro_similarity`;
- a decisao deve olhar o padrao conjunto entre estrategias, e nao uma melhoria pontual de uma estrategia isolada.

#### Leitura atual da segmentacao binarizada

Na leitura atual dos heatmaps de `Interacao entre estrategia e dificuldade`, as tags ficaram assim:

- incluir no `cenario_ideal`: `angulo_extremo`, `cortado`;
- excluir do `cenario_ideal`: `baixo_contraste`, `multi_bufalos`, `ocluido`.

Resumo da decisao:

- `angulo_extremo` permaneceu neutra ou favoravel na maior parte das estrategias e metricas principais;
- `cortado` mostrou comportamento consistentemente favoravel, inclusive em `iou`, `recall` e `area_similarity`;
- `baixo_contraste` apresentou piora recorrente e consistente em praticamente todo o conjunto;
- `multi_bufalos` teve leitura mista, mas continuou associado a queda em `iou`, `precision` e `area_similarity`, que pesam mais na qualidade final da mascara;
- `ocluido` seguiu como a tag mais claramente negativa no conjunto, com piora consistente em todas as estrategias.

## Validacao final dos melhores resultados

Depois das leituras de segmentacao bruta e binarizada, o projeto passa a responder uma pergunta final adicional:

- se os melhores modelos, combinados com suas melhores binarizacoes, ja sao suficientes para segmentar bufalos sem retreinamento.

Essa leitura fica no notebook 08 e usa apenas o cenario configurado em:

- `analysis.validacao_final.cenario_base`

O fluxo esperado e:

1. selecionar os top `N` modelos da segmentacao bruta no cenario base;
2. selecionar a melhor binarizacao de cada um desses modelos no mesmo cenario;
3. avaliar as combinacoes finalistas contra thresholds absolutos configurados em `config.toml`;
4. concluir se os melhores resultados atuais sao suficientes ou se o projeto precisa de retreinamento.

A regra atual de aceitacao e declarativa e fica em:

- `analysis.validacao_final.acceptance_rule`

Na configuracao atual, a regra e `all_metrics`: a combinacao finalista so passa se atender aos thresholds minimos em todas as metricas binarizadas.

## Consequencia pratica nos notebooks

Os notebooks passam a se dividir assim:

- `04`: calcula a analise estatistica da segmentacao bruta, incluindo tags negativas e ranking por cenario;
- `05`: visualiza a segmentacao bruta, incluindo melhor modelo por cenario e estabilidade entre execucoes;
- `06`: calcula a analise estatistica da segmentacao binarizada, incluindo tags negativas e ranking por cenario apenas com dados da propria binarizacao;
- `07`: visualiza a segmentacao binarizada, destacando a melhor estrategia por modelo e as melhores combinacoes `modelo + estrategia`, deixando a comparacao com a segmentacao bruta para a leitura conjunta dos artefatos finais;
- `08`: valida os melhores modelos com suas melhores binarizacoes no cenario configurado e decide se os resultados atuais ja sao suficientes ou se apontam necessidade de retreinamento.
