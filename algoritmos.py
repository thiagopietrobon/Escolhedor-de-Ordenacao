"""Seis algoritmos de ordenação implementados com a biblioteca padrão."""
from __future__ import annotations

import random
import sys
from typing import Iterable

# Limites conservadores para o vetor de frequências do Counting Sort.
# A estimativa usa aproximadamente 36 bytes por posição (referência + inteiro),
# além do cabeçalho da lista. É uma estimativa de segurança, não um medidor exato.
MAX_AMPLITUDE_CONTAGEM = 500_000
MAX_MEMORIA_AUXILIAR_CONTAGEM = 32 * 1024 * 1024
BYTES_ESTIMADOS_POR_CONTAGEM = 36

# Será confirmado pela calibração em dados que não fazem parte dos cenários finais.
LIMITE_HIBRIDO = 24


def _validar_limites_contagem(amplitude: int, max_amplitude: int,
                              max_memoria_bytes: int) -> None:
    memoria_estimada = sys.getsizeof([]) + amplitude * BYTES_ESTIMADOS_POR_CONTAGEM
    if amplitude > max_amplitude:
        raise ValueError(
            f"Counting Sort recusado: amplitude {amplitude:,} excede o limite "
            f"configurado de {max_amplitude:,}."
        )
    if memoria_estimada > max_memoria_bytes:
        raise ValueError(
            "Counting Sort recusado: memória auxiliar estimada de "
            f"{memoria_estimada:,} bytes excede o limite configurado de "
            f"{max_memoria_bytes:,} bytes."
        )


def insercao(valores: list[int]) -> list[int]:
    """Insertion Sort estável; devolve uma nova lista e preserva a entrada."""
    resultado = list(valores)
    for i in range(1, len(resultado)):
        atual = resultado[i]
        j = i - 1
        while j >= 0 and resultado[j] > atual:
            resultado[j + 1] = resultado[j]
            j -= 1
        resultado[j + 1] = atual
    return resultado


def intercalacao(valores: list[int]) -> list[int]:
    """Merge Sort estável, com complexidade O(n log n) e memória auxiliar O(n)."""
    resultado = list(valores)
    if len(resultado) < 2:
        return resultado

    def ordenar_intervalo(inicio: int, fim: int) -> None:
        if fim - inicio <= 1:
            return
        meio = (inicio + fim) // 2
        ordenar_intervalo(inicio, meio)
        ordenar_intervalo(meio, fim)
        esquerda = resultado[inicio:meio]
        direita = resultado[meio:fim]
        i = j = 0
        k = inicio
        while i < len(esquerda) and j < len(direita):
            if esquerda[i] <= direita[j]:
                resultado[k] = esquerda[i]
                i += 1
            else:
                resultado[k] = direita[j]
                j += 1
            k += 1
        while i < len(esquerda):
            resultado[k] = esquerda[i]
            i += 1
            k += 1
        while j < len(direita):
            resultado[k] = direita[j]
            j += 1
            k += 1

    ordenar_intervalo(0, len(resultado))
    return resultado


def _particionar_tres_vias(valores: list[int], inicio: int, fim: int,
                            pivô: int) -> tuple[int, int]:
    """Particiona intervalo inclusivo em valores <, == e > pivô."""
    menor = atual = inicio
    maior = fim
    while atual <= maior:
        if valores[atual] < pivô:
            valores[menor], valores[atual] = valores[atual], valores[menor]
            menor += 1
            atual += 1
        elif valores[atual] > pivô:
            valores[atual], valores[maior] = valores[maior], valores[atual]
            maior -= 1
        else:
            atual += 1
    return menor, maior


def rapida(valores: list[int], seed: int = 0) -> list[int]:
    """Quick Sort iterativo com pivô aleatório; não é estável."""
    resultado = list(valores)
    if len(resultado) < 2:
        return resultado
    rng = random.Random(seed)
    pilha = [(0, len(resultado) - 1)]
    while pilha:
        inicio, fim = pilha.pop()
        while inicio < fim:
            pivo = resultado[rng.randint(inicio, fim)]
            igual_inicio, igual_fim = _particionar_tres_vias(
                resultado, inicio, fim, pivo
            )
            esquerda = (inicio, igual_inicio - 1)
            direita = (igual_fim + 1, fim)
            # Processa primeiro o intervalo menor para limitar o tamanho da pilha.
            tam_esq = esquerda[1] - esquerda[0]
            tam_dir = direita[1] - direita[0]
            if tam_esq < tam_dir:
                if direita[0] < direita[1]:
                    pilha.append(direita)
                inicio, fim = esquerda
            else:
                if esquerda[0] < esquerda[1]:
                    pilha.append(esquerda)
                inicio, fim = direita
    return resultado


