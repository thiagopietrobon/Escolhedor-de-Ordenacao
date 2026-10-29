"""Testes do método rapida."""
from algoritmos import rapida
import unittest
from tests.helpers import TesteComumOrdenacao


class TesteRapida(TesteComumOrdenacao, unittest.TestCase):
    ordenador = staticmethod(rapida)
