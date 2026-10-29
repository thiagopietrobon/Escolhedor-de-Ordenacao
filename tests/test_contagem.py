"""Testes do método contagem."""
from algoritmos import contagem
import unittest
from tests.helpers import TesteComumOrdenacao


class TesteContagem(TesteComumOrdenacao, unittest.TestCase):
    ordenador = staticmethod(contagem)

    def test_recusa_amplitude_insegura(self):
        from algoritmos import contagem
        with self.assertRaisesRegex(ValueError, "amplitude|memória auxiliar"):
            contagem([-10**12, 0, 10**12])

    def test_limites_configuraveis(self):
        from algoritmos import contagem
        with self.assertRaises(ValueError):
            contagem([1, 2, 3], max_amplitude=2)

    def test_recusa_quando_memoria_estimada_excede_limite(self):
        from algoritmos import contagem
        with self.assertRaisesRegex(ValueError, "memória auxiliar estimada"):
            contagem([1, 2, 3], max_amplitude=100, max_memoria_bytes=100)
