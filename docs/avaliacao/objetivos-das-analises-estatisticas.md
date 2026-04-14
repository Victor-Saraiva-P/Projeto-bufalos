# Objetivos das Analises Estatisticas

Este documento registra quais perguntas cada etapa analitica do projeto precisa responder e como essas perguntas se conectam com os notebooks 04 a 07.

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

### Estabilidade entre execucoes

Como a segmentacao bruta tem menos combinacoes do que a segmentacao binarizada, ela e o lugar apropriado para medir estabilidade entre execucoes.

Essa leitura usa:

- resumos por `modelo + execucao`;
- coeficiente de variacao entre execucoes;
- amplitude entre melhor e pior execucao.

Se a estabilidade for alta, a analise da segmentacao binarizada pode ser reduzida para uma execucao configuravel sem perda interpretativa relevante.

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

1. qual estrategia de binarizacao performa melhor no agregado;
2. como a binarizacao afeta o melhor modelo da segmentacao bruta;
3. quais tags impactam negativamente a binarizacao e se esse padrao repete a segmentacao bruta;
4. como o melhor resultado muda nos mesmos tres cenarios analiticos.

### Melhor forma de binarizacao

O ranking principal da segmentacao binarizada deve ser lido primeiro no nivel da estrategia, e nao no nivel do modelo.

As metricas centrais sao:

- `iou`;
- `precision`;
- `recall`;
- `area_similarity`;
- `perimetro_similarity`.

O objetivo e descobrir qual forma de binarizacao produz melhor equilibrio entre sobreposicao, cobertura e preservacao geometrica da mascara final.

### Gargalo entre modelo e binarizacao

Depois de identificar o melhor modelo da segmentacao bruta, a analise binarizada precisa verificar como cada estrategia afeta especificamente esse modelo.

Essa etapa responde a uma pergunta importante do projeto:

- se o melhor modelo bruto deixa de performar bem apos a binarizacao, o gargalo pode estar na estrategia de binarizacao e nao na mascara continua original.

Por isso, a leitura binarizada deve incluir um recorte focado no melhor modelo bruto em cada cenario.

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

## Consequencia pratica nos notebooks

Os notebooks passam a se dividir assim:

- `04`: calcula a analise estatistica da segmentacao bruta, incluindo tags negativas e ranking por cenario;
- `05`: visualiza a segmentacao bruta, incluindo melhor modelo por cenario e estabilidade entre execucoes;
- `06`: calcula a analise estatistica da segmentacao binarizada, incluindo tags negativas, ranking por cenario e recorte do melhor modelo bruto;
- `07`: visualiza a segmentacao binarizada, destacando melhor estrategia, melhor combinacao `modelo + estrategia` e comportamento do melhor modelo bruto apos a binarizacao.
