Este documento registra a decisao tecnica de usar uma estrategia dedicada e conservadora para binarizacao do ground truth.

## Decisao adotada

- usar `GroundTruthLimiarGlobal` apenas para as mascaras de ground truth;
- converter a imagem para grayscale, aplicar threshold global fixo e salvar o resultado em `.png`;
- nao aplicar blur gaussiano, opening nem outras morfologias nessa etapa;
- manter `GaussianaOpening` nas segmentacoes previstas dos modelos.

## Contexto

As mascaras manuais de ground truth ja chegam visualmente muito proximas de uma imagem binaria. A separacao entre objeto e fundo permanece nítida, e os artefatos introduzidos pela compressao JPEG aparecem apenas como poucos tons intermediarios nas bordas, perceptiveis sobretudo sob ampliacao.

Nessas condicoes, um pipeline mais agressivo de binarizacao deixa de ser vantajoso. Operacoes como suavizacao gaussiana e opening morfologico podem alterar o contorno da mascara sem necessidade, engrossando, afinando ou simplificando bordas que ja estavam semanticamente corretas.

## Justificativa

- o threshold global faz apenas a quantizacao final dos pixels ambiguos;
- a estrategia restaura valores binarios puros (`0` e `255`) sem redesenhar o contorno;
- a saida em `.png` evita reintroduzir artefatos de compressao com perdas;
- separar a estrategia do ground truth da estrategia das segmentacoes deixa explicita a diferenca entre uma mascara manual quase binaria e uma predicao bruta de modelo.

## Regra pratica

Quando a mascara manual ja parece binaria a olho nu e os desvios so aparecem sob zoom, a abordagem padrao passa a ser:

`JPEG quase binario -> threshold global -> PNG`

Se futuramente surgirem mascaras manuais com ruido real, buracos ou pontos isolados relevantes, essa decisao pode ser revisitada com amostras que justifiquem pos-processamento adicional.

## Evidencia visual

As capturas usadas na discussao desta decisao mostram exatamente esse padrao: uma mascara visualmente binaria e artefatos residuais perceptiveis apenas com bastante zoom nas bordas. Essas imagens ainda nao estao versionadas no repositorio como arquivos em `docs/`, entao a explicacao textual foi registrada aqui junto da regra adotada no codigo.
