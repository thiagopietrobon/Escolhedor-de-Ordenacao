"""Testes do método base."""

import unittest

from algoritmos import base
from tests.helpers import TesteComumOrdenacao


class TesteBase(TesteComumOrdenacao, unittest.TestCase):
    ordenador = staticmethod(base)