def _insercao_intervalo(valores: list[int], inicio: int, fim: int) -> None:
    """Insertion Sort no intervalo inclusivo fornecido."""
    for i in range(inicio + 1, fim + 1):
        atual = valores[i]
        j = i - 1
        while j >= inicio and valores[j] > atual:
            valores[j + 1] = valores[j]
            j -= 1
        valores[j + 1] = atual


def hibrida(valores: list[int], limite: int = LIMITE_HIBRIDO,
            seed: int = 0) -> list[int]:
    """Quick Sort nas partições grandes e Insertion Sort nas pequenas."""
    if limite < 1:
        raise ValueError("O limite do algoritmo híbrido deve ser pelo menos 1.")
    resultado = list(valores)
    if len(resultado) < 2:
        return resultado
    rng = random.Random(seed)
    pilha = [(0, len(resultado) - 1)]
    while pilha:
        inicio, fim = pilha.pop()
        while fim - inicio + 1 > limite:
            pivo = resultado[rng.randint(inicio, fim)]
            igual_inicio, igual_fim = _particionar_tres_vias(
                resultado, inicio, fim, pivo
            )
            esquerda = (inicio, igual_inicio - 1)
            direita = (igual_fim + 1, fim)
            tam_esq = esquerda[1] - esquerda[0]
            tam_dir = direita[1] - direita[0]
            if tam_esq < tam_dir:
                if direita[0] < direita[1]:
                    pilha.append(direita)
                inicio, fim = esquerda
            else:
                if esquerda[0] < esquerda[1]:
                    pilha.append(esquerda)
                inicio, fim = direita
        if inicio < fim:
            _insercao_intervalo(resultado, inicio, fim)
    return resultado


def contagem(valores: list[int],
             max_amplitude: int = MAX_AMPLITUDE_CONTAGEM,
             max_memoria_bytes: int = MAX_MEMORIA_AUXILIAR_CONTAGEM) -> list[int]:
    """Counting Sort estável, incluindo negativos; recusa amplitude insegura."""
    if not valores:
        return []
    minimo = min(valores)
    maximo = max(valores)
    amplitude = maximo - minimo + 1
    _validar_limites_contagem(amplitude, max_amplitude, max_memoria_bytes)

    frequencias = [0] * amplitude
    for valor in valores:
        frequencias[valor - minimo] += 1
    # Acumula as posições finais para permitir a construção estável.
    for i in range(1, amplitude):
        frequencias[i] += frequencias[i - 1]
    resultado = [0] * len(valores)
    for valor in reversed(valores):
        indice = valor - minimo
        frequencias[indice] -= 1
        resultado[frequencias[indice]] = valor
    return resultado


def _radix_nao_negativos(valores: list[int], base: int = 256) -> list[int]:
    """LSD Radix Sort estável para inteiros não negativos."""
    resultado = list(valores)
    if len(resultado) < 2:
        return resultado
    maior = max(resultado)
    expoente = 1
    while maior // expoente > 0:
        contagens = [0] * base
        for valor in resultado:
            digito = (valor // expoente) % base
            contagens[digito] += 1
        for i in range(1, base):
            contagens[i] += contagens[i - 1]
        saida = [0] * len(resultado)
        for valor in reversed(resultado):
            digito = (valor // expoente) % base
            contagens[digito] -= 1
            saida[contagens[digito]] = valor
        resultado = saida
        expoente *= base
    return resultado


def base(valores: list[int]) -> list[int]:
    """Radix Sort estável com suporte a inteiros negativos e positivos."""
    negativos_abs = [-valor for valor in valores if valor < 0]
    nao_negativos = [valor for valor in valores if valor >= 0]
    negativos_ordenados = _radix_nao_negativos(negativos_abs)
    positivos_ordenados = _radix_nao_negativos(nao_negativos)
    negativos = [-valor for valor in reversed(negativos_ordenados)]
    return negativos + positivos_ordenados


METODOS = {
    "insercao": insercao,
    "intercalacao": intercalacao,
    "rapida": rapida,
    "hibrida": hibrida,
    "contagem": contagem,
    "base": base,
}


def executar_metodo(nome: str, valores: list[int], seed: int = 0,
                    limite_hibrido: int = LIMITE_HIBRIDO) -> list[int]:
    """Executa um método pelo identificador usado no CSV e na documentação."""
    if nome == "rapida":
        return rapida(valores, seed=seed)
    if nome == "hibrida":
        return hibrida(valores, limite=limite_hibrido, seed=seed)
    if nome not in METODOS:
        raise ValueError(f"Método desconhecido: {nome}")
    return METODOS[nome](valores)
