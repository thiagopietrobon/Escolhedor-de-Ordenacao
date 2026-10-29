# ⚡ Seletor Automático de Algoritmos de Ordenação

<p align="center">
  <strong>Qual algoritmo de ordenação escolher? Depende dos dados.</strong>
  <br />
  Um experimento em Python sobre algoritmos, heurísticas e desempenho.
</p>

<p align="center">
  <a href="https://github.com/thiagopietrobon/Escolhedor-de-Ordenacao">
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10 ou superior" />
  </a>
  <img src="https://img.shields.io/badge/Dependências-Biblioteca%20padrão-2E8B57?style=for-the-badge" alt="Somente biblioteca padrão" />
  <img src="https://img.shields.io/badge/Projeto-Experimental-8A63D2?style=for-the-badge" alt="Projeto experimental" />
</p>

<p align="center">
  <a href="https://github.com/thiagopietrobon/Escolhedor-de-Ordenacao/commits/main">
    <img src="https://img.shields.io/github/last-commit/thiagopietrobon/Escolhedor-de-Ordenacao?style=flat-square&logo=github" alt="Último commit" />
  </a>
  <img src="https://img.shields.io/github/languages/top/thiagopietrobon/Escolhedor-de-Ordenacao?style=flat-square" alt="Linguagem principal do repositório" />
  <a href="https://github.com/thiagopietrobon/Escolhedor-de-Ordenacao">
    <img src="https://img.shields.io/github/repo-size/thiagopietrobon/Escolhedor-de-Ordenacao?style=flat-square" alt="Tamanho do repositório" />
  </a>
</p>

---

## 🧠 Sobre o projeto

Nem sempre o algoritmo teoricamente mais eficiente é o mais rápido para uma entrada específica.

Este projeto implementa **seis algoritmos de ordenação e um seletor automático** que tenta escolher uma estratégia adequada às características dos dados. A proposta é investigar, por meio de experimentos reproduzíveis, quando essa escolha funciona, quando falha e qual é o custo de realizá-la.

Mais do que comparar tempos de execução, o projeto busca responder a uma pergunta:

> **Vale a pena analisar os dados antes de decidir como ordená-los?**

O seletor utiliza heurísticas baseadas no tamanho da lista, em amostras de sua organização e na possibilidade de utilizar Counting Sort com segurança. Ele não executa todos os algoritmos para descobrir qual deles vence.

## ✨ O que você encontrará aqui

- **Seis algoritmos:** diferentes estratégias para ordenar números inteiros.
- **Seleção automática:** escolha de um método com base em características da entrada.
- **Calibração experimental:** avaliação de parâmetros antes dos experimentos finais.
- **Testes automatizados:** verificação dos resultados dos algoritmos.
- **Benchmarks reproduzíveis:** cenários definidos, sementes e múltiplas repetições.
- **Análise de desempenho:** resultados registrados em CSV para comparação posterior.
- **Caso adversarial:** investigação de uma situação em que as heurísticas do seletor não identificam a melhor alternativa.

## ⚙️ Algoritmos implementados

| Algoritmo | Estratégia | Característica principal |
|---|---|---|
| Insertion Sort | Inserção direta | Simples e eficiente para entradas pequenas ou ordenadas |
| Merge Sort | Divisão e intercalação | Desempenho previsível e estabilidade |
| Quick Sort aleatório | Particionamento com pivô aleatório | Ordenação por comparação com partição em três vias |
| Quick Sort híbrido | Quick Sort + Insertion Sort | Combina estratégias para diferentes tamanhos de partição |
| Counting Sort | Contagem de ocorrências | Pode ser muito eficiente quando a faixa de valores é limitada |
| Radix Sort | Ordenação por dígitos, base 256 | Processa inteiros sem depender de comparações entre pares |

Os métodos retornam uma nova lista em ordem crescente e preservam a lista recebida. Counting Sort possui limites de amplitude e memória auxiliar para evitar alocações excessivas.

## 🔎 Como funciona o seletor?

A seleção é feita por regras e heurísticas previamente definidas, e não por uma competição entre todos os algoritmos.

```text
              Entrada de inteiros
                      │
                      ▼
             Análise da entrada
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
     Lista pequena          Lista maior
          │                       │
          ▼                       ▼
    Insertion Sort       Análise por amostragem
                                  │
                                  ▼
                       Counting Sort é seguro?
                           │             │
                          Sim           Não
                           │             │
                           ▼             ▼
                     Counting Sort   Análise das
                                      descidas
                                          │
                                          ▼
                                  Insertion ou
                                  método híbrido
```

**Importante:** o diagrama resume a ideia geral. A decisão efetiva segue as condições implementadas em `seletor.py`.

### Critérios atuais

1. Listas com até 32 elementos são direcionadas ao Insertion Sort.
2. Em listas maiores, o seletor examina uma amostra de pares adjacentes.
3. Counting Sort só é considerado quando a amplitude observada na amostra permite investigar essa alternativa.
4. A amplitude real e os limites de memória são verificados antes de selecionar Counting Sort.
5. Quando há poucas descidas na amostra, o seletor favorece Insertion Sort; nos demais casos, utiliza o algoritmo híbrido como alternativa padrão.

