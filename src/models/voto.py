"""
Modelo de dados: Voto de um participante.

Representa a seleção de dezenas favoritas e rejeitadas feita por um
participante do bolão, com validações de regras de negócio.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


# Limites da Lotofácil
DEZENA_MIN = 1
DEZENA_MAX = 25
MAX_POSITIVAS = 5
MAX_NEGATIVAS = 3


@dataclass
class Voto:
    """Voto (palpite) de um participante do bolão.

    Attributes:
        telefone_limpo: Telefone do participante (chave).
        dezenas_positivas: Lista de dezenas favoritas (1-5 dezenas, de 01 a 25).
        dezenas_negativas: Lista de dezenas rejeitadas (0-3 dezenas, de 01 a 25).
        data_hora: Data e hora do registro do voto.
    """

    telefone_limpo: str
    dezenas_positivas: List[int]
    dezenas_negativas: List[int]
    data_hora: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validações executadas após a inicialização."""
        self._validar_positivas()
        self._validar_negativas()
        self._validar_range_dezenas()
        self._validar_duplicatas()
        self._validar_anti_intersecao()

    def _validar_positivas(self):
        if len(self.dezenas_positivas) == 0:
            raise ValueError(
                "É necessário selecionar pelo menos 1 dezena positiva (favorita)."
            )
        if len(self.dezenas_positivas) > MAX_POSITIVAS:
            raise ValueError(
                f"Máximo de {MAX_POSITIVAS} dezenas positivas (favoritas). "
                f"Recebido: {len(self.dezenas_positivas)}."
            )

    def _validar_negativas(self):
        if len(self.dezenas_negativas) > MAX_NEGATIVAS:
            raise ValueError(
                f"Máximo de {MAX_NEGATIVAS} dezenas negativas (rejeitadas). "
                f"Recebido: {len(self.dezenas_negativas)}."
            )

    def _validar_range_dezenas(self):
        todas = self.dezenas_positivas + self.dezenas_negativas
        for d in todas:
            if d < DEZENA_MIN or d > DEZENA_MAX:
                raise ValueError(
                    f"Dezena {d} fora do intervalo válido ({DEZENA_MIN} a {DEZENA_MAX})."
                )

    def _validar_duplicatas(self):
        if len(self.dezenas_positivas) != len(set(self.dezenas_positivas)):
            raise ValueError("Dezenas positivas contêm valores duplicados.")
        if len(self.dezenas_negativas) != len(set(self.dezenas_negativas)):
            raise ValueError("Dezenas negativas contêm valores duplicados.")

    def _validar_anti_intersecao(self):
        intersecao = set(self.dezenas_positivas) & set(self.dezenas_negativas)
        if intersecao:
            raise ValueError(
                f"A mesma dezena não pode ser selecionada simultaneamente como "
                f"favorita e rejeitada. Interseção encontrada: {sorted(intersecao)}"
            )
