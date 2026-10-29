"""Testes do método rapida."""

import unittest

from algoritmos import rapida
from tests.helpers import TesteComumOrdenacao


class TesteRapida(TesteComumOrdenacao, unittest.TestCase):
    ordenador = staticmethod(rapida)
