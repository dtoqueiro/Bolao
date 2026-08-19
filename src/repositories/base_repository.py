"""
Interface abstrata para o repositório de dados.

Define o contrato que todas as implementações de persistência devem seguir
(Google Sheets, memória, banco de dados, etc.).
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from src.models.participante import Participante
from src.models.voto import Voto
from src.models.config_bolao import ConfigBolao


class BaseRepository(ABC):
    """Contrato abstrato para operações de persistência do bolão.

    Qualquer implementação (Google Sheets, memória, SQLite) deve
    herdar desta classe e implementar todos os métodos abstratos.
    """

    # --- Participantes ---

    @abstractmethod
    def get_participantes(self) -> List[Participante]:
        """Retorna todos os participantes cadastrados."""
        ...

    @abstractmethod
    def get_participante_by_telefone(self, telefone: str) -> Optional[Participante]:
        """Busca participante pelo telefone limpo (11 dígitos)."""
        ...

    @abstractmethod
    def get_participante_by_nome(self, nome: str) -> Optional[Participante]:
        """Busca participante pelo nome (case-insensitive, sem acentos)."""
        ...

    @abstractmethod
    def add_participante(self, participante: Participante) -> None:
        """Cadastra um novo participante. Lança ValueError se telefone duplicado."""
        ...

    @abstractmethod
    def update_participante(self, participante: Participante) -> None:
        """Atualiza dados de um participante existente (busca por telefone)."""
        ...

    @abstractmethod
    def update_participante_telefone(self, telefone_antigo: str, telefone_novo: str) -> None:
        """Atualiza o telefone de um participante."""
        ...

    @abstractmethod
    def delete_participante(self, telefone: str) -> None:
        """Remove um participante pelo telefone."""
        ...

    # --- Votos ---

    @abstractmethod
    def get_votos(self) -> List[Voto]:
        """Retorna todos os votos registrados."""
        ...

    @abstractmethod
    def add_voto(self, voto: Voto) -> None:
        """Registra um novo voto."""
        ...

    @abstractmethod
    def delete_voto(self, telefone: str) -> None:
        """Remove o voto de um participante (para reset)."""
        ...

    @abstractmethod
    def contar_votos(self) -> int:
        """Retorna o número total de votos registrados."""
        ...

    # --- Configuração ---

    @abstractmethod
    def get_config(self) -> ConfigBolao:
        """Retorna a configuração atual do bolão."""
        ...

    @abstractmethod
    def update_config(self, config: ConfigBolao) -> None:
        """Atualiza a configuração do bolão."""
        ...
