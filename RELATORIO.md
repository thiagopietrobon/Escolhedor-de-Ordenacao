# Relatório — Seletor Automático de Algoritmos de Ordenação

## 1. Objetivo

O objetivo deste trabalho é desenvolver e avaliar um sistema de ordenação adaptativa capaz de selecionar um algoritmo de ordenação de acordo com as características de uma lista de números inteiros.

O projeto implementa seis métodos: Insertion Sort, Merge Sort, Quick Sort com pivô aleatório, um método híbrido de Quick Sort com Insertion Sort, Counting Sort e Radix Sort. A função `escolher(v)` analisa a entrada e indica o método selecionado, enquanto `ordenar(v)` executa a seleção e realiza a ordenação.

A avaliação experimental busca responder a três questões: em quais situações a seleção automática apresenta resultados competitivos, quanto custa analisar a entrada antes de ordená-la e quais limitações podem fazer o seletor escolher um método menos eficiente que uma alternativa fixa.

Não se pressupõe que a seleção automática seja sempre superior. As conclusões são limitadas aos cenários e às condições efetivamente avaliados.

## 2. Metodologia experimental

Os experimentos foram realizados com quatro cenários principais, sete alternativas de execução — os seis algoritmos fixos e a função adaptativa — e 15 repetições por combinação.

Antes da execução dos cenários finais, a suíte de testes automatizados foi executada. O registro disponível informa que 14 testes passaram. Durante os experimentos, cada método recebeu uma cópia independente da mesma lista de entrada. A função nativa `sorted()` foi utilizada como referência de correção, e a comparação dos resultados ocorreu fora do intervalo cronometrado.

A geração dos dados, a preparação das cópias e a verificação de correção não foram incluídas no tempo de ordenação. A medição utilizou `time.perf_counter()`. As alternativas foram executadas em ordem pseudoaleatória reproduzível, e as sementes foram registradas nos arquivos CSV.

A mediana das 15 repetições foi utilizada como medida principal, reduzindo a influência de variações pontuais. Os tempos são apresentados em segundos.

O arquivo `resultados/resultados.csv` contém 420 registros, correspondentes a quatro cenários, sete alternativas e 15 repetições. Desses registros, 405 correspondem a execuções concluídas e 15 são recusas de Counting Sort por ultrapassarem o limite de segurança definido para a amplitude dos valores. O relatório das medições registra que não houve timeout.

## 3. Algoritmos implementados

| Algoritmo | Funcionamento e características |
|---|---|
| Insertion Sort (`insercao`) | Insere cada elemento na posição adequada de um prefixo já ordenado. Tem pior caso quadrático, mas pode ser eficiente em listas pequenas ou ordenadas. É estável. |
| Merge Sort (`intercalacao`) | Divide a lista, ordena as partes e intercala os resultados. Apresenta complexidade O(n log n) e utiliza memória auxiliar linear. É estável. |
| Quick Sort aleatório (`rapida`) | Utiliza um pivô aleatório e particionamento em três vias. Tem complexidade esperada O(n log n), embora o pior caso seja O(n²). Não é estável. |
| Método híbrido (`hibrida`) | Combina Quick Sort para partições maiores com Insertion Sort nas partições pequenas. O limite utilizado foi calibrado experimentalmente. Não é estável. |
| Counting Sort (`contagem`) | Utiliza um vetor de frequências associado ao intervalo dos valores. Pode ser eficiente quando a amplitude é pequena, mas exige memória proporcional a essa amplitude. A implementação recusa entradas que ultrapassem os limites de segurança. |
| Radix Sort (`base`) | Ordena os inteiros por grupos de dígitos, utilizando a estratégia LSD em base 256. Suporta valores negativos, positivos e zero. A implementação completa não garante estabilidade global. |

Os seis algoritmos retornam uma nova lista em ordem crescente e preservam a lista original. Todos participam da comparação como alternativas fixas, independentemente de serem escolhidos pelo seletor em determinado cenário.

## 4. Estratégia de seleção automática

A função `escolher(v)` utiliza características da entrada para selecionar um método, sem executar todos os algoritmos para descobrir qual deles é mais rápido. A função `ordenar(v)` realiza a seleção e executa o método escolhido.

As regras utilizadas nos experimentos finais foram:

