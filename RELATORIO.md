# Relatório — Seletor Automático de Algoritmos de Ordenação

## 1. Objetivo e metodologia

O objetivo foi implementar seis métodos de ordenação e avaliar experimentalmente se `ordenar(v)` supera a escolha antecipada de um algoritmo fixo. Foram usados quatro cenários reproduzíveis, 15 repetições por alternativa, mediana dos tempos como medida principal e uma busca por um caso em que a regra do seletor não escolhesse a alternativa mais rápida.

A suíte `unittest` foi executada antes da avaliação final: **14 testes passaram**. Em cada medição, a entrada foi copiada antes de iniciar o cronômetro; geração e validação do resultado ficaram fora do trecho cronometrado. Após cada execução concluída, o resultado foi comparado a `sorted()`; um resultado incorreto interromperia os experimentos. A ordem das alternativas foi pseudoaleatória e reprodutível por repetição. Os tempos registrados foram medidos, não simulados.

O CSV principal contém 420 registros (4 cenários × 7 alternativas × 15 repetições): 405 execuções concluídas e 15 recusas do Counting Sort por limite de segurança. Não houve timeout.

## 2. Descrição dos algoritmos e propriedades

| Identificador | Ideia e complexidade esperada | Estabilidade e limitações |
|---|---|---|
| `insercao` | Insere cada elemento no prefixo ordenado; pior caso O(n²), melhor caso O(n) em entrada ordenada. | Estável; funciona bem em listas pequenas ou com poucas inversões. |
| `intercalacao` | Merge Sort; O(n log n), com memória auxiliar O(n). | Estável; faz alocações auxiliares ao intercalar. |
| `rapida` | Quick Sort com pivô aleatório e particionamento em três vias; esperado O(n log n), pior caso O(n²). | Não estável; a semente torna a sequência de pivôs reproduzível. |
| `hibrida` | Quick Sort nas partições grandes e Insertion Sort nas partições pequenas. | Não estável; limite de partição calibrado em dados separados. |
| `contagem` | Counting Sort com amplitude k; O(n + k), memória proporcional a k, além da saída. | Implementação por posições acumuladas e percurso reverso; estável. Recusa amplitudes/memória acima dos limites. |
| `base` | Radix Sort LSD em base 256; número de passagens depende da magnitude dos inteiros, com memória auxiliar O(n + 256) por passagem. | As passagens por dígito são estáveis, mas a recombinação dos negativos inverte a parte negativa; a implementação completa não garante estabilidade global. Suporta inteiros negativos, zero e positivos. |

Todas as implementações retornam uma nova lista crescente e preservam a entrada original. A estabilidade está documentada por implementação; o contrato deste projeto trabalha com inteiros.

## 3. Regras teóricas do seletor

`escolher(v)` retorna um identificador sem realizar a ordenação completa. `ordenar(v, seed=0)` executa a escolha e a ordenação. Para listas vazias ou unitárias, `ordenar` devolve uma cópia sem executar uma ordenação completa.

As regras congeladas antes dos cenários finais foram:

1. Para n ≤ 32, escolher `insercao`.
2. Para entradas maiores, observar 256 pares adjacentes espalhados pela lista e contar descidas (pares em que o elemento à esquerda é maior que o da direita).
3. Considerar Counting Sort somente se a amplitude observada na amostra for ≤ 4.096. Nesse caso, calcular mínimo e máximo reais e só escolher `contagem` se a amplitude real for ≤ max(256, 4n), ≤ 500.000 e a memória auxiliar estimada não exceder 32 MiB.
4. Se houver no máximo duas descidas amostradas, escolher `insercao`.
5. Caso não haja evidência suficiente, usar `hibrida` como fallback.

A amostra é apenas um indicador. O teto amostrado de 4.096 é uma barreira operacional que evita iniciar uma varredura exata quando a faixa já parece larga; ele não prova que Counting Sort seria inadequado acima desse valor. O caso adversarial mostra o custo dessa simplificação.

