"""
Fixtures compartilhadas para todos os testes do Bolão Lotofácil.
"""
import pytest
from datetime import datetime


@pytest.fixture
def participantes_dados():
    """Dados brutos de participantes para testes."""
    return [
        {"nome": "João Silva", "telefone_limpo": "11999998888", "status_voto": "Pendente", "nivel_acesso": "Participante"},
        {"nome": "Maria Santos", "telefone_limpo": "21988887777", "status_voto": "Pendente", "nivel_acesso": "Participante"},
        {"nome": "Carlos Admin", "telefone_limpo": "31977776666", "status_voto": "Pendente", "nivel_acesso": "Admin"},
        {"nome": "Ana Oliveira", "telefone_limpo": "41966665555", "status_voto": "Votou", "nivel_acesso": "Participante"},
    ]


@pytest.fixture
def config_padrao():
    """Configuração padrão do bolão para testes."""
    return {
        "status": "ABERTO",
        "quorum_alvo": 25,
        "qtd_jogos": 10,
        "dezenas_por_jogo": 16,
    }


@pytest.fixture
def votos_exemplo():
    """Lista de votos de exemplo para testes."""
    return [
        {"telefone_limpo": "11999998888", "dezenas_positivas": [1, 2, 3, 4, 5], "dezenas_negativas": [23, 24, 25], "data_hora": datetime(2026, 8, 17, 10, 0, 0)},
        {"telefone_limpo": "21988887777", "dezenas_positivas": [1, 2, 6, 7, 8], "dezenas_negativas": [23, 24, 25], "data_hora": datetime(2026, 8, 17, 10, 5, 0)},
        {"telefone_limpo": "31977776666", "dezenas_positivas": [1, 3, 5, 10, 15], "dezenas_negativas": [20, 21, 22], "data_hora": datetime(2026, 8, 17, 10, 10, 0)},
    ]
