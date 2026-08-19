"""
Serviço de votação.

Gerencia o registro de votos dos participantes, aplicando as regras
de negócio e validações definidas nos modelos.
"""
from dataclasses import dataclass
from typing import List, Optional

from src.models.voto import Voto
from src.repositories.base_repository import BaseRepository


@dataclass
class ResultadoVotacao:
    """Resultado de uma tentativa de registro de voto."""
    sucesso: bool
    mensagem: str
    voto_registrado: Optional[Voto] = None


class VotacaoService:
    """Serviço que gerencia o registro de votos no bolão."""

    def __init__(self, repository: BaseRepository):
        self._repo = repository

    def registrar_voto(self, telefone_limpo: str, dezenas_positivas: List[int], dezenas_negativas: List[int]) -> ResultadoVotacao:
        """Tenta registrar um voto para um participante.

        Args:
            telefone_limpo: Telefone identificador do participante (chave).
            dezenas_positivas: Lista de dezenas escolhidas (favoritas).
            dezenas_negativas: Lista de dezenas rejeitadas.

        Returns:
            ResultadoVotacao com sucesso/falha e mensagem explicativa.
        """
        # 1. Verifica se o bolão está aberto
        config = self._repo.get_config()
        if not config.esta_aberto():
            return ResultadoVotacao(
                sucesso=False,
                mensagem="Não é possível votar: o bolão já está fechado."
            )

        # 2. Busca o participante
        participante = self._repo.get_participante_by_telefone(telefone_limpo)
        if participante is None:
            return ResultadoVotacao(
                sucesso=False,
                mensagem=f"Participante não encontrado (telefone: {telefone_limpo})."
            )

        # 4. Tenta criar o modelo de voto (onde ocorrem as validações de regra de negócio)
        try:
            voto = Voto(
                telefone_limpo=telefone_limpo,
                dezenas_positivas=dezenas_positivas,
                dezenas_negativas=dezenas_negativas
            )
        except ValueError as e:
            return ResultadoVotacao(
                sucesso=False,
                mensagem=f"Voto inválido: {e}"
            )

        # 5. Se o participante já tinha votado, apagamos o voto anterior para substituir
        if participante.ja_votou():
            self._repo.delete_voto(telefone_limpo)

        # 6. Salva o voto e atualiza o status do participante
        self._repo.add_voto(voto)
        
        participante.status_voto = "Votou"
        self._repo.update_participante(participante)

        # 6. Verifica quórum para auto-encerramento (Opcional, mas útil)
        # Se atingiu o quórum, o bolão deve ser fechado
        if self._repo.contar_votos() >= config.quorum_alvo:
             config.status = "FECHADO"
             self._repo.update_config(config)

        return ResultadoVotacao(
            sucesso=True,
            mensagem="Voto registrado com sucesso!",
            voto_registrado=voto
        )
