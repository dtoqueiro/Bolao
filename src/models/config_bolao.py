"""
Modelo de dados: Configuração do Bolão.

Representa os parâmetros configuráveis do bolão, gerenciados pelo
Administrador no painel de controle.
"""
from dataclasses import dataclass


# Limites de validação
STATUS_VALIDOS = ("ABERTO", "FECHADO")
QUORUM_MIN = 3
QUORUM_MAX = 50
JOGOS_MIN = 1
JOGOS_MAX = 30
DEZENAS_MIN = 15
DEZENAS_MAX = 20
COBERTURA_MINIMA = 50  # qtd_jogos * dezenas_por_jogo >= 50

# Tabela de preços da Lotofácil (dezenas -> preço em R$)
TABELA_PRECOS = {
    15: 3.50,
    16: 56.00,
    17: 476.00,
    18: 2856.00,
    19: 13566.00,
    20: 54264.00,
}


@dataclass
class ConfigBolao:
    """Configuração parametrizável do bolão Lotofácil.

    Attributes:
        status: Estado atual do bolão ("ABERTO" ou "FECHADO").
        quorum_alvo: Número de participantes que dispara encerramento automático.
        qtd_jogos: Quantidade de jogos (bilhetes) a serem gerados.
        dezenas_por_jogo: Quantidade de dezenas por jogo (15 a 20).
        nome_bolao: O nome de exibição do bolão na interface.
        login_telefone_habilitado: Se True, permite login usando número de telefone.
    """

    status: str = "ABERTO"
    quorum_alvo: int = 25
    qtd_jogos: int = 10
    dezenas_por_jogo: int = 16
    nome_bolao: str = "Bolão Lotofácil"
    login_telefone_habilitado: bool = False

    def __post_init__(self):
        """Validações executadas após a inicialização."""
        self._validar_status()
        self._validar_quorum()
        self._validar_qtd_jogos()
        self._validar_dezenas_por_jogo()
        self._validar_consistencia()

    def _validar_status(self):
        if self.status not in STATUS_VALIDOS:
            raise ValueError(
                f"Status inválido: '{self.status}'. "
                f"Valores aceitos: {STATUS_VALIDOS}"
            )

    def _validar_quorum(self):
        if not (QUORUM_MIN <= self.quorum_alvo <= QUORUM_MAX):
            raise ValueError(
                f"Quórum deve estar entre {QUORUM_MIN} e {QUORUM_MAX}. "
                f"Recebido: {self.quorum_alvo}."
            )

    def _validar_qtd_jogos(self):
        if not (JOGOS_MIN <= self.qtd_jogos <= JOGOS_MAX):
            raise ValueError(
                f"Quantidade de jogos deve estar entre {JOGOS_MIN} e {JOGOS_MAX}. "
                f"Recebido: {self.qtd_jogos}."
            )

    def _validar_dezenas_por_jogo(self):
        if not (DEZENAS_MIN <= self.dezenas_por_jogo <= DEZENAS_MAX):
            raise ValueError(
                f"Dezenas por jogo deve estar entre {DEZENAS_MIN} e {DEZENAS_MAX}. "
                f"Recebido: {self.dezenas_por_jogo}."
            )

    def _validar_consistencia(self):
        total = self.qtd_jogos * self.dezenas_por_jogo
        if total < COBERTURA_MINIMA:
            raise ValueError(
                f"Cobertura insuficiente: {self.qtd_jogos} jogos × "
                f"{self.dezenas_por_jogo} dezenas = {total} slots. "
                f"Mínimo necessário: {COBERTURA_MINIMA} slots "
                f"(média de 2 aparições por dezena)."
            )

    def esta_aberto(self) -> bool:
        """Verifica se o bolão está aberto para votação."""
        return self.status == "ABERTO"

    def total_slots(self) -> int:
        """Calcula o total de posições de dezenas em todos os jogos."""
        return self.qtd_jogos * self.dezenas_por_jogo

    def frequencia_media(self) -> float:
        """Calcula a frequência média de aparição de cada dezena."""
        return self.total_slots() / 25

    def custo_estimado(self) -> float:
        """Calcula o custo estimado total do bolão em R$."""
        preco_unitario = TABELA_PRECOS.get(self.dezenas_por_jogo, 0.0)
        return self.qtd_jogos * preco_unitario