1. Para listas com até 32 elementos, selecionar Insertion Sort.
2. Para listas maiores, analisar 256 pares adjacentes distribuídos pela entrada e contar as descidas, isto é, os pares em que o elemento anterior é maior que o seguinte.
3. Considerar Counting Sort somente quando a amplitude observada na amostra não ultrapassar 4.096.
4. Quando a amostra indicar uma faixa candidata, verificar os limites reais da entrada e considerar Counting Sort se a amplitude não ultrapassar `max(256, 4 × n)`, o limite absoluto de 500.000 e o limite estimado de memória de 32 MiB.
5. Se forem observadas no máximo duas descidas, selecionar Insertion Sort.
6. Nas demais situações, utilizar o método híbrido como alternativa padrão.

A política procura equilibrar o custo da análise, as características dos valores e a segurança de memória. Entretanto, a amostragem não descreve necessariamente todas as características da lista. Essa limitação é importante para interpretar os resultados.

## 5. Calibração dos parâmetros

### 5.1. Limite do método híbrido

A calibração do método híbrido foi realizada com dados separados dos cenários finais. Foram consideradas entradas aleatórias amplas, entradas com valores repetidos e entradas quase ordenadas, nos tamanhos 1.500 e 6.000. Os limites candidatos foram 8, 12, 16, 24, 32, 48 e 64, com cinco repetições por combinação.

| Limite da partição | Mediana agregada (s) |
|---:|---:|
| 8 | 0,003967685 |
| 12 | 0,003845941 |
| 16 | 0,003724040 |
| 24 | 0,003519945 |
| 32 | 0,003837979 |
| 48 | 0,003914269 |
| 64 | 0,004430402 |

Entre os limites avaliados, o valor 24 apresentou a menor mediana agregada e foi utilizado nos experimentos finais.

### 5.2. Limite para Insertion Sort

A calibração comparou Insertion Sort e o método híbrido para listas de 16, 24, 32, 48 e 64 elementos, em diferentes distribuições.

| Tamanho | Mediana de inserção (s) | Mediana do híbrido (s) |
|---:|---:|---:|
| 16 | 0,000005345 | 0,000012436 |
| 24 | 0,000011682 | 0,000017858 |
| 32 | 0,000018392 | 0,000022437 |
| 48 | 0,000037637 | 0,000033429 |
| 64 | 0,000074010 | 0,000046562 |

Nos dados avaliados, Insertion Sort apresentou mediana inferior à do híbrido até 32 elementos. A partir desse tamanho, o híbrido passou a apresentar resultado melhor entre os candidatos comparados. Por isso, o limiar de 32 elementos foi mantido.

### 5.3. Limite de descidas amostradas

A calibração das regras de descidas apresentou os seguintes custos agregados:

| Máximo de descidas | Custo agregado da regra (s) |
|---:|---:|
| 0 | 0,212973 |
| 1 | 0,187679 |
| 2 | 0,179830 |
| 4 | 0,182442 |
| 8 | 0,182442 |
| 12 | 0,288635 |

Entre os candidatos testados, o limite de duas descidas apresentou o menor custo agregado.

### 5.4. Critério de amplitude para Counting Sort

A calibração também avaliou a relação entre amplitude e tamanho da lista em entradas de 2.000, 5.000 e 10.000 elementos. Foram testadas razões entre amplitude e tamanho de 0,1 a 4,0.

Nos dados avaliados, Counting Sort apresentou mediana inferior à do método híbrido até a maior razão testada. O fator 4,0 foi utilizado como referência, sem remover os limites absolutos de amplitude e memória.

Os dados brutos das calibrações estão registrados em `resultados/calibracao_hibrido.csv` e `resultados/calibracao_seletor.csv`. A calibração orientou a escolha dos parâmetros, mas os scripts de calibração não alteram automaticamente as constantes do código.

## 6. Cenários avaliados

Foram utilizados quatro cenários principais, gerados de maneira reproduzível.

| Cenário | Tamanho | Características | Semente |
|---|---:|---|---:|
| A — Aleatória ampla | 10.000 | Inteiros uniformes entre −1.000.000.000 e 1.000.000.000 | 41001 |
| B — Faixa estreita | 10.000 | Inteiros uniformes entre −50 e 50, com valores repetidos | 42002 |
| C — Quase ordenada | 10.000 | Sequência inicialmente ordenada com 100 trocas de posições | 43003 |
| D — Lista pequena | 20 | Inteiros uniformes entre −1.000 e 1.000 | 44004 |

