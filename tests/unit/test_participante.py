"""
🔴 RED: Testes para o modelo Participante.
Escritos ANTES da implementação (TDD).
"""
import pytest
from src.models.participante import Participante


class TestParticipanteCriacao:
    """Testes de criação e validação do modelo Participante."""

    def test_cria_participante_valido(self):
        p = Participante(
            nome="João Silva",
            telefone_limpo="11999998888",
            status_voto="Pendente",
            nivel_acesso="Participante",
        )
        assert p.nome == "João Silva"
        assert p.telefone_limpo == "11999998888"
        assert p.status_voto == "Pendente"
        assert p.nivel_acesso == "Participante"

    def test_cria_participante_admin(self):
        p = Participante(
            nome="Carlos Admin",
            telefone_limpo="31977776666",
            status_voto="Pendente",
            nivel_acesso="Admin",
        )
        assert p.nivel_acesso == "Admin"

    def test_status_padrao_pendente(self):
        p = Participante(
            nome="Teste",
            telefone_limpo="11999998888",
        )
        assert p.status_voto == "Pendente"

    def test_nivel_acesso_padrao_participante(self):
        p = Participante(
            nome="Teste",
            telefone_limpo="11999998888",
        )
        assert p.nivel_acesso == "Participante"


class TestParticipanteValidacao:
    """Testes de validação de dados do Participante."""

    def test_rejeita_telefone_curto(self):
        with pytest.raises(ValueError, match="11 dígitos"):
            Participante(nome="Teste", telefone_limpo="1199999")

    def test_rejeita_telefone_longo(self):
        with pytest.raises(ValueError, match="11 dígitos"):
            Participante(nome="Teste", telefone_limpo="119999988881")

    def test_rejeita_telefone_com_letras(self):
        with pytest.raises(ValueError, match="numéricos"):
            Participante(nome="Teste", telefone_limpo="1199999abcd")

    def test_rejeita_nome_vazio(self):
        with pytest.raises(ValueError, match="[Nn]ome"):
            Participante(nome="", telefone_limpo="11999998888")

    def test_rejeita_nome_somente_espacos(self):
        with pytest.raises(ValueError, match="[Nn]ome"):
            Participante(nome="   ", telefone_limpo="11999998888")

    def test_rejeita_status_invalido(self):
        with pytest.raises(ValueError, match="[Ss]tatus"):
            Participante(
                nome="Teste",
                telefone_limpo="11999998888",
                status_voto="Invalido",
            )

    def test_rejeita_nivel_acesso_invalido(self):
        with pytest.raises(ValueError, match="[Nn]ível|[Aa]cesso"):
            Participante(
                nome="Teste",
                telefone_limpo="11999998888",
                nivel_acesso="SuperAdmin",
            )


class TestParticipanteMetodos:
    """Testes de métodos auxiliares do Participante."""

    def test_eh_admin(self):
        p = Participante(nome="Admin", telefone_limpo="11999998888", nivel_acesso="Admin")
        assert p.eh_admin() is True

    def test_nao_eh_admin(self):
        p = Participante(nome="User", telefone_limpo="11999998888", nivel_acesso="Participante")
        assert p.eh_admin() is False

    def test_ja_votou(self):
        p = Participante(nome="User", telefone_limpo="11999998888", status_voto="Votou")
        assert p.ja_votou() is True

    def test_nao_votou(self):
        p = Participante(nome="User", telefone_limpo="11999998888", status_voto="Pendente")
        assert p.ja_votou() is False
