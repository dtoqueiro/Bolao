"""
🔴 RED: Testes para o utilitário de limpeza de telefone.
Escritos ANTES da implementação (TDD).
"""
import pytest
from src.utils.phone_cleaner import limpar_telefone


class TestLimparTelefoneFormatosComuns:
    """Testes de limpeza para formatos comuns de telefone brasileiro."""

    def test_telefone_ja_limpo(self):
        assert limpar_telefone("11999998888") == "11999998888"

    def test_telefone_com_parenteses_e_traco(self):
        assert limpar_telefone("(11) 99999-8888") == "11999998888"

    def test_telefone_com_codigo_pais_55(self):
        assert limpar_telefone("+55 11 99999-8888") == "11999998888"

    def test_telefone_com_codigo_pais_sem_mais(self):
        assert limpar_telefone("55 11 99999-8888") == "11999998888"

    def test_telefone_com_espacos(self):
        assert limpar_telefone("11 99999 8888") == "11999998888"

    def test_telefone_com_pontos(self):
        assert limpar_telefone("11.99999.8888") == "11999998888"

    def test_telefone_com_parenteses_sem_espaco(self):
        assert limpar_telefone("(11)999998888") == "11999998888"

    def test_telefone_com_tracos_multiplos(self):
        assert limpar_telefone("11-99999-8888") == "11999998888"

    def test_telefone_com_codigo_pais_completo(self):
        assert limpar_telefone("+55(21)98888-7777") == "21988887777"


class TestLimparTelefoneDDDs:
    """Testes para diferentes DDDs brasileiros."""

    def test_ddd_sao_paulo(self):
        assert limpar_telefone("(11) 98765-4321") == "11987654321"

    def test_ddd_rio(self):
        assert limpar_telefone("(21) 97654-3210") == "21976543210"

    def test_ddd_belo_horizonte(self):
        assert limpar_telefone("(31) 96543-2109") == "31965432109"

    def test_ddd_curitiba(self):
        assert limpar_telefone("(41) 95432-1098") == "41954321098"


class TestLimparTelefoneErros:
    """Testes de validação e rejeição de entradas inválidas."""

    def test_rejeita_telefone_curto(self):
        with pytest.raises(ValueError, match="11 dígitos"):
            limpar_telefone("1199999")

    def test_rejeita_telefone_longo_sem_codigo_pais(self):
        with pytest.raises(ValueError, match="11 dígitos"):
            limpar_telefone("119999988881234")

    def test_rejeita_string_vazia(self):
        with pytest.raises(ValueError, match="vazio|inválido"):
            limpar_telefone("")

    def test_rejeita_somente_espacos(self):
        with pytest.raises(ValueError, match="vazio|inválido"):
            limpar_telefone("   ")

    def test_rejeita_letras(self):
        with pytest.raises(ValueError, match="11 dígitos|inválido"):
            limpar_telefone("abcdefghijk")

    def test_rejeita_telefone_fixo_8_digitos(self):
        """Telefone fixo (8 dígitos + DDD = 10) não tem 11 dígitos."""
        with pytest.raises(ValueError, match="11 dígitos"):
            limpar_telefone("(11) 3456-7890")


class TestLimparTelefoneEdgeCases:
    """Testes de edge cases."""

    def test_telefone_com_tabs(self):
        assert limpar_telefone("11\t99999\t8888") == "11999998888"

    def test_telefone_com_newline(self):
        assert limpar_telefone("11999998888\n") == "11999998888"

    def test_telefone_com_codigo_pais_0055(self):
        assert limpar_telefone("0055 11 99999-8888") == "11999998888"
