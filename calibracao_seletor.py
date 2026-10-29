"""Calibração experimental de critérios do seletor, com dados não finais."""
from __future__ import annotations

import csv
import random
import statistics
import time
from pathlib import Path

from algoritmos import base, contagem, hibrida, insercao
from seletor import _indices_amostra

RAIZ = Path(__file__).resolve().parent
PASTA = RAIZ / "resultados"
REPETICOES = 5
SEMENTE_BASE = 61_700


def _medir(funcao, entrada, repeticoes=REPETICOES):
    tempos = []
    esperado = sorted(entrada)
    for i in range(repeticoes):
        inicio = time.perf_counter()
        resultado = funcao(entrada.copy())
        tempos.append(time.perf_counter() - inicio)
        if resultado != esperado:
            raise RuntimeError("Falha de correção durante a calibração do seletor")
    return statistics.median(tempos)


def _gerar(familia, n, seed):
    rng = random.Random(seed)
    if familia == "aleatoria_ampla":
        return [rng.randint(-10**7, 10**7) for _ in range(n)]
    if familia == "duplicatas":
        return [rng.randint(-50, 50) for _ in range(n)]
    if familia == "quase_ordenada":
        valores = list(range(n))
        for _ in range(max(1, n // 100)):
            i, j = rng.sample(range(n), 2)
            valores[i], valores[j] = valores[j], valores[i]
        return valores
    if familia.startswith("trocas_"):
        trocas = int(familia.split("_")[1])
        valores = list(range(n))
        for _ in range(trocas):
            i, j = rng.sample(range(n), 2)
            valores[i], valores[j] = valores[j], valores[i]
        return valores
    raise ValueError(f"Família desconhecida: {familia}")


def calibrar_insercao(linhas):
    tamanhos = [16, 24, 32, 48, 64]
    familias_por_tamanho = ["aleatoria_ampla", "duplicatas", "quase_ordenada"]
    resumo = {}
    for n in tamanhos:
        tempos = {"insercao": [], "hibrida": []}
        for idx, familia in enumerate(familias_por_tamanho):
            for rep in range(1, 6):
                seed = SEMENTE_BASE + n * 10 + idx * 1000 + rep
                entrada = _gerar(familia, n, seed)
                for metodo, funcao in (("insercao", insercao), ("hibrida", hibrida)):
                    mediana = _medir(funcao, entrada, repeticoes=3)
                    tempos[metodo].append(mediana)
                    linhas.append({"criterio": "tamanho_insercao", "tamanho": n,
                                   "familia": familia, "repeticao": rep, "seed": seed,
                                   "candidato": metodo, "mediana_s": f"{mediana:.9f}",
                                   "valor_auxiliar": ""})
        resumo[n] = {metodo: statistics.median(valores) for metodo, valores in tempos.items()}
    elegiveis = [n for n, tempos in resumo.items() if tempos["insercao"] <= tempos["hibrida"]]
    limite = max(elegiveis) if elegiveis else min(tamanhos)
    return limite, resumo


def calibrar_descidas(linhas):
    n = 5000
    limites = [0, 1, 2, 4, 8, 12]
    familias = ["trocas_0", "trocas_5", "trocas_10", "trocas_20", "trocas_50",
                "trocas_100", "trocas_200", "aleatoria_ampla"]
    conjuntos = []
    for idx, familia in enumerate(familias):
        for rep in range(1, 4):
            seed = SEMENTE_BASE + 200_000 + idx * 1000 + rep
            entrada = _gerar(familia, n, seed)
            indices = _indices_amostra(n, 256)
            descidas = sum(1 for i in indices if entrada[i] > entrada[i + 1])
            tempo_hibrida = _medir(hibrida, entrada, repeticoes=3)
            tempo_insercao = None
            if descidas <= max(limites):
                tempo_insercao = _medir(insercao, entrada, repeticoes=3)
            tempo_escolha = []
            for _ in range(5):
                inicio = time.perf_counter()
                # Mede a varredura de pares amostrados que a regra de descidas exige.
                sum(1 for i in indices if entrada[i] > entrada[i + 1])
                tempo_escolha.append(time.perf_counter() - inicio)
            conjuntos.append({"familia": familia, "seed": seed, "descidas": descidas,
                              "tempo_hibrida": tempo_hibrida, "tempo_insercao": tempo_insercao,
                              "tempo_escolha": statistics.median(tempo_escolha)})

    custos = {}
    for limite in limites:
        custo_total = 0.0
        for caso in conjuntos:
            if caso["descidas"] <= limite and caso["tempo_insercao"] is not None:
                custo_total += caso["tempo_insercao"] + caso["tempo_escolha"]
                metodo = "insercao"
                custo = caso["tempo_insercao"]
            else:
                custo_total += caso["tempo_hibrida"] + caso["tempo_escolha"]
                metodo = "hibrida"
                custo = caso["tempo_hibrida"]
            linhas.append({"criterio": "max_descidas", "tamanho": n,
                           "familia": caso["familia"], "repeticao": 1, "seed": caso["seed"],
                           "candidato": limite, "mediana_s": f"{custo:.9f}",
                           "valor_auxiliar": f"descidas={caso['descidas']};escolhido={metodo};custo_agregado_parcial={custo_total:.9f}"})
        custos[limite] = custo_total
    melhor = min(custos, key=custos.get)
    return melhor, custos


def calibrar_contagem(linhas):
    razoes = [0.1, 0.25, 0.5, 1.0, 2.0, 4.0]
    tamanhos = [2000, 5000, 10000]
    resumo = {}
    for razao in razoes:
        resumo[razao] = {}
        for n in tamanhos:
            tempos_contagem, tempos_hibrida = [], []
            for rep in range(1, 5):
                seed = SEMENTE_BASE + 400_000 + int(razao * 1000) * 100 + n + rep
                rng = random.Random(seed)
                meia_faixa = max(1, round(n * razao / 2))
                entrada = [rng.randint(-meia_faixa, meia_faixa) for _ in range(n)]
                amplitude = max(entrada) - min(entrada) + 1
                tc = _medir(contagem, entrada, repeticoes=3)
                th = _medir(hibrida, entrada, repeticoes=3)
                tempos_contagem.append(tc)
                tempos_hibrida.append(th)
                linhas.append({"criterio": "razao_amplitude_contagem", "tamanho": n,
                               "familia": f"razao_{razao}", "repeticao": rep, "seed": seed,
                               "candidato": razao, "mediana_s": f"{tc:.9f}",
                               "valor_auxiliar": f"amplitude={amplitude};hibrida_s={th:.9f}"})
            resumo[razao][n] = (statistics.median(tempos_contagem), statistics.median(tempos_hibrida))
    elegiveis = [razao for razao in razoes
                 if all(resumo[razao][n][0] < resumo[razao][n][1] for n in tamanhos)]
    fator = max(elegiveis) if elegiveis else min(razoes)
    return fator, resumo


def main():
    linhas = []
    limite_insercao, resumo_tamanho = calibrar_insercao(linhas)
    limite_descidas, custos_descidas = calibrar_descidas(linhas)
    fator_contagem, resumo_contagem = calibrar_contagem(linhas)
    destino = PASTA / "calibracao_seletor.csv"
    with destino.open("w", newline="", encoding="utf-8") as arquivo:
        campos = ["criterio", "tamanho", "familia", "repeticao", "seed", "candidato", "mediana_s", "valor_auxiliar"]
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)
    print("Calibração do seletor — dados independentes dos cenários finais")
    print("Tamanho | mediana agregada inserção | mediana agregada híbrida")
    for n, resumo in resumo_tamanho.items():
        print(f"{n:>7} | {resumo['insercao']:.8f} s | {resumo['hibrida']:.8f} s")
    print(f"Limite de tamanho selecionado: {limite_insercao}")
    print("Descidas amostradas | custo agregado medido")
    for limite in sorted(custos_descidas):
        print(f"{limite:>18} | {custos_descidas[limite]:.6f} s")
    print(f"Limite de descidas selecionado: {limite_descidas}")
    print("Razão amplitude/n | contagem vs híbrida (medianas por tamanho)")
    for razao, resumo in resumo_contagem.items():
        detalhe = ", ".join(f"n={n}: {v[0]:.5f}/{v[1]:.5f}s" for n, v in resumo.items())
        print(f"{razao:>6}: {detalhe}")
    print(f"Fator de amplitude selecionado: {fator_contagem}")
    print(f"Dados de calibração gravados em: {destino}")
    print("LIMITES_SELECIONADOS=" + repr({
        "TAMANHO_MAXIMO_INSERCAO": limite_insercao,
        "MAX_DESCIDAS_PARA_INSERCAO": limite_descidas,
        "FATOR_AMPLITUDE_CONTAGEM": fator_contagem,
    }))


if __name__ == "__main__":
    main()
