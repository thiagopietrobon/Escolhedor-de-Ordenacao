"""Testes do método hibrida."""

import unittest

from algoritmos import hibrida
from tests.helpers import TesteComumOrdenacao


class TesteHibrida(TesteComumOrdenacao, unittest.TestCase):
    ordenador = staticmethod(hibrida)
