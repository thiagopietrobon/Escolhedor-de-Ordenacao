"""Testes do controle e registro das medições experimentais."""
import os
import unittest
from unittest.mock import patch

import experimentos


class TesteExperimentos(unittest.TestCase):
    def test_timeout_deve_ser_positivo_e_finito(self):
        for valor in ("0", "-1", "nan", "inf", "texto"):
            with self.subTest(valor=valor), patch.dict(
                os.environ, {"ORDENACAO_TIMEOUT_S": valor}
            ):
                with self.assertRaisesRegex(ValueError, "número positivo"):
                    experimentos._obter_timeout()

    def test_timeout_valido(self):
        with patch.dict(os.environ, {"ORDENACAO_TIMEOUT_S": "2.5"}):
            self.assertEqual(experimentos._obter_timeout(), 2.5)

    def test_value_error_de_metodo_nao_e_recusa_de_limite(self):
        resultado = experimentos._trabalho_medido(
            "metodo-inexistente", [], seed=0, limite_hibrido=24
        )
        self.assertEqual(resultado[0], "erro")

    def test_value_error_do_counting_sort_e_recusa_de_limite(self):
        resultado = experimentos._trabalho_medido(
            "contagem",
            [-10**12, 0, 10**12],
            seed=0,
            limite_hibrido=24,
        )
        self.assertEqual(resultado[0], "recusada_limite")
