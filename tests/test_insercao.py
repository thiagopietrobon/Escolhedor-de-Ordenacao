"""Testes do método insercao."""
from algoritmos import insercao
import unittest
from tests.helpers import TesteComumOrdenacao


class TesteInsercao(TesteComumOrdenacao, unittest.TestCase):
    ordenador = staticmethod(insercao)