## 4. Calibração e parâmetros escolhidos

### 4.1 Limite do método híbrido

A calibração usou dados separados dos cenários finais: três famílias (aleatória ampla, duplicatas e quase ordenada), tamanhos 1.500 e 6.000, cinco repetições por combinação e limites candidatos 8, 12, 16, 24, 32, 48 e 64. As sementes estão em `resultados/calibracao_hibrido.csv` (240 observações incluindo Quick Sort de referência). A menor mediana agregada foi obtida com limite 24, congelado para os cenários finais.

| Limite | Mediana agregada (s) |
|---:|---:|
| 8 | 0.003967685 |
| 12 | 0.003845941 |
| 16 | 0.003724040 |
| 24 | 0.003519945 |
| 32 | 0.003837979 |
| 48 | 0.003914269 |
| 64 | 0.004430402 |

### 4.2 Critérios do seletor

A calibração separada de `insercao` versus `hibrida` testou tamanhos 16, 24, 32, 48 e 64, com dados aleatórios, duplicatas e quase ordenados. O maior tamanho candidato cuja mediana agregada de Insertion Sort não superou a do híbrido foi 32.

| Tamanho | Mediana agregada de `insercao` (s) | Mediana agregada de `hibrida` (s) |
|---:|---:|---:|
| 16 | 0.000005345 | 0.000012436 |
| 24 | 0.000011682 | 0.000017858 |
| 32 | 0.000018392 | 0.000022437 |
| 48 | 0.000037637 | 0.000033429 |
| 64 | 0.000074010 | 0.000046562 |

Para o limiar de descidas amostradas, os custos agregados dos limites testados foram:

| Máximo de descidas | Custo agregado da regra (s) |
|---:|---:|
| 0 | 0.212973 |
| 1 | 0.187679 |
| 2 | 0.179830 |
| 4 | 0.182442 |
| 8 | 0.182442 |
| 12 | 0.288635 |

O menor custo agregado entre os candidatos foi obtido com limite 2. A relação amplitude/tamanho para Counting Sort foi avaliada em listas de 2.000, 5.000 e 10.000 elementos, com razões candidatas de 0,1 a 4,0. Nos dados medidos, Counting Sort teve mediana inferior à do híbrido nos três tamanhos até a maior razão testada; o fator foi definido em 4,0, mantendo-se os limites absolutos de segurança. As 366 observações da calibração estão em `resultados/calibracao_seletor.csv`.

A amostra de 256 pares e o teto amostrado 4.096 foram mantidos como restrições de custo da análise. O teto de 4.096 não foi otimizado por busca de parâmetros: foi fixado antes da avaliação como limite operacional da varredura exata de mínimo/máximo. Ele deve ser reconsiderado em trabalho futuro, mas não foi alterado após observar os resultados finais.

### 4.3 Segurança do Counting Sort

Os limites iniciais congelados são amplitude máxima 500.000 e memória auxiliar estimada máxima de 33.554.432 bytes (32 MiB). A estimativa usa aproximadamente 36 bytes por posição do vetor de frequências e o cabeçalho da lista; não inclui a entrada nem a saída. Os limites são configuráveis. Uma chamada direta recusa uma faixa insegura com `ValueError` antes de tentar alocar o vetor.

## 5. Cenários experimentais

| Cenário | Tamanho | Definição da entrada | Semente de dados |
|---|---:|---|---:|
| A — aleatória ampla | 10.000 | Inteiros uniformes entre -1.000.000.000 e 1.000.000.000 | 41001 |
| B — faixa estreita | 10.000 | Inteiros uniformes entre -50 e 50, com duplicatas | 42002 |
| C — quase ordenada | 10.000 | `range(10000)` com 100 trocas; os índices são distintos em cada troca, mas podem reaparecer depois | 43003 |
| D — pequena | 20 | Inteiros uniformes entre -1.000 e 1.000 | 44004 |

