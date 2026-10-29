"""Testes do método hibrida."""
from algoritmos import hibrida
import unittest
from tests.helpers import TesteComumOrdenacao


class TesteHibrida(TesteComumOrdenacao, unittest.TestCase):
    ordenador = staticmethod(hibrida)
