"""Geração de cenários, medições reproduzíveis, CSV e busca adversarial."""

from __future__ import annotations

import csv
import math
import multiprocessing
import os
import platform
import random
import signal
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from threading import current_thread, main_thread
from typing import Any

from algoritmos import (
    MAX_AMPLITUDE_CONTAGEM,
    MAX_MEMORIA_AUXILIAR_CONTAGEM,
    LIMITE_HIBRIDO,
    LimiteContagemExcedido,
    executar_metodo,
)
from seletor import escolher, ordenar

RAIZ = Path(__file__).resolve().parent
PASTA_RESULTADOS = RAIZ / "resultados"
ARQUIVO_RESULTADOS = PASTA_RESULTADOS / "resultados.csv"
ARQUIVO_ADVERSARIAL = PASTA_RESULTADOS / "resultados_adversarial.csv"
ARQUIVO_BUSCA = PASTA_RESULTADOS / "busca_adversarial.csv"
REPETICOES = 15


def _obter_timeout() -> float:
    texto = os.environ.get("ORDENACAO_TIMEOUT_S", "60")
    try:
        timeout = float(texto)
    except ValueError as erro:
        raise ValueError("ORDENACAO_TIMEOUT_S deve ser um número positivo.") from erro
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("ORDENACAO_TIMEOUT_S deve ser um número positivo.")
    return timeout


TEMPO_LIMITE_SEGUNDOS = _obter_timeout()
METODOS_FIXOS = ["insercao", "intercalacao", "rapida", "hibrida", "contagem", "base"]
ALTERNATIVAS = METODOS_FIXOS + ["ordenar"]
CAMPOS = [
    "cenario",
    "metodo",
    "repeticao",
    "tempo_ordenacao_s",
    "tempo_selecao_s",
    "tempo_total_s",
    "tamanho_entrada",
    "seed_dados",
    "seed_algoritmo",
    "parametros",
    "metodo_escolhido",
    "status",
    "erro",
    "python",
    "sistema_operacional",
]


class TempoEsgotado(Exception):
    """Execução interrompida por ultrapassar o limite configurado."""


def _gerar_cenarios() -> dict[str, dict[str, Any]]:
    cenarios: dict[str, dict[str, Any]] = {}

    seed_a = 41001
    rng_a = random.Random(seed_a)
    cenarios["A_aleatoria_ampla"] = {
        "valores": [
            rng_a.randint(-1_000_000_000, 1_000_000_000) for _ in range(10_000)
        ],
        "seed_dados": seed_a,
        "descricao": "10.000 inteiros uniformes entre -1.000.000.000 e 1.000.000.000",
        "parametros": "distribuicao=uniforme;min=-1000000000;max=1000000000;seed=41001",
    }

    seed_b = 42002
    rng_b = random.Random(seed_b)
    cenarios["B_faixa_estreita"] = {
        "valores": [rng_b.randint(-50, 50) for _ in range(10_000)],
        "seed_dados": seed_b,
        "descricao": "10.000 inteiros uniformes entre -50 e 50, com duplicatas",
        "parametros": "distribuicao=uniforme;min=-50;max=50;seed=42002",
    }

    seed_c = 43003
    rng_c = random.Random(seed_c)
    valores_c = list(range(10_000))
    for _ in range(100):
        i, j = rng_c.sample(range(len(valores_c)), 2)
        valores_c[i], valores_c[j] = valores_c[j], valores_c[i]
    cenarios["C_quase_ordenada"] = {
        "valores": valores_c,
        "seed_dados": seed_c,
        "descricao": "10.000 valores inicialmente ordenados e 100 trocas de posições",
        "parametros": "base=range(10000);100_trocas;pares_distintos_por_troca;posicoes_podem_reaparecer;seed=43003",
    }

    seed_d = 44004
    rng_d = random.Random(seed_d)
    cenarios["D_pequena"] = {
        "valores": [rng_d.randint(-1000, 1000) for _ in range(20)],
        "seed_dados": seed_d,
        "descricao": "20 inteiros uniformes entre -1.000 e 1.000",
        "parametros": "distribuicao=uniforme;min=-1000;max=1000;seed=44004",
    }
    return cenarios


