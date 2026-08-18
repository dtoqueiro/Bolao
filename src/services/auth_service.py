"""
Serviço de autenticação.

Gerencia login por telefone ou nome completo, com validação de
status de votação e identificação de nível de acesso (Admin).
Não importa Streamlit — lógica pura, testável isoladamente.
"""
from dataclasses import dataclass
from typing import Optional

from src.models.participante import Participante
from src.repositories.base_repository import BaseRepository
from src.utils.phone_cleaner import limpar_telefone


@dataclass
class ResultadoLogin:
    """Resultado de uma tentativa de login.

    Attributes:
        sucesso: True se o login foi bem-sucedido.
        participante: Dados do participante (None se falhou).
        mensagem: Mensagem descritiva do resultado.
        eh_admin: True se o participante tem privilégios de Admin.
    """
    sucesso: bool
    participante: Optional[Participante]
    mensagem: str
    eh_admin: bool = False


class AuthService:
    """Serviço de autenticação e identificação de participantes.

    Suporta login por telefone (com limpeza automática) ou por
    nome completo (com normalização de acentos e case).

    Args:
        repository: Implementação do repositório de dados.
    """

    def __init__(self, repository: BaseRepository):
        self._repo = repository

    def login_por_telefone(self, telefone_raw: str) -> ResultadoLogin:
        """Tenta autenticar um participante pelo número de telefone.

        O telefone é limpo automaticamente (remove formatação, código de país).

        Args:
            telefone_raw: Telefone em qualquer formato.

        Returns:
            ResultadoLogin com sucesso/falha e dados do participante.
        """
        # Tentar limpar o telefone
        try:
            telefone_limpo = limpar_telefone(telefone_raw)
        except ValueError as e:
            return ResultadoLogin(
                sucesso=False,
                participante=None,
                mensagem=f"Telefone inválido: {e}",
            )

        # Buscar participante
        participante = self._repo.get_participante_by_telefone(telefone_limpo)
        if participante is None:
            return ResultadoLogin(
                sucesso=False,
                participante=None,
                mensagem=f"Telefone não cadastrado: {telefone_limpo}. "
                         f"Verifique o número ou entre em contato com o administrador.",
            )

        # Verificar se já votou
        return self._verificar_status_e_retornar(participante)

    def login_por_nome(self, nome: str) -> ResultadoLogin:
        """Tenta autenticar um participante pelo nome completo.

        O nome é normalizado automaticamente (sem acentos, case-insensitive).

        Args:
            nome: Nome completo do participante.

        Returns:
            ResultadoLogin com sucesso/falha e dados do participante.
        """
        if not nome or not nome.strip():
            return ResultadoLogin(
                sucesso=False,
                participante=None,
                mensagem="Nome não pode ser vazio.",
            )

        # Buscar participante (MemoryRepository já normaliza internamente)
        participante = self._repo.get_participante_by_nome(nome)
        if participante is None:
            return ResultadoLogin(
                sucesso=False,
                participante=None,
                mensagem=f"Nome não encontrado: '{nome}'. "
                         f"Verifique a grafia ou entre em contato com o administrador.",
            )

        # Verificar se já votou
        return self._verificar_status_e_retornar(participante)

    def _verificar_status_e_retornar(self, participante: Participante) -> ResultadoLogin:
        """Verifica o status de votação e retorna o resultado."""
        if participante.ja_votou():
            return ResultadoLogin(
                sucesso=False,
                participante=None,
                mensagem=f"{participante.nome} já votou neste bolão. "
                         f"Se precisar refazer, peça ao administrador para resetar.",
            )

        return ResultadoLogin(
            sucesso=True,
            participante=participante,
            mensagem=f"Bem-vindo(a), {participante.nome}!",
            eh_admin=participante.eh_admin(),
        )
