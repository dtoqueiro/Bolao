"""
🔴 RED: Testes para o cálculo de ranking do motor matemático.
Escritos ANTES da implementação (TDD).
"""
import pytest
from src.models.voto import Voto
from src.services.engine_service import EngineService


class TestEngineRanking:
    """Testes de cálculo de ranking das dezenas."""

    def test_ranking_sem_votos(self):
        engine = EngineService()
        ranking = engine.calcular_ranking([])
        # Com 0 votos, todas as dezenas de 1 a 25 devem ter score 0
        assert len(ranking) == 25
        for dezena, score in ranking:
            assert score == 0

    def test_ranking_apenas_votos_positivos(self):
        engine = EngineService()
        votos = [
            Voto(telefone_limpo="111", dezenas_positivas=[1, 2, 3], dezenas_negativas=[]),
            Voto(telefone_limpo="222", dezenas_positivas=[1, 2], dezenas_negativas=[]),
            Voto(telefone_limpo="333", dezenas_positivas=[1], dezenas_negativas=[])
        ]
        ranking = engine.calcular_ranking(votos)
        # 1 recebeu 3 votos = 3
        # 2 recebeu 2 votos = 2
        # 3 recebeu 1 voto = 1
        scores = {dezena: score for dezena, score in ranking}
        assert scores[1] == 3
        assert scores[2] == 2
        assert scores[3] == 1
        assert scores[4] == 0
        
        # O ranking deve estar ordenado descendentemente
        assert ranking[0] == (1, 3)
        assert ranking[1] == (2, 2)
        assert ranking[2] == (3, 1)

    def test_ranking_com_votos_negativos(self):
        engine = EngineService()
        votos = [
            Voto(telefone_limpo="111", dezenas_positivas=[1, 2], dezenas_negativas=[24, 25]),
            Voto(telefone_limpo="222", dezenas_positivas=[1], dezenas_negativas=[25])
        ]
        ranking = engine.calcular_ranking(votos)
        scores = {dezena: score for dezena, score in ranking}
        assert scores[1] == 2
        assert scores[2] == 1
        assert scores[24] == -1
        assert scores[25] == -2
        
        # 1 no topo, 25 no fim
        assert ranking[0] == (1, 2)
        assert ranking[-1] == (25, -2)

    def test_ranking_empates(self):
        engine = EngineService()
        votos = [
            Voto(telefone_limpo="111", dezenas_positivas=[10, 20], dezenas_negativas=[])
        ]
        ranking = engine.calcular_ranking(votos)
        scores = {dezena: score for dezena, score in ranking}
        assert scores[10] == 1
        assert scores[20] == 1
        
        # Como 10 e 20 tem o mesmo score, a ordem entre eles não importa tanto,
        # mas ambos devem estar antes do score 0.
        top_dezenas = [d for d, s in ranking if s == 1]
        assert set(top_dezenas) == {10, 20}
