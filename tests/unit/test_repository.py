"""
🔴 RED: Testes para o repositório de dados (MemoryRepository).
Escritos ANTES da implementação (TDD).
"""
import pytest
from datetime import datetime
from src.models.participante import Participante
from src.models.voto import Voto
from src.models.config_bolao import ConfigBolao
from src.repositories.memory_repository import MemoryRepository


@pytest.fixture
def repo():
    """Cria repositório em memória com dados de teste."""
    r = MemoryRepository()
    r.add_participante(Participante(nome="João Silva", telefone_limpo="11999998888"))
    r.add_participante(Participante(nome="Maria Santos", telefone_limpo="21988887777"))
    r.add_participante(Participante(nome="Carlos Admin", telefone_limpo="31977776666", nivel_acesso="Admin"))
    return r


@pytest.fixture
def repo_vazio():
    """Cria repositório em memória vazio."""
    return MemoryRepository()


class TestMemoryRepositoryParticipantes:
    """Testes de CRUD de participantes."""

    def test_add_e_listar_participantes(self, repo):
        participantes = repo.get_participantes()
        assert len(participantes) == 3

    def test_buscar_por_telefone(self, repo):
        p = repo.get_participante_by_telefone("11999998888")
        assert p is not None
        assert p.nome == "João Silva"

    def test_buscar_por_telefone_inexistente(self, repo):
        p = repo.get_participante_by_telefone("99999999999")
        assert p is None

    def test_buscar_por_nome(self, repo):
        p = repo.get_participante_by_nome("Maria Santos")
        assert p is not None
        assert p.telefone_limpo == "21988887777"

    def test_buscar_por_nome_inexistente(self, repo):
        p = repo.get_participante_by_nome("Fulano Desconhecido")
        assert p is None

    def test_buscar_por_nome_case_insensitive(self, repo):
        p = repo.get_participante_by_nome("joão silva")
        assert p is not None
        assert p.nome == "João Silva"

    def test_buscar_por_nome_sem_acentos(self, repo):
        p = repo.get_participante_by_nome("Joao Silva")
        assert p is not None
        assert p.nome == "João Silva"

    def test_update_participante(self, repo):
        p = repo.get_participante_by_telefone("11999998888")
        p.status_voto = "Votou"
        repo.update_participante(p)
        p_atualizado = repo.get_participante_by_telefone("11999998888")
        assert p_atualizado.status_voto == "Votou"

    def test_update_telefone_participante(self, repo):
        repo.update_participante_telefone("11999998888", "11888887777")
        assert repo.get_participante_by_telefone("11999998888") is None
        assert repo.get_participante_by_telefone("11888887777") is not None

    def test_add_participante_telefone_duplicado(self, repo):
        with pytest.raises(ValueError, match="[Dd]uplicado|já existe|já cadastrado"):
            repo.add_participante(
                Participante(nome="Outro Nome", telefone_limpo="11999998888")
            )


class TestMemoryRepositoryVotos:
    """Testes de CRUD de votos."""

    def test_add_e_listar_votos(self, repo):
        voto = Voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[1, 2, 3, 4, 5],
            dezenas_negativas=[23, 24, 25],
        )
        repo.add_voto(voto)
        votos = repo.get_votos()
        assert len(votos) == 1
        assert votos[0].telefone_limpo == "11999998888"

    def test_delete_voto(self, repo):
        voto = Voto(
            telefone_limpo="11999998888",
            dezenas_positivas=[1, 2, 3, 4, 5],
            dezenas_negativas=[23, 24, 25],
        )
        repo.add_voto(voto)
        assert len(repo.get_votos()) == 1
        repo.delete_voto("11999998888")
        assert len(repo.get_votos()) == 0

    def test_delete_voto_inexistente_nao_da_erro(self, repo):
        repo.delete_voto("99999999999")  # Não deve lançar exceção

    def test_contar_votos(self, repo):
        assert repo.contar_votos() == 0
        repo.add_voto(Voto(telefone_limpo="11999998888", dezenas_positivas=[1, 2, 3], dezenas_negativas=[]))
        repo.add_voto(Voto(telefone_limpo="21988887777", dezenas_positivas=[4, 5, 6], dezenas_negativas=[]))
        assert repo.contar_votos() == 2


class TestMemoryRepositoryConfig:
    """Testes de CRUD de configuração."""

    def test_config_padrao(self, repo_vazio):
        config = repo_vazio.get_config()
        assert config.status == "ABERTO"
        assert config.quorum_alvo == 25
        assert config.qtd_jogos == 9
        assert config.dezenas_por_jogo == 16

    def test_update_config(self, repo_vazio):
        config = repo_vazio.get_config()
        config.qtd_jogos = 12
        repo_vazio.update_config(config)
        config_atualizada = repo_vazio.get_config()
        assert config_atualizada.qtd_jogos == 12

    def test_update_config_status_fechado(self, repo_vazio):
        config = repo_vazio.get_config()
        config.status = "FECHADO"
        repo_vazio.update_config(config)
        assert repo_vazio.get_config().status == "FECHADO"
