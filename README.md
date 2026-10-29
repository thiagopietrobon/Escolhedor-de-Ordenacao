# Seletor Automático de Algoritmos de Ordenação

Projeto em Python que implementa seis algoritmos de ordenação e compara um seletor automático com cada algoritmo fixo. O foco é medir, em condições reproduzíveis, quando a escolha automática compensa, quando falha e quanto custa analisar uma entrada.

> **Importante:** os resultados são empíricos e dependem do ambiente. O seletor não promete ser mais rápido para toda entrada possível.

## Requisitos

- Python 3.10 ou superior.
- Nenhuma dependência externa: o projeto utiliza somente a biblioteca padrão do Python.

## Começar no Windows

Abra o PowerShell na pasta do projeto e execute:

```powershell
py --version
py -m unittest discover -v
py main.py
```

O menu permite digitar uma lista de inteiros separados por espaço ou utilizar uma lista de demonstração. Os experimentos completos não são iniciados pelo menu.

## Comandos principais

| Objetivo | Comando |
|---|---|
| Executar o menu interativo | `py main.py` |
| Executar os testes | `py -m unittest discover -v` |
| Executar a calibração do limite híbrido | `py calibracao.py` |
| Calibrar critérios do seletor | `py calibracao_seletor.py` |
| Regenerar o relatório a partir dos CSVs | `py gerar_relatorio.py` |
| Executar os quatro cenários finais e a busca adversarial | `py experimentos.py` |
| Repetir somente a busca/medição adversarial | `py experimentos.py --adversarial` |

`experimentos.py` executa a suíte de testes antes de iniciar os cenários finais e interrompe o processo se algum teste falhar. A execução completa pode demorar porque inclui 15 repetições de Insertion Sort em listas de 10.000 elementos.

O limite de 60 segundos por execução é configurável pela variável de ambiente `ORDENACAO_TIMEOUT_S`. Exemplo no PowerShell:

```powershell
$env:ORDENACAO_TIMEOUT_S = "90"
py experimentos.py
```

O valor é aplicado por execução individual, não ao conjunto inteiro de experimentos. Uma execução interrompida não recebe um tempo inventado. O ambiente POSIX utiliza um alarme; no Windows, o método é executado em um processo isolado que pode ser encerrado ao ultrapassar o limite.

## Algoritmos implementados

| Identificador | Método | Observações |
|---|---|---|
| `insercao` | Insertion Sort | Bom em entradas pequenas ou já ordenadas; estabilidade preservada. |
| `intercalacao` | Merge Sort | Divide e intercala recursivamente; estável; usa memória auxiliar linear. |
| `rapida` | Quick Sort com pivô aleatório | Particionamento em três vias e semente configurável; não é estável. |
| `hibrida` | Quick Sort + Insertion Sort | Usa Quick Sort nas partições grandes e Insertion Sort nas pequenas; não é estável. |
| `contagem` | Counting Sort | Suporta negativos, zero e positivos; recusa amplitudes/memória auxiliar acima dos limites. |
| `base` | Radix Sort LSD, base 256 | Suporta negativos e positivos; as passagens por dígito são estáveis, mas a recombinação dos negativos não garante estabilidade global. |

Todos os métodos retornam uma nova lista crescente e preservam a lista recebida. Os testes comparam os resultados a `sorted()` e verificam valores negativos, magnitudes diferentes, repetidos e casos extremos.

## Seletor automático

As funções públicas são `escolher(v)` e `ordenar(v, seed=0)`. `escolher` retorna o identificador escolhido sem realizar a ordenação completa. `ordenar` inclui o custo de seleção e de execução do método escolhido. Para listas vazias ou unitárias, `ordenar` devolve uma cópia sem executar uma ordenação completa.

Os critérios congelados antes dos experimentos finais são:

1. Até 32 elementos, escolher `insercao`.
2. Para listas maiores, observar 256 pares adjacentes distribuídos pela lista.
3. Só investigar a faixa exata para Counting Sort se a amplitude observada na amostra for de, no máximo, 4.096.
4. Quando a faixa é candidata, calcular mínimo e máximo reais; escolher `contagem` se a amplitude não exceder `max(256, 4 × n)`, o limite de amplitude e o limite estimado de memória.
5. Se houver no máximo 2 descidas amostradas, escolher `insercao`; caso contrário, usar `hibrida` como fallback.

A amostra é apenas um indicador. Ela pode deixar passar características importantes do restante da lista, como demonstra o caso adversarial documentado no relatório.

### Limites do Counting Sort

Os valores iniciais são `MAX_AMPLITUDE_CONTAGEM = 500_000` e `MAX_MEMORIA_AUXILIAR_CONTAGEM = 33_554_432` bytes (32 MiB). A estimativa usa aproximadamente 36 bytes por posição do vetor de frequências, além do cabeçalho da lista. É uma estimativa conservadora, não um medidor exato, e não inclui a entrada e a lista de saída. Uma chamada direta que ultrapassa os limites lança `ValueError` antes de alocar o vetor; o seletor evita selecionar o método quando essas condições não são atendidas.

