"""Testes do método intercalacao."""

import unittest

from algoritmos import intercalacao
from tests.helpers import TesteComumOrdenacao


class TesteIntercalacao(TesteComumOrdenacao, unittest.TestCase):
    ordenador = staticmethod(intercalacao)
