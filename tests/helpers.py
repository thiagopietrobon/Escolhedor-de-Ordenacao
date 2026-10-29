"""Casos comuns de correção para cada algoritmo."""

import random


class TesteComumOrdenacao:
    ordenador = None

    def test_casos_basicos_e_extremos(self):
        casos = [
            [],
            [1],
            [4, 4, 4, 4],
            [1, 2, 3, 4, 5],
            [5, 4, 3, 2, 1],
            [-7, 0, 7, -7, 3, 0],
            [-1000000000000, -9, -2, 0, 2, 9, 1000000000000],
            [3, -1, 3, 2, -1, 0, 2],
        ]
        rng = random.Random(70219)
        casos.extend(
            [
                [rng.randint(-200, 200) for _ in range(250)],
                [rng.randint(-20, 20) for _ in range(1000)],
            ]
        )
        for entrada in casos:
            # Counting Sort deve recusar esse caso específico pela amplitude,
            # e a recusa é verificada em seu próprio teste dedicado.
            if (
                getattr(self.ordenador, "__name__", "") == "contagem"
                and entrada
                and max(entrada) - min(entrada) + 1 > 500_000
            ):
                continue
            with self.subTest(tamanho=len(entrada), entrada=entrada[:12]):
                original = entrada.copy()
                resultado = self.ordenador(entrada)
                self.assertEqual(resultado, sorted(entrada))
                self.assertEqual(entrada, original, "A entrada original foi alterada")
                self.assertEqual(len(resultado), len(entrada))
                self.assertEqual(sorted(resultado), sorted(entrada))
                self.assertTrue(
                    all(
                        resultado[i] <= resultado[i + 1]
                        for i in range(len(resultado) - 1)
                    )
                )
