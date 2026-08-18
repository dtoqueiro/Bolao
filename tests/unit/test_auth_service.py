"""
🔴 RED: Testes para o serviço de autenticação.
Escritos ANTES da implementação (TDD).
"""
import pytest
from src.models.participante import Participante
from src.repositories.memory_repository import MemoryRepository
from src.services.auth_service import AuthService


@pytest.fixture
def repo_com_participantes():
    """Repositório com participantes de teste."""
    repo = MemoryRepository()
    repo.add_participante(Participante(
        nome="João Silva", telefone_limpo="11999998888",
        status_voto="Pendente", nivel_acesso="Participante",
    ))
    repo.add_participante(Participante(
        nome="Maria Santos", telefone_limpo="21988887777",
        status_voto="Pendente", nivel_acesso="Participante",
    ))
    repo.add_participante(Participante(
        nome="Carlos Admin", telefone_limpo="31977776666",
        status_voto="Pendente", nivel_acesso="Admin",
    ))
    repo.add_participante(Participante(
        nome="Ana Oliveira", telefone_limpo="41966665555",
        status_voto="Votou", nivel_acesso="Participante",
    ))
    return repo


@pytest.fixture
def auth(repo_com_participantes):
    """Instância do AuthService com repositório de teste."""
    return AuthService(repo_com_participantes)


class TestLoginPorTelefone:
    """Testes de login por telefone."""

    def test_login_telefone_limpo(self, auth):
        resultado = auth.login_por_telefone("11999998888")
        assert resultado.participante is not None
        assert resultado.participante.nome == "João Silva"
        assert resultado.sucesso is True

    def test_login_telefone_com_formatacao(self, auth):
        """O serviço deve limpar o telefone antes de buscar."""
        resultado = auth.login_por_telefone("(11) 99999-8888")
        assert resultado.sucesso is True
        assert resultado.participante.nome == "João Silva"

    def test_login_telefone_com_codigo_pais(self, auth):
        resultado = auth.login_por_telefone("+55 11 99999-8888")
        assert resultado.sucesso is True
        assert resultado.participante.nome == "João Silva"

    def test_login_telefone_nao_cadastrado(self, auth):
        resultado = auth.login_por_telefone("99888887777")
        assert resultado.sucesso is False
        assert resultado.participante is None
        assert "não cadastrado" in resultado.mensagem.lower() or "não encontrado" in resultado.mensagem.lower()

    def test_login_telefone_ja_votou(self, auth):
        resultado = auth.login_por_telefone("41966665555")
        assert resultado.sucesso is False
        assert resultado.participante is None
        assert "já votou" in resultado.mensagem.lower()

    def test_login_telefone_invalido(self, auth):
        resultado = auth.login_por_telefone("123")
        assert resultado.sucesso is False
        assert "inválido" in resultado.mensagem.lower() or "dígitos" in resultado.mensagem.lower()


class TestLoginPorNome:
    """Testes de login por nome."""

    def test_login_nome_exato(self, auth):
        resultado = auth.login_por_nome("João Silva")
        assert resultado.sucesso is True
        assert resultado.participante.telefone_limpo == "11999998888"

    def test_login_nome_case_insensitive(self, auth):
        resultado = auth.login_por_nome("joão silva")
        assert resultado.sucesso is True
        assert resultado.participante.nome == "João Silva"

    def test_login_nome_sem_acentos(self, auth):
        resultado = auth.login_por_nome("Joao Silva")
        assert resultado.sucesso is True

    def test_login_nome_maiusculo(self, auth):
        resultado = auth.login_por_nome("MARIA SANTOS")
        assert resultado.sucesso is True
        assert resultado.participante.nome == "Maria Santos"

    def test_login_nome_nao_cadastrado(self, auth):
        resultado = auth.login_por_nome("Fulano Desconhecido")
        assert resultado.sucesso is False
        assert "não cadastrado" in resultado.mensagem.lower() or "não encontrado" in resultado.mensagem.lower()

    def test_login_nome_ja_votou(self, auth):
        resultado = auth.login_por_nome("Ana Oliveira")
        assert resultado.sucesso is False
        assert "já votou" in resultado.mensagem.lower()

    def test_login_nome_vazio(self, auth):
        resultado = auth.login_por_nome("")
        assert resultado.sucesso is False


class TestLoginAdmin:
    """Testes de identificação de Admin."""

    def test_login_admin_por_telefone(self, auth):
        resultado = auth.login_por_telefone("31977776666")
        assert resultado.sucesso is True
        assert resultado.participante.eh_admin() is True
        assert resultado.eh_admin is True

    def test_login_admin_por_nome(self, auth):
        resultado = auth.login_por_nome("Carlos Admin")
        assert resultado.sucesso is True
        assert resultado.eh_admin is True

    def test_login_participante_nao_eh_admin(self, auth):
        resultado = auth.login_por_telefone("11999998888")
        assert resultado.sucesso is True
        assert resultado.eh_admin is False


class TestResultadoLogin:
    """Testes da estrutura do resultado de login."""

    def test_resultado_sucesso_tem_participante(self, auth):
        resultado = auth.login_por_telefone("11999998888")
        assert resultado.sucesso is True
        assert resultado.participante is not None
        assert resultado.mensagem != ""

    def test_resultado_falha_sem_participante(self, auth):
        resultado = auth.login_por_telefone("99888887777")
        assert resultado.sucesso is False
        assert resultado.participante is None
        assert resultado.mensagem != ""
