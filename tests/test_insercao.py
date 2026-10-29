"""Testes do método insercao."""

import unittest

from algoritmos import insercao
from tests.helpers import TesteComumOrdenacao


class TesteInsercao(TesteComumOrdenacao, unittest.TestCase):
    ordenador = staticmethod(insercao)