Cada cenário foi gerado uma única vez antes das medições. As alternativas receberam cópias da mesma entrada, permitindo comparações sob condições equivalentes.

A semente dos algoritmos aleatórios nas repetições principais seguiu a regra `80000 + índice_do_cenário × 1000 + repetição`. A ordem das alternativas foi embaralhada de forma reproduzível com a semente `71000 + índice_do_cenário × 100 + repetição`.

## 7. Ambiente e condições de execução

O ambiente registrado nos arquivos de resultados foi:

- Python 3.13.5.
- Linux x86-64 (`Linux-6.18.55-x86_64-with-glibc2.41`).
- Biblioteca padrão do Python, sem dependências externas.
- 15 repetições por alternativa em cada cenário.
- Mediana dos tempos como medida principal.
- Limite de 60 segundos por execução individual.

Os tempos podem variar em outros computadores, sistemas operacionais, versões do Python e condições de carga. Portanto, os valores deste relatório descrevem o ambiente registrado e não constituem garantias de desempenho universal.

## 8. Resultados dos quatro cenários principais

A tabela apresenta as medianas registradas nos experimentos. Para os métodos fixos, o tempo total corresponde ao tempo da ordenação. Para `ordenar(v)`, o tempo total inclui a seleção e a execução do método escolhido.

| Cenário | Alternativa | Mediana do tempo total (s) | Mediana da seleção (s) | Método escolhido | Situação |
|---|---|---:|---:|---|---|
| A | `insercao` | 2,804795692 | — | — | Concluída |
| A | `intercalacao` | 0,023045165 | — | — | Concluída |
| A | `rapida` | 0,033535514 | — | — | Concluída |
| A | `hibrida` | 0,027113445 | — | — | Concluída |
| A | `contagem` | — | — | — | Recusada por limite |
| A | `base` | 0,008793352 | — | — | Concluída |
| A | `ordenar(v)` | 0,031284966 | 0,000061660 | `hibrida` | Concluída |
| B | `insercao` | 2,501226268 | — | — | Concluída |
| B | `intercalacao` | 0,024155487 | — | — | Concluída |
| B | `rapida` | 0,012193101 | — | — | Concluída |
| B | `hibrida` | 0,011073851 | — | — | Concluída |
| B | `contagem` | 0,001420372 | — | — | Concluída |
| B | `base` | 0,002452437 | — | — | Concluída |
| B | `ordenar(v)` | 0,002270658 | 0,000437714 | `contagem` | Concluída |
| C | `insercao` | 0,068375614 | — | — | Concluída |
| C | `intercalacao` | 0,020433356 | — | — | Concluída |
| C | `rapida` | 0,030543519 | — | — | Concluída |
| C | `hibrida` | 0,023785615 | — | — | Concluída |
| C | `contagem` | 0,002245669 | — | — | Concluída |
| C | `base` | 0,003829602 | — | — | Concluída |
| C | `ordenar(v)` | 0,022684686 | 0,000058001 | `hibrida` | Concluída |
| D | `insercao` | 0,000009319 | — | — | Concluída |
| D | `intercalacao` | 0,000017025 | — | — | Concluída |
| D | `rapida` | 0,000029477 | — | — | Concluída |
| D | `hibrida` | 0,000018068 | — | — | Concluída |
| D | `contagem` | 0,000115637 | — | — | Concluída |
| D | `base` | 0,000045406 | — | — | Concluída |
| D | `ordenar(v)` | 0,000009423 | 0,000000259 | `insercao` | Concluída |

No cenário A, Counting Sort foi recusado nas 15 repetições porque a amplitude real, 1.999.542.472, ultrapassou o limite configurado de 500.000. Por esse motivo, não existe mediana válida para essa combinação.

## 9. Análise comparativa dos resultados

### 9.1. Cenário A — Aleatória ampla

Entre as alternativas que concluíram a ordenação, Radix Sort apresentou a menor mediana, de 0,008793352 s. A mediana de `ordenar(v)` foi 0,031284966 s, e o seletor escolheu o método híbrido.

