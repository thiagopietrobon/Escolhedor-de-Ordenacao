"""Calibração em dados separados dos cenários finais de avaliação."""
from __future__ import annotations

import csv
import random
import statistics
import time
from pathlib import Path

from algoritmos import hibrida, rapida

RAIZ = Path(__file__).resolve().parent
ARQUIVO_CALIBRACAO = RAIZ / "resultados" / "calibracao_hibrido.csv"
CORTES_CANDIDATOS = [8, 12, 16, 24, 32, 48, 64]
TAMANHOS = [1500, 6000]
REPETICOES = 5
SEMENTE_BASE = 84_271


def gerar_entrada(familia: str, n: int, seed: int) -> list[int]:
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
    raise ValueError(f"Família desconhecida: {familia}")


def executar_calibracao() -> tuple[int, list[dict[str, object]]]:
    familias = ["aleatoria_ampla", "duplicatas", "quase_ordenada"]
    linhas: list[dict[str, object]] = []
    resumo: dict[int, list[float]] = {corte: [] for corte in CORTES_CANDIDATOS}

    # Baralha a ordem dos candidatos em cada combinação para reduzir viés de ordem.
    for familia in familias:
        for n in TAMANHOS:
            for repeticao in range(1, REPETICOES + 1):
                seed_dados = SEMENTE_BASE + n + repeticao + familias.index(familia) * 100_000
                entrada = gerar_entrada(familia, n, seed_dados)
                ordem = CORTES_CANDIDATOS.copy()
                random.Random(seed_dados + 444).shuffle(ordem)
                for corte in ordem:
                    inicio = time.perf_counter()
                    saida = hibrida(entrada.copy(), limite=corte, seed=seed_dados + repeticao)
                    decorrido = time.perf_counter() - inicio
                    if saida != sorted(entrada):
                        raise RuntimeError(f"Resultado incorreto durante calibração: {familia}, corte={corte}")
                    resumo[corte].append(decorrido)
                    linhas.append({
                        "familia": familia,
                        "tamanho": n,
                        "repeticao": repeticao,
                        "seed_dados": seed_dados,
                        "seed_algoritmo": seed_dados + repeticao,
                        "limite_hibrido": corte,
                        "tempo_s": f"{decorrido:.9f}",
                    })

    # Inclui Quick Sort como referência adicional, mas não confunde seu tempo com
    # os resultados dos diferentes limites híbridos.
    for familia in familias:
        for n in TAMANHOS:
            for repeticao in range(1, REPETICOES + 1):
                seed_dados = SEMENTE_BASE + n + repeticao + familias.index(familia) * 100_000
                entrada = gerar_entrada(familia, n, seed_dados)
                seed_algoritmo = seed_dados + repeticao
                inicio = time.perf_counter()
                saida = rapida(entrada.copy(), seed=seed_algoritmo)
                decorrido = time.perf_counter() - inicio
                if saida != sorted(entrada):
                    raise RuntimeError("Resultado incorreto no Quick Sort de referência da calibração")
                linhas.append({
                    "familia": familia,
                    "tamanho": n,
                    "repeticao": repeticao,
                    "seed_dados": seed_dados,
                    "seed_algoritmo": seed_algoritmo,
                    "limite_hibrido": "rapida_referencia",
                    "tempo_s": f"{decorrido:.9f}",
                })

    ARQUIVO_CALIBRACAO.parent.mkdir(parents=True, exist_ok=True)
    campos = ["familia", "tamanho", "repeticao", "seed_dados", "seed_algoritmo", "limite_hibrido", "tempo_s"]
    with ARQUIVO_CALIBRACAO.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)

    medianas = {corte: statistics.median(tempos) for corte, tempos in resumo.items()}
    melhor = min(medianas, key=medianas.get)
    print("Calibração do limite híbrido — dados separados da avaliação final")
    for corte in CORTES_CANDIDATOS:
        print(f"limite={corte:>2}: mediana agregada={medianas[corte]:.6f} s")
    print(f"Limite selecionado pela menor mediana agregada: {melhor}")
    print(f"Registros gravados em: {ARQUIVO_CALIBRACAO}")
    return melhor, linhas


if __name__ == "__main__":
    executar_calibracao()
