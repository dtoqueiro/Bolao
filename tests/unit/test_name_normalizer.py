"""
🔴 RED: Testes para o utilitário de normalização de nomes.
Escritos ANTES da implementação (TDD).
"""
import pytest
from src.utils.name_normalizer import normalizar_nome, nomes_correspondem


class TestNormalizarNome:
    """Testes de normalização de nomes."""

    def test_nome_simples(self):
        assert normalizar_nome("João Silva") == "joao silva"

    def test_nome_maiusculo(self):
        assert normalizar_nome("MARIA SANTOS") == "maria santos"

    def test_nome_com_acentos(self):
        assert normalizar_nome("José Antônio") == "jose antonio"

    def test_nome_com_cedilha(self):
        assert normalizar_nome("Conceição Araújo") == "conceicao araujo"

    def test_nome_com_til(self):
        assert normalizar_nome("João Conceição") == "joao conceicao"

    def test_nome_com_espacos_extras(self):
        assert normalizar_nome("  João   Silva  ") == "joao silva"

    def test_nome_com_tabs(self):
        assert normalizar_nome("João\tSilva") == "joao silva"

    def test_nome_misto_maiusculas_minusculas(self):
        assert normalizar_nome("jOãO sIlVa") == "joao silva"


class TestNomesCorrespondem:
    """Testes de correspondência entre nomes."""

    def test_nomes_identicos(self):
        assert nomes_correspondem("João Silva", "João Silva") is True

    def test_nomes_case_diferente(self):
        assert nomes_correspondem("João Silva", "JOÃO SILVA") is True

    def test_nomes_com_e_sem_acentos(self):
        assert nomes_correspondem("João Silva", "Joao Silva") is True

    def test_nomes_com_espacos_diferentes(self):
        assert nomes_correspondem("João Silva", "  João   Silva  ") is True

    def test_nomes_diferentes(self):
        assert nomes_correspondem("João Silva", "Maria Santos") is False

    def test_nomes_parcialmente_iguais(self):
        """Nomes parciais NÃO devem corresponder (busca exata após normalização)."""
        assert nomes_correspondem("João", "João Silva") is False

    def test_nome_vazio(self):
        assert nomes_correspondem("", "João Silva") is False

    def test_ambos_vazios(self):
        assert nomes_correspondem("", "") is False
