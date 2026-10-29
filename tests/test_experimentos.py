
"""Testes do controle e registro das medições experimentais."""

import os
import subprocess
import sys
import unittest
from unittest.mock import patch

import experimentos
from algoritmos import LimiteContagemExcedido


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

    def test_importacao_falha_com_timeout_invalido(self):
        ambiente = os.environ.copy()
        ambiente["ORDENACAO_TIMEOUT_S"] = "0"

        resultado = subprocess.run(
            [
                sys.executable,
                "-c",
                "import experimentos",
            ],
            env=ambiente,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(resultado.returncode, 0)
        self.assertIn("ORDENACAO_TIMEOUT_S", resultado.stderr)

    def test_metodo_desconhecido_e_registrado_como_erro(self):
        resultado = experimentos._trabalho_medido(
            "metodo-inexistente", [], seed=0, limite_hibrido=24
        )

        self.assertEqual(resultado[0], "erro")
        self.assertIn("ValueError", resultado[3])

    def test_recusa_de_limite_do_counting_sort(self):
        resultado = experimentos._trabalho_medido(
            "contagem",
            [-10**12, 0, 10**12],
            seed=0,
            limite_hibrido=24,
        )

        self.assertEqual(resultado[0], "recusada_limite")
        self.assertIsInstance(
            LimiteContagemExcedido(
                "teste"
            ),
            ValueError,
        )

    def test_value_error_inesperado_do_counting_sort_e_erro(self):
        with patch.object(
            experimentos,
            "executar_metodo",
            side_effect=ValueError("falha inesperada"),
        ):
            resultado = experimentos._trabalho_medido(
                "contagem", [1, 2, 3], seed=0, limite_hibrido=24
            )

        self.assertEqual(resultado[0], "erro")
        self.assertIn("ValueError: falha inesperada", resultado[3])

    def test_runtime_error_e_registrado(self):
        with patch.object(
            experimentos,
            "executar_metodo",
            side_effect=RuntimeError("erro interno"),
        ):
            resultado = experimentos._trabalho_medido(
                "insercao", [3, 2, 1], seed=0, limite_hibrido=24
            )

        self.assertEqual(resultado[0], "erro")
        self.assertIn("RuntimeError: erro interno", resultado[3])

    def test_keyboard_interrupt_nao_e_engolido(self):
        with patch.object(
            experimentos,
            "executar_metodo",
            side_effect=KeyboardInterrupt,
        ):
            with self.assertRaises(KeyboardInterrupt):
                experimentos._trabalho_medido(
                    "insercao", [3, 2, 1], seed=0, limite_hibrido=24
                )

    
    def test_processo_filho_termina_sem_resultado(self):
        class ConexaoFalsa:
            def __init__(self):
                self.fechada = False

            def send(self, valor):
                pass

            def close(self):
                self.fechada = True

            def poll(self, timeout):
                return False

            def recv(self):
                raise EOFError("canal fechado")

        class ProcessoFalso:
            def __init__(self, *args, **kwargs):
                self.exitcode = 1
                self.iniciado = False

            def start(self):
                self.iniciado = True

            def is_alive(self):
                return False

            def join(self):
                pass

            def terminate(self):
                pass

        conexao_pai = ConexaoFalsa()
        conexao_filho = ConexaoFalsa()

        class ContextoFalso:
            @staticmethod
            def Pipe(duplex=False):
                return conexao_pai, conexao_filho

            @staticmethod
            def Process(target, args):
                return ProcessoFalso()

        with (
            patch.object(experimentos.os, "name", "nt"),
            patch.object(experimentos.multiprocessing, "get_context", return_value=ContextoFalso()),
            patch.object(experimentos, "TEMPO_LIMITE_SEGUNDOS", 0.01),
            patch.object(experimentos, "current_thread", return_value="worker"),
            patch.object(experimentos, "main_thread", return_value="main"),
        ):
            resultado = experimentos._executar_com_limite(
                "insercao", [3, 2, 1], seed=0
            )

        self.assertEqual(resultado[0], "erro")
        self.assertIn("sem enviar um resultado", resultado[3])
        self.assertIn("código de saída 1", resultado[3])

    def test_processo_vivo_apos_timeout_e_interrompido(self):
        class ConexaoFalsa:
            def close(self):
                pass

            def poll(self, timeout):
                return False

        class ProcessoFalso:
            exitcode = None

            def start(self):
                pass

            def is_alive(self):
                return True

            def terminate(self):
                self.terminado = True

            def join(self):
                pass

        conexao_pai = ConexaoFalsa()
        conexao_filho = ConexaoFalsa()

        class ContextoFalso:
            @staticmethod
            def Pipe(duplex=False):
                return conexao_pai, conexao_filho

            @staticmethod
            def Process(target, args):
                return ProcessoFalso()

        with (
            patch.object(experimentos.os, "name", "nt"),
            patch.object(experimentos.multiprocessing, "get_context", return_value=ContextoFalso()),
            patch.object(experimentos, "TEMPO_LIMITE_SEGUNDOS", 0.01),
            patch.object(experimentos, "current_thread", return_value="worker"),
            patch.object(experimentos, "main_thread", return_value="main"),
        ):
            resultado = experimentos._executar_com_limite(
                "insercao", [3, 2, 1], seed=0
            )

        self.assertEqual(resultado[0], "interrompida")
        self.assertIn("excedeu o limite", resultado[3])


if __name__ == "__main__":
    unittest.main()