A geração ocorreu uma única vez por cenário e ficou fora dos tempos. Cada alternativa recebeu uma cópia independente da mesma lista de referência. As sementes dos métodos aleatórios seguiram `80000 + índice_do_cenário × 1000 + repetição`; a ordem das alternativas foi embaralhada com `71000 + índice_do_cenário × 100 + repetição`. O limite de cada execução individual foi 60 segundos.

## 6. Ambiente e condições de execução

- Python 3.13.5.
- Linux x86-64 (`Linux-6.18.55-x86_64-with-glibc2.41`).
- Somente a biblioteca padrão do Python.
- 15 repetições por combinação; medida principal: mediana do tempo total, em segundos.
- Geração e verificação de correção fora do trecho cronometrado.
- O tempo de seleção foi medido em chamada separada de `escolher(v)`; não foi somado à mediana total. Não se presume que a mediana da soma seja a soma das medianas.

## 7. Tabela principal — 28 combinações

Para métodos fixos, o total é o tempo da ordenação. Para `ordenar(v)`, é a chamada completa, incluindo escolha e execução. O tempo de seleção é uma mediana independente, preenchida somente na linha automática.

| Cenário | Alternativa | Mediana do tempo total (s) | Mediana da seleção (s) | Método escolhido por `ordenar` | Situação |
|---|---|---:|---:|---|---|
| A — Lista aleatória com valores amplos | insercao | 2.804795692 | — | — | Concluída (15/15) |
| A — Lista aleatória com valores amplos | intercalacao | 0.023045165 | — | — | Concluída (15/15) |
| A — Lista aleatória com valores amplos | rapida | 0.033535514 | — | — | Concluída (15/15) |
| A — Lista aleatória com valores amplos | hibrida | 0.027113445 | — | — | Concluída (15/15) |
| A — Lista aleatória com valores amplos | contagem | — | — | — | Recusada por limite (15/15) |
| A — Lista aleatória com valores amplos | base | 0.008793352 | — | — | Concluída (15/15) |
| A — Lista aleatória com valores amplos | ordenar(v) | 0.031284966 | 0.000061660 | hibrida | Concluída (15/15) |
| B — Faixa estreita de valores | insercao | 2.501226268 | — | — | Concluída (15/15) |
| B — Faixa estreita de valores | intercalacao | 0.024155487 | — | — | Concluída (15/15) |
| B — Faixa estreita de valores | rapida | 0.012193101 | — | — | Concluída (15/15) |
| B — Faixa estreita de valores | hibrida | 0.011073851 | — | — | Concluída (15/15) |
| B — Faixa estreita de valores | contagem | 0.001420372 | — | — | Concluída (15/15) |
| B — Faixa estreita de valores | base | 0.002452437 | — | — | Concluída (15/15) |
| B — Faixa estreita de valores | ordenar(v) | 0.002270658 | 0.000437714 | contagem | Concluída (15/15) |
| C — Lista quase ordenada | insercao | 0.068375614 | — | — | Concluída (15/15) |
| C — Lista quase ordenada | intercalacao | 0.020433356 | — | — | Concluída (15/15) |
| C — Lista quase ordenada | rapida | 0.030543519 | — | — | Concluída (15/15) |
| C — Lista quase ordenada | hibrida | 0.023785615 | — | — | Concluída (15/15) |
| C — Lista quase ordenada | contagem | 0.002245669 | — | — | Concluída (15/15) |
| C — Lista quase ordenada | base | 0.003829602 | — | — | Concluída (15/15) |
| C — Lista quase ordenada | ordenar(v) | 0.022684686 | 0.000058001 | hibrida | Concluída (15/15) |
| D — Lista pequena | insercao | 0.000009319 | — | — | Concluída (15/15) |
| D — Lista pequena | intercalacao | 0.000017025 | — | — | Concluída (15/15) |
| D — Lista pequena | rapida | 0.000029477 | — | — | Concluída (15/15) |
| D — Lista pequena | hibrida | 0.000018068 | — | — | Concluída (15/15) |
| D — Lista pequena | contagem | 0.000115637 | — | — | Concluída (15/15) |
| D — Lista pequena | base | 0.000045406 | — | — | Concluída (15/15) |
| D — Lista pequena | ordenar(v) | 0.000009423 | 0.000000259 | insercao | Concluída (15/15) |