A heurística reduz o custo da análise, mas não garante a melhor escolha para todas as entradas. Essa limitação faz parte da investigação.

## 🚀 Começando

### Requisitos

- Python 3.10 ou superior.
- Git, para clonar o repositório.
- Nenhuma dependência externa.

### 1. Clone o repositório

```bash
git clone https://github.com/thiagopietrobon/Escolhedor-de-Ordenacao.git
cd Escolhedor-de-Ordenacao
```

### 2. Verifique o Python

No Windows, usando PowerShell:

```powershell
py --version
```

### 3. Execute os testes

```powershell
py -m unittest discover -v
```

### 4. Abra o programa

```powershell
py main.py
```

O menu interativo permite informar uma lista de inteiros separados por espaços ou utilizar uma lista de demonstração.

## 🧪 Experimentos e benchmarks

Os experimentos comparam os seis algoritmos fixos com o seletor automático em quatro cenários principais.

| Cenário | Entrada | O que investiga |
|---|---|---|
| A — Aleatória ampla | 10.000 inteiros entre −1 bilhão e 1 bilhão | O impacto de uma grande amplitude de valores |
| B — Faixa estreita | 10.000 inteiros entre −50 e 50 | A vantagem potencial de Counting Sort |
| C — Quase ordenada | 10.000 elementos com 100 trocas de posições | O comportamento em entradas parcialmente ordenadas |
| D — Pequena | 20 inteiros entre −1.000 e 1.000 | O custo dos métodos em entradas pequenas |

Cada cenário é preparado antes da cronometragem. Os métodos recebem cópias independentes da entrada, e os resultados são verificados em relação a `sorted()` fora da região cronometrada.

Os experimentos principais utilizam 15 repetições por alternativa e registram os tempos para análise estatística. As sementes permitem reproduzir a geração das entradas e controlar a aleatoriedade dos métodos.

### Executar os experimentos

```powershell
py experimentos.py
```

Esse comando executa os testes antes dos cenários finais e da busca adversarial. A execução pode demorar, especialmente devido ao Insertion Sort em listas maiores.

Para executar somente a busca e a medição adversarial:

```powershell
py experimentos.py --adversarial
```

### Calibração

Para investigar o limite utilizado pelo algoritmo híbrido:

```powershell
py calibracao.py
```

Para avaliar os critérios do seletor:

```powershell
py calibracao_seletor.py
```

A calibração registra os resultados e ajuda a avaliar os parâmetros. Ela não altera automaticamente as constantes do código.

## 📊 Resultados e dados

Os resultados são armazenados em arquivos CSV, permitindo que as medições sejam consultadas, filtradas e analisadas separadamente.

| Arquivo | Conteúdo |
|---|---|
| `resultados/resultados.csv` | Medições dos quatro cenários principais |
| `resultados/resultados_adversarial.csv` | Medições das alternativas no caso adversarial |
| `resultados/busca_adversarial.csv` | Registro das entradas examinadas durante a busca adversarial |
| `resultados/calibracao_hibrido.csv` | Dados brutos da calibração do algoritmo híbrido |
| `resultados/calibracao_seletor.csv` | Dados brutos da calibração dos critérios de seleção |

Os arquivos CSV são a saída dos experimentos. **O relatório é escrito e atualizado manualmente**, utilizando essas medições como base.

Consulte [`RELATORIO.md`](RELATORIO.md) para conhecer a metodologia, as medianas, as comparações e as conclusões da análise.

## 🛡️ Segurança e limitações

- Counting Sort verifica os limites de amplitude e memória antes de realizar alocações potencialmente excessivas.
- O limite de tempo por execução é configurável pela variável de ambiente `ORDENACAO_TIMEOUT_S` e tem valor padrão de 60 segundos.
- Uma heurística baseada em amostragem pode não representar adequadamente a lista inteira.
- O custo da seleção também faz parte do desempenho do método automático.
- Os tempos variam conforme o hardware, o sistema operacional e a versão do Python.

Portanto, os resultados devem ser interpretados como evidências experimentais, não como uma garantia universal de desempenho.

## 🗂️ Estrutura do projeto

```text
Escolhedor-de-Ordenacao/
├── main.py
├── algoritmos.py
├── seletor.py
├── experimentos.py
├── calibracao.py
├── calibracao_seletor.py
├── requirements.txt
├── RELATORIO.md
├── resultados/
│   ├── resultados.csv
│   ├── resultados_adversarial.csv
│   ├── busca_adversarial.csv
│   ├── calibracao_hibrido.csv
│   └── calibracao_seletor.csv
└── tests/
    ├── helpers.py
    └── testes dos algoritmos e do seletor
```

## 🎯 Objetivo acadêmico

O projeto explora algoritmos de ordenação, análise de complexidade, heurísticas, testes automatizados e experimentação empírica. Também demonstra por que uma decisão algorítmica deve considerar não apenas o custo de execução, mas o custo de escolher a estratégia.

---

<p align="center">
  <strong>Desenvolvido em Python para estudar, medir e questionar o desempenho dos algoritmos.</strong>
  <br />
  <a href="https://github.com/thiagopietrobon/Escolhedor-de-Ordenacao">Ver repositório no GitHub</a>
</p>