def _trabalho_medido(
    nome: str,
    valores: list[int],
    seed: int,
    limite_hibrido: int,
) -> tuple[str, float | None, list[int] | None, str]:
    """Executa o algoritmo e classifica corretamente o resultado."""
    inicio = time.perf_counter()

    try:
        if nome == "ordenar":
            resultado = ordenar(valores, seed=seed)
        else:
            resultado = executar_metodo(
                nome,
                valores,
                seed=seed,
                limite_hibrido=limite_hibrido,
            )

        return "concluida", time.perf_counter() - inicio, resultado, ""

    except LimiteContagemExcedido as erro:
        return (
            "recusada_limite",
            time.perf_counter() - inicio,
            None,
            str(erro),
        )

    except TempoEsgotado:
        raise

    except Exception as erro:
        return (
            "erro",
            time.perf_counter() - inicio,
            None,
            f"{type(erro).__name__}: {erro}",
        )


def _worker_processo(
    conexao: Any, nome: str, valores: list[int], seed: int, limite_hibrido: int
) -> None:
    try:
        conexao.send(_trabalho_medido(nome, valores, seed, limite_hibrido))
    finally:
        conexao.close()


def _executar_com_limite(
    nome: str, valores: list[int], seed: int
) -> tuple[str, float | None, list[int] | None, str]:
    """Executa com timeout individual; no POSIX usa alarme sem criar subprocesso."""
    if (
        os.name == "posix"
        and hasattr(signal, "setitimer")
        and current_thread() is main_thread()
    ):

        def interromper(_sinal: int, _quadro: Any) -> None:
            raise TempoEsgotado(
                f"Execução excedeu o limite de {TEMPO_LIMITE_SEGUNDOS:g} segundos"
            )

        handler_anterior = signal.signal(signal.SIGALRM, interromper)
        alarme_anterior = signal.setitimer(signal.ITIMER_REAL, TEMPO_LIMITE_SEGUNDOS)
        try:
            return _trabalho_medido(nome, valores, seed, LIMITE_HIBRIDO)
        except TempoEsgotado as erro:
            return "interrompida", None, None, str(erro)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, handler_anterior)
            if alarme_anterior[0] > 0:
                signal.setitimer(signal.ITIMER_REAL, *alarme_anterior)

    # Fallback compatível com Windows: o relógio fica dentro do processo filho,
    # enquanto o processo pai aplica o timeout e encerra a execução se necessário.
    contexto = multiprocessing.get_context("spawn")
    conexao_pai, conexao_filho = contexto.Pipe(duplex=False)
    processo = contexto.Process(
        target=_worker_processo,
        args=(conexao_filho, nome, valores, seed, LIMITE_HIBRIDO),
    )
    processo.start()
    conexao_filho.close()
    recebeu_dados = conexao_pai.poll(TEMPO_LIMITE_SEGUNDOS)

    if not recebeu_dados:
        if processo.is_alive():
            processo.terminate()
            processo.join()
            conexao_pai.close()
            return (
                "interrompida",
                None,
                None,
                f"Execução excedeu o limite de "
                f"{TEMPO_LIMITE_SEGUNDOS:g} segundos",
            )

        processo.join()

    try:
        resultado = conexao_pai.recv()
    except (EOFError, OSError) as erro:
        processo.join()
        resultado = (
            "erro",
            None,
            None,
            "O processo filho terminou sem enviar um resultado "
            f"(código de saída {processo.exitcode}). "
            f"Detalhe: {erro}",
        )
    finally:
        conexao_pai.close()

    processo.join()
    return resultado


def _medir_escolha(valores: list[int]) -> float:
    inicio = time.perf_counter()
    escolher(valores)
    return time.perf_counter() - inicio


def _linha(
    cenario: str,
    metodo: str,
    repeticao: int,
    seed_dados: int,
    seed_algoritmo: int,
    parametros: str,
    escolhido: str = "",
) -> dict[str, Any]:
    return {
        "cenario": cenario,
        "metodo": metodo,
        "repeticao": repeticao,
        "tempo_ordenacao_s": "",
        "tempo_selecao_s": "",
        "tempo_total_s": "",
        "tamanho_entrada": "",
        "seed_dados": seed_dados,
        "seed_algoritmo": seed_algoritmo,
        "parametros": parametros,
        "metodo_escolhido": escolhido,
        "status": "pendente",
        "erro": "",
        "python": platform.python_version(),
        "sistema_operacional": platform.platform(),
    }