## Experimentos e reprodução

Os cenários principais são gerados uma única vez antes da cronometragem:

| Cenário | Tamanho | Geração | Semente |
|---|---:|---|---:|
| A — aleatória ampla | 10.000 | Uniforme entre -1.000.000.000 e 1.000.000.000 | `41001` |
| B — faixa estreita | 10.000 | Uniforme entre -50 e 50, com repetidos | `42002` |
| C — quase ordenada | 10.000 | `range(10000)` com 100 trocas de posições | `43003` |
| D — pequena | 20 | Uniforme entre -1.000 e 1.000 | `44004` |

Cada cenário usa uma lista de referência compartilhada; cada alternativa recebe uma cópia independente. A geração, as verificações e a medição separada de seleção não entram no tempo total de `ordenar`. O tempo total automático é cronometrado diretamente, sem somar medianas de componentes. Todos os sete métodos/alternativas têm 15 repetições por cenário, totalizando 420 registros. O método `contagem` é recusado no cenário A por segurança; suas 15 recusas são registradas sem mediana de ordenação.

As sementes dos métodos aleatórios nas repetições principais seguem `80000 + índice_do_cenário × 1000 + repetição`. A ordem das alternativas é embaralhada de forma reprodutível com a semente `71000 + índice_do_cenário × 100 + repetição`.

## Estrutura do projeto

```text
projeto-ordenacao/
├── README.md
├── RELATORIO.md
├── main.py
├── algoritmos.py
├── seletor.py
├── experimentos.py
├── calibracao.py
├── calibracao_seletor.py
├── gerar_relatorio.py
├── requirements.txt
├── resultados/
│   ├── resultados.csv
│   ├── resultados_adversarial.csv
│   ├── busca_adversarial.csv
│   ├── calibracao_hibrido.csv
│   └── calibracao_seletor.csv
└── tests/
    ├── __init__.py
    ├── helpers.py
    ├── test_insercao.py
    ├── test_intercalacao.py
    ├── test_rapida.py
    ├── test_hibrida.py
    ├── test_contagem.py
    ├── test_base.py
    └── test_seletor.py
```

`gerar_relatorio.py` reconstrói o `RELATORIO.md` a partir dos CSVs atuais, para que as medianas e as tabelas acompanhem as medições gravadas.

## Arquivos de resultados

- `resultados/resultados.csv`: 420 linhas de medições dos cenários A–D.
- `resultados/resultados_adversarial.csv`: 105 linhas, sete alternativas × 15 repetições para o caso adversarial.
- `resultados/busca_adversarial.csv`: registro de cada semente examinada durante a busca sequencial.
- `resultados/calibracao_hibrido.csv`: medições brutas dos limites candidatos do algoritmo híbrido.
- `resultados/calibracao_seletor.csv`: medições brutas de calibração dos critérios de tamanho, descidas amostradas e amplitude relativa.

O CSV principal inclui cenário, método, repetição, tempos, tamanho, sementes, parâmetros, método escolhido, situação e ambiente. Para a alternativa `ordenar`, `tempo_total_s` registra a chamada completa e `tempo_selecao_s` contém uma medição independente de `escolher`; `tempo_ordenacao_s` fica vazio, pois não é medido separadamente dentro daquela chamada. Os tempos de seleção e total são medianas independentes e não devem ser somados para estimar o total.

## Calibração

`calibracao.py` compara limites híbridos `[8, 12, 16, 24, 32, 48, 64]` em entradas aleatórias amplas, com duplicatas e quase ordenadas, nos tamanhos 1.500 e 6.000, usando sementes diferentes dos cenários finais. A menor mediana agregada medida foi obtida com limite 24.

`calibracao_seletor.py` examina, também em dados separados, o cruzamento entre Insertion Sort e o híbrido, os limiares de descidas amostradas e a relação entre amplitude e tamanho para Counting Sort. Os scripts gravam dados brutos e imprimem os valores selecionados, mas **não alteram automaticamente as constantes do código**. Caso os parâmetros sejam modificados, faça isso antes de uma nova avaliação final e repita a suíte de testes e os experimentos.

## Ambiente de referência das medições incluídas

- Python 3.13.5.
- Linux x86-64 (`Linux-6.18.55-x86_64-with-glibc2.41`).
- Biblioteca padrão; sem dependências externas.

Em outros computadores, sistemas operacionais ou versões do Python, os tempos podem variar. Consulte `RELATORIO.md` para a tabela completa de medianas, a análise dos resultados e o caso adversarial.

## Limitações conhecidas

- O seletor é uma heurística calibrada em amostras limitadas e pode escolher um método mais lento, como evidencia o caso adversarial.
- A análise de amostra não garante que a amplitude ou a ordenação observada represente a lista inteira.
- Counting Sort recusa entradas que excedam os limites de segurança, então algumas combinações não têm mediana comparável.
- Os tempos refletem o ambiente Linux usado para gerar os CSVs; outros computadores e versões do Python podem mudar os resultados.