## 8. Vencedores observados e interpretação

- **Cenário A:** Counting Sort foi recusado em 15/15 repetições, pois a amplitude real 1,999,542,472 excedeu o limite 500.000. Entre as seis alternativas concluídas, `base` teve a menor mediana (0.008793352 s), frente a 0.031284966 s do seletor. Não se declara vencedor formal para as sete alternativas porque Counting Sort não produziu uma mediana válida; o seletor também não foi o mais rápido entre os métodos concluídos.
- **Cenário B:** `contagem` foi a alternativa mais rápida, com 0.001420372 s. O seletor também escolheu Counting Sort nas 15 repetições, mas o total de `ordenar(v)` foi 0.002270658 s, cerca de 1.60 vezes o tempo da chamada fixa.
- **Cenário C:** `contagem` teve a menor mediana (0.002245669 s). `ordenar(v)` levou 0.022684686 s e escolheu `hibrida`; a mediana automática foi cerca de 10.10 vezes a mediana de Counting Sort. Embora a entrada estivesse quase ordenada, seus valores estavam entre 0 e 9.999, amplitude real 10.000, segura para o método.
- **Cenário D:** `ordenar(v)` teve 0.000009423 s e `insercao` teve 0.000009319 s. `insercao` foi ligeiramente mais rápida que `ordenar(v)`, por 0.104 microssegundos. A diferença é pequena, mas pela regra estrita a alternativa automática não venceu o algoritmo fixo.

O seletor não satisfez o critério estrito de mediana inferior a todos os seis métodos fixos em nenhum cenário com sete medianas comparáveis. No cenário A, Counting Sort foi recusado por segurança e não há comparação completa. Em B e C, Counting Sort foi mais rápido; em A, a alternativa `base` foi a mais rápida entre as que concluíram.

## 9. Custo da análise

| Cenário | Mediana de `escolher(v)` (s) | Mediana total de `ordenar(v)` (s) | Método selecionado |
|---|---:|---:|---|
| A — Lista aleatória com valores amplos | 0.000061660 | 0.031284966 | hibrida |
| B — Faixa estreita de valores | 0.000437714 | 0.002270658 | contagem |
| C — Lista quase ordenada | 0.000058001 | 0.022684686 | hibrida |
| D — Lista pequena | 0.000000259 | 0.000009423 | insercao |

Em B, a mediana de `escolher(v)` foi 0.000437714 s; a mediana total automática ficou cerca de 59.9% acima da mediana fixa de Counting Sort. A proporção entre medianas é descritiva: os tempos de seleção e total são medições independentes e não devem ser somados para estimar o tempo total. Em D, a regra baseada no tamanho é quase imediata.

## 10. Caso adversarial medido e reproduzível

A busca foi determinística e sequencial: começou na semente 50000, avançou sem saltos e permitia até 80 sementes. Cada candidata recebia cinco medições preliminares de cada método fixo; a primeira candidata, semente **50000**, confirmou uma decisão inadequada. Depois, as sete alternativas receberam o protocolo completo de 15 repetições. Os dados estão em `resultados/resultados_adversarial.csv` e `resultados/busca_adversarial.csv`.

A entrada pode ser reconstruída exatamente assim:

```python
import random

valores = list(range(10_000))
rng = random.Random(50000)
for _ in range(100):
    i, j = rng.sample(range(10_000), 2)
    valores[i], valores[j] = valores[j], valores[i]
```

O seletor escolheu `hibrida` nas 15 repetições. A amostra observou quatro descidas, acima do limite 2. O mínimo e máximo amostrados foram 0 e 9.998, com amplitude amostrada 9.999. Como essa amplitude ultrapassou o teto amostrado 4.096, o seletor não verificou a faixa exata e usou o híbrido como fallback. No entanto, a amplitude real era 10.000, segura e pequena o bastante para Counting Sort.