def _salvar_csv(caminho: Path, linhas: list[dict[str, Any]]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(linhas)


def executar_experimentos() -> list[dict[str, Any]]:
    # Os testes são uma barreira obrigatória antes de medir os cenários finais.
    validacao = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-v"],
        cwd=RAIZ,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    print(validacao.stdout)
    if validacao.returncode != 0:
        raise RuntimeError(
            "A suíte de testes falhou; os experimentos finais não foram iniciados."
        )

    cenarios = _gerar_cenarios()
    linhas: list[dict[str, Any]] = []
    referencia_sort = sorted
    for indice_cenario, (nome_cenario, info) in enumerate(cenarios.items()):
        referencia = info["valores"]
        esperado = referencia_sort(referencia)
        print(f"\nCenário {nome_cenario}: {info['descricao']}")
        for repeticao in range(1, REPETICOES + 1):
            ordem = ALTERNATIVAS.copy()
            random.Random(71000 + indice_cenario * 100 + repeticao).shuffle(ordem)
            seed_algoritmo = 80000 + indice_cenario * 1000 + repeticao
            for metodo in ordem:
                escolhido = (
                    escolher(referencia)
                    if metodo == "ordenar" and len(referencia) > 1
                    else ""
                )
                registro = _linha(
                    nome_cenario,
                    metodo,
                    repeticao,
                    info["seed_dados"],
                    seed_algoritmo if metodo in ("rapida", "hibrida", "ordenar") else 0,
                    info["parametros"]
                    + f";limite_execucao_s={TEMPO_LIMITE_SEGUNDOS:g};limite_contagem={MAX_AMPLITUDE_CONTAGEM};memoria_contagem={MAX_MEMORIA_AUXILIAR_CONTAGEM};limite_hibrido={LIMITE_HIBRIDO}",
                    escolhido,
                )
                registro["tamanho_entrada"] = len(referencia)
                if metodo == "ordenar":
                    registro["tempo_selecao_s"] = (
                        f"{_medir_escolha(referencia.copy()):.9f}"
                    )
                status, decorrido, resultado, erro = _executar_com_limite(
                    metodo, referencia.copy(), seed_algoritmo
                )
                if status == "concluida":
                    if resultado != esperado:
                        raise RuntimeError(
                            f"Resultado incorreto: {nome_cenario}/{metodo}/{repeticao}"
                        )
                    if metodo == "ordenar":
                        registro["tempo_total_s"] = f"{decorrido:.9f}"
                    else:
                        registro["tempo_ordenacao_s"] = f"{decorrido:.9f}"
                        registro["tempo_total_s"] = f"{decorrido:.9f}"
                registro["status"] = status
                registro["erro"] = erro
                linhas.append(registro)
                if registro["status"] != "concluida":
                    print(
                        f"  {metodo:12} repetição {repeticao:2}: {registro['status']} — {registro['erro']}"
                    )
        _salvar_csv(ARQUIVO_RESULTADOS, linhas)
        print(f"CSV atualizado: {ARQUIVO_RESULTADOS}")
    print(
        f"\nMedições principais gravadas: {len(linhas)} linhas em {ARQUIVO_RESULTADOS}"
    )
    return linhas


def _gerar_adversarial(seed: int, n: int = 10_000, trocas: int = 100) -> list[int]:
    valores = list(range(n))
    rng = random.Random(seed)
    for _ in range(trocas):
        i, j = rng.sample(range(n), 2)
        valores[i], valores[j] = valores[j], valores[i]
    return valores


def buscar_caso_adversarial() -> tuple[int, list[int], list[dict[str, Any]]]:
    """Busca por sementes em ordem fixa e grava cada tentativa antes de parar."""
    tentativas: list[dict[str, Any]] = []
    seed_inicial = 50000
    max_sementes = 80
    confirmacoes = 5
    encontrado: tuple[int, list[int]] | None = None
    for offset in range(max_sementes):
        seed = seed_inicial + offset
        entrada = _gerar_adversarial(seed)
        escolhido = escolher(entrada)
        medianas: dict[str, float] = {}
        for metodo in METODOS_FIXOS:
            tempos = []
            for repeticao in range(1, confirmacoes + 1):
                status, tempo_s, resultado, erro = _executar_com_limite(
                    metodo, entrada.copy(), seed + repeticao
                )
                if status != "concluida" or resultado != sorted(entrada):
                    continue
                tempos.append(float(tempo_s))
            if len(tempos) == confirmacoes:
                medianas[metodo] = statistics.median(tempos)
        mediana_escolhido = medianas.get(escolhido)
        menor_metodo = min(medianas, key=medianas.get) if medianas else ""
        menor_tempo = medianas.get(menor_metodo)
        falha = bool(
            mediana_escolhido is not None
            and menor_tempo is not None
            and menor_metodo != escolhido
            and menor_tempo < mediana_escolhido
        )
        tentativas.append(
            {
                "seed": seed,
                "tamanho": len(entrada),
                "trocas": 100,
                "metodo_escolhido": escolhido,
                "mediana_metodo_escolhido_s": f"{mediana_escolhido:.9f}"
                if mediana_escolhido is not None
                else "",
                "metodo_mais_rapido_na_busca": menor_metodo,
                "menor_mediana_s": f"{menor_tempo:.9f}"
                if menor_tempo is not None
                else "",
                "tentativa_confirmada": str(falha).lower(),
                "medianas_metodos_s": ";".join(
                    f"{k}:{v:.9f}" for k, v in sorted(medianas.items())
                ),
            }
        )
        _salvar_busca(tentativas)
        if falha:
            encontrado = (seed, entrada)
            print(
                f"Caso adversarial encontrado: seed={seed}; seletor={escolhido}; mais rápido preliminar={menor_metodo}"
            )
            break
        print(
            f"Busca adversarial: seed={seed}, seletor={escolhido}, sem falha confirmada nesta tentativa."
        )

    if encontrado is None:
        print(
            f"Nenhum caso foi confirmado nas {max_sementes} sementes; a busca fica documentada em {ARQUIVO_BUSCA}."
        )
        return -1, [], tentativas
    return encontrado[0], encontrado[1], tentativas


def _salvar_busca(linhas: list[dict[str, Any]]) -> None:
    caminho = ARQUIVO_BUSCA
    caminho.parent.mkdir(parents=True, exist_ok=True)
    campos = [
        "seed",
        "tamanho",
        "trocas",
        "metodo_escolhido",
        "mediana_metodo_escolhido_s",
        "metodo_mais_rapido_na_busca",
        "menor_mediana_s",
        "tentativa_confirmada",
        "medianas_metodos_s",
    ]
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(linhas)


def executar_experimento_adversarial() -> list[dict[str, Any]]:
    seed, entrada, tentativas = buscar_caso_adversarial()
    if seed < 0:
        return []
    resultado_esperado = sorted(entrada)
    metodo_escolhido = escolher(entrada)
    parametros = f"base=range(10000);100_trocas;seed={seed};busca_sequencial_iniciada=50000;limite_sementes=80;confirmacao_busca=5"
    linhas: list[dict[str, Any]] = []
    for repeticao in range(1, REPETICOES + 1):
        ordem = ALTERNATIVAS.copy()
        random.Random(99000 + repeticao).shuffle(ordem)
        seed_algoritmo = seed + repeticao
        for metodo in ordem:
            registro = _linha(
                "E_adversarial",
                metodo,
                repeticao,
                seed,
                seed_algoritmo,
                parametros,
                metodo_escolhido,
            )
            registro["tamanho_entrada"] = len(entrada)
            if metodo == "ordenar":
                registro["tempo_selecao_s"] = f"{_medir_escolha(entrada.copy()):.9f}"
            estado, decorrido, resultado, erro = _executar_com_limite(
                metodo, entrada.copy(), seed_algoritmo
            )
            if estado == "concluida":
                if resultado != resultado_esperado:
                    raise RuntimeError(
                        f"Resultado incorreto no caso adversarial: {metodo}/{repeticao}"
                    )
                if metodo == "ordenar":
                    registro["tempo_total_s"] = f"{decorrido:.9f}"
                else:
                    registro["tempo_ordenacao_s"] = f"{decorrido:.9f}"
                    registro["tempo_total_s"] = f"{decorrido:.9f}"
            registro["status"] = estado
            registro["erro"] = erro
            linhas.append(registro)
    _salvar_csv(ARQUIVO_ADVERSARIAL, linhas)
    print(f"Registros adversariais gravados: {len(linhas)} em {ARQUIVO_ADVERSARIAL}")
    return linhas


if __name__ == "__main__":
    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    if "--adversarial" in sys.argv:
        executar_experimento_adversarial()
    else:
        executar_experimentos()
        executar_experimento_adversarial()
