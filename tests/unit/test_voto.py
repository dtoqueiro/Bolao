"""
🔴 RED: Testes para o modelo Voto.
Escritos ANTES da implementação (TDD).
"""
import pytest
from datetime import datetime
from src.models.voto import Voto


class TestVotoCriacao:
    """Testes de criação do modelo Voto."""

    def test_cria_voto_valido_completo(self):
        v = Voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[1, 2, 3, 4, 5],
            dezenas_negativas=[23, 24, 25],
        )
        assert v.telefone_limpo == "11999998888"
        assert v.dezenas_positivas == [1, 2, 3, 4, 5]
        assert v.dezenas_negativas == [23, 24, 25]

    def test_cria_voto_sem_negativas(self):
        v = Voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[1, 2, 3, 4, 5],
            dezenas_negativas=[],
        )
        assert v.dezenas_negativas == []

    def test_cria_voto_com_data_hora(self):
        agora = datetime(2026, 8, 17, 10, 0, 0)
        v = Voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[1, 2, 3],
            dezenas_negativas=[24, 25],
            data_hora=agora,
        )
        assert v.data_hora == agora

    def test_data_hora_padrao_preenchida(self):
        v = Voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[1, 2, 3],
            dezenas_negativas=[],
        )
        assert v.data_hora is not None
        assert isinstance(v.data_hora, datetime)


class TestVotoValidacaoPositivas:
    """Testes de validação das dezenas positivas."""

    def test_rejeita_mais_de_5_positivas(self):
        with pytest.raises(ValueError, match="5"):
            Voto(
                telefone_limpo="11999998888",
                dezenas_positivas=[1, 2, 3, 4, 5, 6],
                dezenas_negativas=[],
            )

    def test_rejeita_zero_positivas(self):
        with pytest.raises(ValueError, match="positiva"):
            Voto(
                telefone_limpo="11999998888",
                dezenas_positivas=[],
                dezenas_negativas=[],
            )

    def test_aceita_1_positiva(self):
        v = Voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[10],
            dezenas_negativas=[],
        )
        assert len(v.dezenas_positivas) == 1

    def test_aceita_5_positivas(self):
        v = Voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[1, 2, 3, 4, 5],
            dezenas_negativas=[],
        )
        assert len(v.dezenas_positivas) == 5


class TestVotoValidacaoNegativas:
    """Testes de validação das dezenas negativas."""

    def test_rejeita_mais_de_3_negativas(self):
        with pytest.raises(ValueError, match="3"):
            Voto(
                telefone_limpo="11999998888",
                dezenas_positivas=[1, 2, 3],
                dezenas_negativas=[21, 22, 23, 24],
            )

    def test_aceita_0_negativas(self):
        v = Voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[1, 2, 3],
            dezenas_negativas=[],
        )
        assert len(v.dezenas_negativas) == 0

    def test_aceita_3_negativas(self):
        v = Voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[1, 2, 3],
            dezenas_negativas=[23, 24, 25],
        )
        assert len(v.dezenas_negativas) == 3


class TestVotoValidacaoAntiIntersecao:
    """Testes de validação de anti-interseção (REQ-07)."""

    def test_rejeita_dezena_positiva_e_negativa(self):
        with pytest.raises(ValueError, match="[Ii]nterseção|simultaneamente|mesma dezena"):
            Voto(
                telefone_limpo="11999998888",
                dezenas_positivas=[1, 2, 3, 4, 5],
                dezenas_negativas=[5, 24, 25],
            )

    def test_rejeita_multiplas_intersecoes(self):
        with pytest.raises(ValueError, match="[Ii]nterseção|simultaneamente|mesma dezena"):
            Voto(
                telefone_limpo="11999998888",
                dezenas_positivas=[1, 2, 3],
                dezenas_negativas=[1, 2, 3],
            )


class TestVotoValidacaoDezenas:
    """Testes de validação do range das dezenas (01-25)."""

    def test_rejeita_dezena_zero(self):
        with pytest.raises(ValueError, match="1.*25|fora do intervalo"):
            Voto(
                telefone_limpo="11999998888",
                dezenas_positivas=[0, 1, 2],
                dezenas_negativas=[],
            )

    def test_rejeita_dezena_26(self):
        with pytest.raises(ValueError, match="1.*25|fora do intervalo"):
            Voto(
                telefone_limpo="11999998888",
                dezenas_positivas=[1, 2, 26],
                dezenas_negativas=[],
            )

    def test_rejeita_dezena_negativa_fora_range(self):
        with pytest.raises(ValueError, match="1.*25|fora do intervalo"):
            Voto(
                telefone_limpo="11999998888",
                dezenas_positivas=[1, 2, 3],
                dezenas_negativas=[0],
            )

    def test_rejeita_positivas_duplicadas(self):
        with pytest.raises(ValueError, match="[Dd]uplicad|[Rr]epetid"):
            Voto(
                telefone_limpo="11999998888",
                dezenas_positivas=[1, 1, 2],
                dezenas_negativas=[],
            )

    def test_rejeita_negativas_duplicadas(self):
        with pytest.raises(ValueError, match="[Dd]uplicad|[Rr]epetid"):
            Voto(
                telefone_limpo="11999998888",
                dezenas_positivas=[1, 2, 3],
                dezenas_negativas=[24, 24],
            )