O seletor não foi a alternativa mais rápida entre as que concluíram. Counting Sort não pode ser incluído nessa comparação como uma alternativa concluída, pois foi recusado pelo limite de segurança.

### 9.2. Cenário B — Faixa estreita

Counting Sort apresentou a menor mediana, de 0,001420372 s. O seletor também escolheu esse método, mas a chamada completa de `ordenar(v)` apresentou mediana de 0,002270658 s.

A mediana da chamada automática foi aproximadamente 1,60 vez a mediana do Counting Sort executado diretamente. Isso mostra que acertar a escolha não elimina o custo da análise prévia.

### 9.3. Cenário C — Quase ordenada

Counting Sort apresentou a menor mediana, de 0,002245669 s. O seletor escolheu o método híbrido, cuja chamada automática teve mediana de 0,022684686 s.

A mediana automática foi aproximadamente 10,10 vezes a mediana do Counting Sort fixo. Embora a lista estivesse quase ordenada, sua amplitude real era 10.000, valor que atendia aos limites de segurança do método de contagem.

Esse resultado evidencia uma limitação importante: estar quase ordenada não é a única característica relevante para a escolha de um algoritmo. A amplitude dos valores também pode influenciar significativamente o desempenho.

### 9.4. Cenário D — Lista pequena

Insertion Sort apresentou mediana de 0,000009319 s, enquanto a função automática apresentou mediana de 0,000009423 s. O seletor escolheu Insertion Sort, mas a chamada automática foi ligeiramente mais lenta.

A diferença foi de 0,000000104 s, ou 0,104 microssegundo. Essa diferença é pequena e deve ser interpretada com cautela, pois as medições de tempos muito curtos são sensíveis às condições de execução.

### 9.5. Comparação geral

O seletor não apresentou mediana inferior à de todos os métodos fixos em nenhum dos quatro cenários com comparação completa. No cenário A, Counting Sort não concluiu por segurança, portanto não existe comparação válida com todas as sete alternativas.

Nos cenários B e C, Counting Sort foi mais rápido que a chamada automática. No cenário D, Insertion Sort foi ligeiramente mais rápido. No cenário A, Radix Sort foi a alternativa mais rápida entre as que concluíram.

Esses resultados não tornam o seletor inútil, mas mostram que sua qualidade depende das regras de decisão e do custo de analisar a entrada. Uma política adaptativa deve ser avaliada pelo tempo total, e não somente pelo algoritmo que escolhe.

## 10. Custo da seleção

A função `escolher(v)` foi medida separadamente para avaliar o custo da análise. A tabela apresenta a mediana da seleção e a mediana total da chamada automática.

| Cenário | Mediana de `escolher(v)` (s) | Mediana de `ordenar(v)` (s) | Método escolhido |
|---|---:|---:|---|
| A | 0,000061660 | 0,031284966 | `hibrida` |
| B | 0,000437714 | 0,002270658 | `contagem` |
| C | 0,000058001 | 0,022684686 | `hibrida` |
| D | 0,000000259 | 0,000009423 | `insercao` |

As medições de seleção foram realizadas separadamente das medições da chamada completa. Portanto, não se deve somar as medianas dessas colunas para estimar o tempo total: a mediana da soma não é necessariamente igual à soma das medianas.

No cenário B, a análise prévia é relevante em relação ao tempo do Counting Sort fixo. Mesmo tendo selecionado o método mais rápido, a chamada automática foi mais lenta que a execução direta. Nos cenários A e C, o maior problema observado não foi apenas o custo da seleção, mas a escolha de uma alternativa mais lenta que um método fixo disponível.

## 11. Caso adversarial

Além dos quatro cenários principais, foi realizada uma busca sequencial por uma entrada em que o seletor escolhesse uma alternativa menos eficiente que um método fixo. A busca começou na semente 50000, com limite de até 80 sementes. Cada candidata recebeu cinco medições preliminares por método fixo. A primeira candidata, semente 50000, confirmou uma decisão inadequada e foi submetida ao protocolo completo de 15 repetições.

A lista adversarial foi construída a partir de `range(10000)`, com 100 trocas de posições controladas pela semente 50000. Assim, a entrada pode ser reproduzida com os mesmos parâmetros.

