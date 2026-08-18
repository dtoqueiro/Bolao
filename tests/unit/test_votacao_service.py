"""
🔴 RED: Testes para o serviço de votação.
Escritos ANTES da implementação (TDD).
"""
import pytest
from src.models.participante import Participante
from src.models.voto import Voto
from src.repositories.memory_repository import MemoryRepository
from src.services.votacao_service import VotacaoService


@pytest.fixture
def repo_com_dados():
    repo = MemoryRepository()
    repo.add_participante(Participante(
        nome="João Silva", telefone_limpo="11999998888",
        status_voto="Pendente", nivel_acesso="Participante"
    ))
    repo.add_participante(Participante(
        nome="Maria Santos", telefone_limpo="21988887777",
        status_voto="Votou", nivel_acesso="Participante"
    ))
    # Adicionando o voto da Maria para consistência
    repo.add_voto(Voto(
        telefone_limpo="21988887777",
        dezenas_positivas=[1, 2, 3],
        dezenas_negativas=[25]
    ))
    return repo


@pytest.fixture
def votacao(repo_com_dados):
    return VotacaoService(repo_com_dados)


class TestRegistrarVoto:
    """Testes de registro de voto."""

    def test_registrar_voto_sucesso(self, votacao, repo_com_dados):
        resultado = votacao.registrar_voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[10, 11, 12, 13, 14],
            dezenas_negativas=[23, 24, 25]
        )
        assert resultado.sucesso is True
        assert "registrado" in resultado.mensagem.lower()
        
        # Verifica no repositório se o voto foi salvo
        votos = repo_com_dados.get_votos()
        assert len(votos) == 2 # 1 da Maria + 1 do João
        voto_joao = next((v for v in votos if v.telefone_limpo == "11999998888"), None)
        assert voto_joao is not None
        assert voto_joao.dezenas_positivas == [10, 11, 12, 13, 14]
        
        # Verifica se o status do participante foi atualizado
        p = repo_com_dados.get_participante_by_telefone("11999998888")
        assert p.status_voto == "Votou"

    def test_rejeita_voto_participante_nao_encontrado(self, votacao):
        resultado = votacao.registrar_voto(
            telefone_limpo="99999999999",
            dezenas_positivas=[1, 2, 3],
            dezenas_negativas=[]
        )
        assert resultado.sucesso is False
        assert "não encontrado" in resultado.mensagem.lower() or "cadastrado" in resultado.mensagem.lower()

    def test_rejeita_voto_participante_ja_votou(self, votacao):
        resultado = votacao.registrar_voto(
            telefone_limpo="21988887777", # Maria já votou
            dezenas_positivas=[4, 5, 6],
            dezenas_negativas=[]
        )
        assert resultado.sucesso is False
        assert "já votou" in resultado.mensagem.lower()

    def test_rejeita_voto_invalido(self, votacao):
        # Mais de 5 dezenas positivas vai quebrar na validação do modelo Voto
        resultado = votacao.registrar_voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[1, 2, 3, 4, 5, 6],
            dezenas_negativas=[]
        )
        assert resultado.sucesso is False
        assert "5" in resultado.mensagem.lower() or "máximo" in resultado.mensagem.lower()

    def test_rejeita_voto_bolao_fechado(self, votacao, repo_com_dados):
        # Fechar o bolão
        config = repo_com_dados.get_config()
        config.status = "FECHADO"
        repo_com_dados.update_config(config)

        resultado = votacao.registrar_voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[1, 2, 3],
            dezenas_negativas=[]
        )
        assert resultado.sucesso is False
        assert "fechado" in resultado.mensagem.lower()

    def test_encerra_bolao_automaticamente_ao_atingir_quorum(self, votacao, repo_com_dados):
        # Configurar quorum para 2
        config = repo_com_dados.get_config()
        config.quorum_alvo = 2 # Maria já votou, então falta 1
        repo_com_dados.update_config(config)
        
        # Registrar voto do João (2º voto, deve atingir quórum)
        resultado = votacao.registrar_voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[1, 2, 3],
            dezenas_negativas=[]
        )
        assert resultado.sucesso is True
        
        # O status do bolão deve ter mudado para FECHADO
        config_atualizada = repo_com_dados.get_config()
        assert config_atualizada.status == "FECHADO"
