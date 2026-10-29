"""Seletor automático e função pública de ordenação."""

from __future__ import annotations

import sys

from algoritmos import (
    BYTES_ESTIMADOS_POR_CONTAGEM,
    LIMITE_HIBRIDO,
    MAX_AMPLITUDE_CONTAGEM,
    MAX_MEMORIA_AUXILIAR_CONTAGEM,
    METODOS,
    _validar_limites_contagem,
    hibrida,
)

# Critérios iniciais calibrados separadamente dos quatro cenários finais.
TAMANHO_MAXIMO_INSERCAO = 32
NUMERO_AMOSTRAS = 256
MAX_DESCIDAS_PARA_INSERCAO = 2
AMPLITUDE_AMOSTRA_CANDIDATA = 4096
FATOR_AMPLITUDE_CONTAGEM = 4.0


def _indices_amostra(n: int, quantidade: int) -> list[int]:
    if n <= 1:
        return []
    total = min(n - 1, quantidade)
    if total == 1:
        return [0]
    return sorted({(i * (n - 2)) // (total - 1) for i in range(total)})


def escolher(v: list[int]) -> str:
    """Escolhe um dos seis métodos sem executar a ordenação completa.

    A amostra é determinística: observa pares adjacentes espalhados pela lista.
    Counting Sort só é escolhido depois de confirmar a amplitude exata e os
    limites de segurança na entrada completa.
    """
    n = len(v)
    if n <= TAMANHO_MAXIMO_INSERCAO:
        return "insercao"

    indices = _indices_amostra(n, NUMERO_AMOSTRAS)
    descidas = sum(1 for i in indices if v[i] > v[i + 1])
    minimo_amostra = min(v[i] for i in indices) if indices else 0
    maximo_amostra = max(v[i] for i in indices) if indices else 0
    amplitude_amostra = maximo_amostra - minimo_amostra + 1

    # A amostra somente sugere que a contagem pode valer a pena; a faixa real
    # é calculada sobre toda a lista antes de tomar a decisão.
    if amplitude_amostra <= AMPLITUDE_AMOSTRA_CANDIDATA:
        minimo = min(v)
        maximo = max(v)
        amplitude = maximo - minimo + 1
        memoria_estimada = sys.getsizeof([]) + amplitude * BYTES_ESTIMADOS_POR_CONTAGEM
        teto_por_tamanho = max(256, int(n * FATOR_AMPLITUDE_CONTAGEM))
        if (
            amplitude <= teto_por_tamanho
            and amplitude <= MAX_AMPLITUDE_CONTAGEM
            and memoria_estimada <= MAX_MEMORIA_AUXILIAR_CONTAGEM
        ):
            try:
                _validar_limites_contagem(
                    amplitude,
                    MAX_AMPLITUDE_CONTAGEM,
                    MAX_MEMORIA_AUXILIAR_CONTAGEM,
                )
            except ValueError:
                pass
            else:
                return "contagem"

    # A amostra é apenas um sinal, não uma garantia de que toda a lista esteja
    # quase ordenada. Esse critério foi mantido simples e mensurável.
    if descidas <= MAX_DESCIDAS_PARA_INSERCAO:
        return "insercao"

    # Fallback geral quando não há evidência suficiente para especializar.
    return "hibrida"


def ordenar(v: list[int], seed: int = 0) -> list[int]:
    """Ordena por decisão automática e retorna uma nova lista crescente.

    A semente é repassada ao método híbrido caso ele seja selecionado.
    """
    if len(v) <= 1:
        return list(v)
    metodo = escolher(v)
    if metodo == "hibrida":
        return hibrida(v, limite=LIMITE_HIBRIDO, seed=seed)
    return METODOS[metodo](v)
