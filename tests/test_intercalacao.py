"""Testes do método intercalacao."""
from algoritmos import intercalacao
import unittest
from tests.helpers import TesteComumOrdenacao


class TesteIntercalacao(TesteComumOrdenacao, unittest.TestCase):
    ordenador = staticmethod(intercalacao)
