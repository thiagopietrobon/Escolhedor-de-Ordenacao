"""Testes do método base."""
from algoritmos import base
import unittest
from tests.helpers import TesteComumOrdenacao


class TesteBase(TesteComumOrdenacao, unittest.TestCase):
    ordenador = staticmethod(base)
