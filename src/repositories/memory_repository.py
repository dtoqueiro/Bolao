"""
Repositório em memória para testes e desenvolvimento.

Implementação do BaseRepository usando estruturas de dados em memória
(listas e dicionários). Usada em todos os testes unitários e de integração
para eliminar dependência do Google Sheets.
"""
import unicodedata
from typing import List, Optional

from src.models.participante import Participante
from src.models.voto import Voto
from src.models.config_bolao import ConfigBolao
from src.repositories.base_repository import BaseRepository


def _normalizar_texto(texto: str) -> str:
    """Remove acentos e converte para minúsculas para comparação."""
    nfkd = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sem_acentos.lower().strip()


class MemoryRepository(BaseRepository):
    """Repositório de dados em memória.

    Armazena participantes, votos e configuração em listas Python.
    Ideal para testes e prototipagem sem dependências externas.
    """

    def __init__(self):
        self._participantes: List[Participante] = []
        self._votos: List[Voto] = []
        self._config: ConfigBolao = ConfigBolao()

    # --- Participantes ---

    def get_participantes(self) -> List[Participante]:
        return list(self._participantes)

    def get_participante_by_telefone(self, telefone: str) -> Optional[Participante]:
        for p in self._participantes:
            if p.telefone_limpo == telefone:
                return p
        return None

    def get_participante_by_nome(self, nome: str) -> Optional[Participante]:
        nome_normalizado = _normalizar_texto(nome)
        for p in self._participantes:
            if _normalizar_texto(p.nome) == nome_normalizado:
                return p
        return None

    def add_participante(self, participante: Participante) -> None:
        existente = self.get_participante_by_telefone(participante.telefone_limpo)
        if existente is not None:
            raise ValueError(
                f"Telefone já cadastrado: {participante.telefone_limpo}. "
                f"Participante existente: {existente.nome}."
            )
        self._participantes.append(participante)

    def update_participante(self, participante: Participante) -> None:
        for i, p in enumerate(self._participantes):
            if p.telefone_limpo == participante.telefone_limpo:
                self._participantes[i] = participante
                return
        raise ValueError(
            f"Participante com telefone {participante.telefone_limpo} não encontrado."
        )

    def update_participante_telefone(self, telefone_antigo: str, telefone_novo: str) -> None:
        for i, p in enumerate(self._participantes):
            if p.telefone_limpo == telefone_antigo:
                self._participantes[i] = Participante(
                    nome=p.nome,
                    telefone_limpo=telefone_novo,
                    status_voto=p.status_voto,
                    nivel_acesso=p.nivel_acesso,
                )
                return
        raise ValueError(
            f"Participante com telefone {telefone_antigo} não encontrado."
        )

    # --- Votos ---

    def get_votos(self) -> List[Voto]:
        return list(self._votos)

    def add_voto(self, voto: Voto) -> None:
        self._votos.append(voto)

    def delete_voto(self, telefone: str) -> None:
        self._votos = [v for v in self._votos if v.telefone_limpo != telefone]

    def contar_votos(self) -> int:
        return len(self._votos)

    # --- Configuração ---

    def get_config(self) -> ConfigBolao:
        return self._config

    def update_config(self, config: ConfigBolao) -> None:
        self._config = config
