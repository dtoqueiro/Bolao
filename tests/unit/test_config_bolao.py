"""
🔴 RED: Testes para o modelo ConfigBolao.
Escritos ANTES da implementação (TDD).
"""
import pytest
from src.models.config_bolao import ConfigBolao


class TestConfigBolaoCriacao:
    """Testes de criação do modelo ConfigBolao."""

    def test_cria_config_padrao(self):
        c = ConfigBolao()
        assert c.status == "ABERTO"
        assert c.quorum_alvo == 25
        assert c.qtd_jogos == 9
        assert c.dezenas_por_jogo == 16

    def test_cria_config_customizada(self):
        c = ConfigBolao(
            status="ABERTO",
            quorum_alvo=10,
            qtd_jogos=5,
            dezenas_por_jogo=15,
        )
        assert c.quorum_alvo == 10
        assert c.qtd_jogos == 5
        assert c.dezenas_por_jogo == 15

    def test_cria_config_fechado(self):
        c = ConfigBolao(status="FECHADO")
        assert c.status == "FECHADO"


class TestConfigBolaoValidacaoStatus:
    """Testes de validação do status."""

    def test_aceita_status_aberto(self):
        c = ConfigBolao(status="ABERTO")
        assert c.status == "ABERTO"

    def test_aceita_status_fechado(self):
        c = ConfigBolao(status="FECHADO")
        assert c.status == "FECHADO"

    def test_rejeita_status_invalido(self):
        with pytest.raises(ValueError, match="[Ss]tatus"):
            ConfigBolao(status="PAUSADO")


class TestConfigBolaoValidacaoQuorum:
    """Testes de validação do quórum."""

    def test_aceita_quorum_minimo(self):
        c = ConfigBolao(quorum_alvo=3)
        assert c.quorum_alvo == 3

    def test_aceita_quorum_maximo(self):
        c = ConfigBolao(quorum_alvo=50)
        assert c.quorum_alvo == 50

    def test_rejeita_quorum_abaixo_minimo(self):
        with pytest.raises(ValueError, match="[Qq]uórum|3.*50"):
            ConfigBolao(quorum_alvo=2)

    def test_rejeita_quorum_acima_maximo(self):
        with pytest.raises(ValueError, match="[Qq]uórum|3.*50"):
            ConfigBolao(quorum_alvo=51)


class TestConfigBolaoValidacaoJogos:
    """Testes de validação da quantidade de jogos."""

    def test_aceita_jogos_minimo(self):
        # 3 jogos × 17 dezenas = 51 slots (passa na validação de consistência)
        c = ConfigBolao(qtd_jogos=3, dezenas_por_jogo=17)
        assert c.qtd_jogos == 3

    def test_aceita_jogos_maximo(self):
        c = ConfigBolao(qtd_jogos=30)
        assert c.qtd_jogos == 30

    def test_rejeita_jogos_zero(self):
        with pytest.raises(ValueError, match="[Jj]ogos|1.*30"):
            ConfigBolao(qtd_jogos=0)

    def test_rejeita_jogos_acima_maximo(self):
        with pytest.raises(ValueError, match="[Jj]ogos|1.*30"):
            ConfigBolao(qtd_jogos=31)


class TestConfigBolaoValidacaoDezenas:
    """Testes de validação das dezenas por jogo."""

    def test_aceita_dezenas_minimo(self):
        c = ConfigBolao(dezenas_por_jogo=15)
        assert c.dezenas_por_jogo == 15

    def test_aceita_dezenas_maximo(self):
        c = ConfigBolao(dezenas_por_jogo=20)
        assert c.dezenas_por_jogo == 20

    def test_rejeita_dezenas_abaixo_minimo(self):
        with pytest.raises(ValueError, match="[Dd]ezenas|15.*20"):
            ConfigBolao(dezenas_por_jogo=14)

    def test_rejeita_dezenas_acima_maximo(self):
        with pytest.raises(ValueError, match="[Dd]ezenas|15.*20"):
            ConfigBolao(dezenas_por_jogo=21)


class TestConfigBolaoValidacaoConsistencia:
    """Testes de validação de consistência entre parâmetros."""

    def test_rejeita_cobertura_insuficiente(self):
        """qtd_jogos * dezenas_por_jogo deve ser >= 50 (média de 2 aparições por dezena)."""
        with pytest.raises(ValueError, match="[Cc]obertura|insuficiente|slots"):
            ConfigBolao(qtd_jogos=1, dezenas_por_jogo=15)  # 15 < 50


class TestConfigBolaoMetodos:
    """Testes de métodos auxiliares."""

    def test_esta_aberto(self):
        c = ConfigBolao(status="ABERTO")
        assert c.esta_aberto() is True

    def test_nao_esta_aberto(self):
        c = ConfigBolao(status="FECHADO")
        assert c.esta_aberto() is False

    def test_total_slots(self):
        c = ConfigBolao(qtd_jogos=9, dezenas_por_jogo=16)
        assert c.total_slots() == 144

    def test_frequencia_media(self):
        c = ConfigBolao(qtd_jogos=9, dezenas_por_jogo=16)
        assert c.frequencia_media() == pytest.approx(5.76)

    def test_custo_estimado(self):
        """Testa cálculo de custo baseado na tabela da Lotofácil."""
        c = ConfigBolao(qtd_jogos=9, dezenas_por_jogo=16)
        # 9 jogos × R$ 56,00 (16 dezenas) = R$ 504,00
        assert c.custo_estimado() == pytest.approx(504.0)
