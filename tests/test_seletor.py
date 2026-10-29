"""Testes específicos das funções de seleção e ordenação automática."""
import random
import unittest
from algoritmos import METODOS
from seletor import escolher, ordenar


class TesteSeletor(unittest.TestCase):
    def test_escolhe_metodo_conhecido(self):
        for entrada in ([], [1], [3, 2], list(range(1000)),
                        [random.Random(1).randint(-20, 20) for _ in range(500)]):
            self.assertIn(escolher(entrada), METODOS)

    def test_ordenar_correto_preservando_entrada(self):
        rng = random.Random(128)
        casos = [[], [5], [4, 4, 1, -3, 0],
                 [rng.randint(-100, 100) for _ in range(1000)]]
        for entrada in casos:
            original = entrada.copy()
            self.assertEqual(ordenar(entrada), sorted(entrada))
            self.assertEqual(entrada, original)

    def test_contagem_nao_escolhida_quando_faixa_e_ampla(self):
        entrada = [-10**9, 0, 10**9] * 100
        self.assertNotEqual(escolher(entrada), "contagem")

    def test_contagem_escolhida_para_faixa_estreita(self):
        entrada = [((i * 17) % 101) - 50 for i in range(1000)]
        self.assertEqual(escolher(entrada), "contagem")

    def test_lista_vazia_e_unitaria_retorna_copia(self):
        for entrada in ([], [7]):
            resultado = ordenar(entrada)
            self.assertEqual(resultado, entrada)
            self.assertIsNot(resultado, entrada)