| Alternativa | Mediana do tempo total (s) | Mediana da seleção (s) | Método escolhido | Situação |
|---|---:|---:|---|---|
| insercao | 0.066926937 | — | — | 15/15 concluídas |
| intercalacao | 0.020651374 | — | — | 15/15 concluídas |
| rapida | 0.029813884 | — | — | 15/15 concluídas |
| hibrida | 0.023714968 | — | — | 15/15 concluídas |
| contagem | 0.002202427 | — | — | 15/15 concluídas |
| base | 0.004295495 | — | — | 15/15 concluídas |
| ordenar(v) | 0.026529763 | 0.000089482 | hibrida | 15/15 concluídas |

Counting Sort foi o método fixo mais rápido, com 0.002202427 s. A mediana total automática foi 0.026529763 s — aproximadamente **12.05 vezes** o tempo de Counting Sort, diferença de 0.024327336 s. A mediana do híbrido isolado foi 0.023714968 s. Isso demonstra uma decisão inadequada medida, não uma hipótese teórica fabricada.

Uma possível melhoria futura seria tornar a verificação da faixa adaptativa: quando a amplitude amostrada for grande em termos absolutos, mas ainda pequena em relação a n, avaliar se compensa calcular mínimo e máximo exatos antes do fallback. A melhoria adicionaria uma varredura O(n) à decisão e precisaria ser calibrada e avaliada pelo tempo total. A regra congelada não foi alterada depois de observar os resultados finais.

## 11. Limitações

1. As medições refletem um único ambiente; outros sistemas e versões do Python podem produzir tempos diferentes.
2. A amostra de 256 pares pode deixar passar características relevantes do restante da entrada; o caso adversarial demonstra essa falha.
3. O teto amostrado 4.096 pode deixar de considerar Counting Sort em entradas cuja amplitude real seja adequada.
4. O limite de memória auxiliar usa uma estimativa conservadora, não o uso real exato de memória; a estimativa refere-se ao vetor de frequências.
5. A comparação usa medianas de 15 repetições e não aplica teste estatístico formal. Diferenças mínimas, como no cenário D, não provam vantagem prática.
6. No cenário A, Counting Sort recusou a entrada por segurança; não existe mediana válida para essa combinação e não se declara vencedor formal entre todas as sete alternativas.
7. O caso adversarial demonstra uma falha em uma entrada específica; não estima a frequência de falhas em toda entrada possível.

## 12. Conclusão

Os experimentos indicam que a seleção automática pode escolher um método plausível em alguns contextos, mas não superou de forma consistente a escolha fixa. O seletor não satisfez o critério estrito de mediana inferior a todos os seis métodos fixos em nenhum cenário com sete medianas comparáveis. No cenário A, Counting Sort foi recusado por segurança e não há comparação completa. Em uma faixa estreita, o seletor escolheu Counting Sort, embora o custo da decisão tenha reduzido o ganho. Na lista quase ordenada, a amostra bloqueou a análise exata da amplitude e levou ao híbrido, apesar da vantagem clara de Counting Sort. O caso adversarial confirmou a limitação com medições completas.

Os dados sustentam uma conclusão limitada: **a seleção automática pode ajudar, mas a qualidade das regras e o custo de analisá-las determinam se ela compensa**. Eles não demonstram superioridade universal. As tabelas e conclusões deste relatório são geradas a partir dos CSVs incluídos no projeto.

## 13. Arquivos de evidência

- `resultados/resultados.csv`: dados brutos dos quatro cenários finais.
- `resultados/resultados_adversarial.csv`: dados brutos do caso adversarial.
- `resultados/busca_adversarial.csv`: registro das sementes tentadas na busca.
- `resultados/calibracao_hibrido.csv`: calibração do limite do híbrido.
- `resultados/calibracao_seletor.csv`: calibração dos critérios do seletor.