| Alternativa | Mediana do tempo total (s) |
|---|---:|
| `insercao` | 0,066926937 |
| `intercalacao` | 0,020651374 |
| `rapida` | 0,029813884 |
| `hibrida` | 0,023714968 |
| `contagem` | 0,002202427 |
| `base` | 0,004295495 |
| `ordenar(v)` | 0,026529763 |

O seletor escolheu o método híbrido nas 15 repetições. A amostra identificou quatro descidas, acima do limite de duas, e apresentou amplitude amostrada de 9.999, acima do teto operacional de 4.096. Por isso, o seletor não realizou a verificação exata da faixa e utilizou o método híbrido como alternativa padrão.

A amplitude real da lista era 10.000, compatível com os limites de segurança do Counting Sort. Esse algoritmo apresentou mediana de 0,002202427 s, enquanto a chamada automática apresentou mediana de 0,026529763 s — aproximadamente 12,05 vezes mais lenta.

O caso mostra que uma amostra pode não representar adequadamente as características relevantes de toda a entrada. A limitação não decorre de uma falha de correção da ordenação, mas de uma decisão de seleção que não escolheu o método mais rápido entre os avaliados.

Uma melhoria possível seria rever o critério de amplitude amostrada e avaliar quando compensa calcular a faixa exata. Essa mudança exigiria nova calibração e novos experimentos; portanto, não é apresentada como uma melhoria já implementada ou validada.

Os registros da busca e do caso adversarial estão em `resultados/busca_adversarial.csv` e `resultados/resultados_adversarial.csv`.

## 12. Limitações

Os resultados devem ser interpretados considerando as seguintes limitações:

1. As medições representam um único ambiente e podem variar em outros computadores, sistemas operacionais e versões do Python.
2. A amostra de 256 pares pode deixar de identificar características importantes do restante da lista.
3. O teto de amplitude amostrada de 4.096 pode impedir a consideração de Counting Sort mesmo quando a amplitude real é segura, como ocorreu no cenário adversarial.
4. O limite de memória do Counting Sort utiliza uma estimativa conservadora, e não uma medição exata do consumo de memória.
5. As comparações utilizam medianas de 15 repetições e não incluem um teste estatístico formal.
6. No cenário A, Counting Sort foi recusado por segurança; não há mediana válida para essa combinação.
7. O caso adversarial demonstra uma falha em uma entrada específica, mas não permite estimar a frequência de falhas para todas as entradas possíveis.
8. Os resultados não demonstram superioridade universal de nenhum algoritmo nem da função adaptativa.

## 13. Conclusão

Os experimentos mostram que a seleção automática pode escolher um algoritmo adequado em determinadas situações, mas não garante desempenho superior à execução de um método fixo. A avaliação revelou que o custo da análise e as limitações das regras de seleção podem reduzir ou eliminar o benefício esperado.

No cenário de faixa estreita, o seletor identificou Counting Sort, mas a chamada completa ainda foi mais lenta que a execução direta do algoritmo. No cenário quase ordenado, a amostragem levou à escolha do método híbrido, apesar da vantagem do Counting Sort. O caso adversarial confirmou essa limitação em uma entrada reproduzível. Para listas pequenas, a diferença entre a chamada automática e Insertion Sort foi mínima, mas o método fixo ainda apresentou a menor mediana.

A conclusão é que a seleção adaptativa deve considerar tanto o custo de ordenar quanto o custo de analisar a entrada. Os resultados sustentam uma avaliação limitada às condições testadas: o seletor implementado não superou consistentemente os métodos fixos e ainda possui limitações que poderiam ser investigadas em trabalhos futuros.

## 14. Arquivos de evidência

Os arquivos CSV que fundamentam a análise são:

- `resultados/resultados.csv`: medições dos quatro cenários principais.
- `resultados/resultados_adversarial.csv`: medições completas do caso adversarial.
- `resultados/busca_adversarial.csv`: registro das candidatas examinadas durante a busca.
- `resultados/calibracao_hibrido.csv`: dados brutos da calibração do limite híbrido.
- `resultados/calibracao_seletor.csv`: dados brutos da calibração dos critérios do seletor.

As tabelas e interpretações deste documento foram redigidas manualmente a partir dos dados experimentais registrados nesses arquivos.
