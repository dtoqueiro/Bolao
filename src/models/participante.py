"""
Modelo de dados: Participante do Bolão.

Representa um membro cadastrado no bolão com seus dados de identificação,
status de votação e nível de acesso.
"""
from dataclasses import dataclass, field


# Status válidos para o voto do participante
STATUS_VOTO_VALIDOS = ("Pendente", "Votou")

# Níveis de acesso válidos
NIVEIS_ACESSO_VALIDOS = ("Participante", "Admin")


@dataclass
class Participante:
    """Participante do bolão Lotofácil.

    Attributes:
        nome: Nome completo do participante.
        telefone_limpo: Telefone com 11 dígitos numéricos (DDD + número).
        status_voto: Status atual da votação ("Pendente" ou "Votou").
        nivel_acesso: Nível de acesso no sistema ("Participante" ou "Admin").
    """

    nome: str
    telefone_limpo: str
    status_voto: str = "Pendente"
    nivel_acesso: str = "Participante"

    def __post_init__(self):
        """Validações executadas após a inicialização."""
        self._validar_nome()
        self._validar_telefone()
        self._validar_status_voto()
        self._validar_nivel_acesso()

    def _validar_nome(self):
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome não pode ser vazio.")

    def _validar_telefone(self):
        telefone = self.telefone_limpo
        if not telefone.isdigit():
            raise ValueError(
                f"Telefone deve conter apenas caracteres numéricos. Recebido: '{telefone}'"
            )
        if len(telefone) != 11:
            raise ValueError(
                f"Telefone deve ter exatamente 11 dígitos. Recebido: {len(telefone)} dígitos."
            )

    def _validar_status_voto(self):
        if self.status_voto not in STATUS_VOTO_VALIDOS:
            raise ValueError(
                f"Status de voto inválido: '{self.status_voto}'. "
                f"Valores aceitos: {STATUS_VOTO_VALIDOS}"
            )

    def _validar_nivel_acesso(self):
        if self.nivel_acesso not in NIVEIS_ACESSO_VALIDOS:
            raise ValueError(
                f"Nível de acesso inválido: '{self.nivel_acesso}'. "
                f"Valores aceitos: {NIVEIS_ACESSO_VALIDOS}"
            )

    def eh_admin(self) -> bool:
        """Verifica se o participante tem privilégios de administrador."""
        return self.nivel_acesso == "Admin"

    def ja_votou(self) -> bool:
        """Verifica se o participante já registrou seu voto."""
        return self.status_voto == "Votou"
