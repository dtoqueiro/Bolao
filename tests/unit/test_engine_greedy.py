"""
🔴 RED: Testes para a geração de seed guloso no motor matemático.
"""
import pytest
from src.services.engine_service import EngineService


class TestEngineGreedySeed:
    """Testes de geração de seed inicial gulosa."""

    def test_gerar_seed_tamanho_correto(self):
        engine = EngineService()
        # Ranking fake (1 a 25) com scores arbitrários
        ranking = [(i, 25 - i) for i in range(1, 26)]
        
        jogos = engine.gerar_seed_guloso(ranking, qtd_jogos=9, dezenas_por_jogo=16)
        
        assert len(jogos) == 9
        for jogo in jogos:
            assert len(jogo) == 16
            assert len(set(jogo)) == 16 # Sem repetições no mesmo jogo
            # Deve ser de 1 a 25
            for d in jogo:
                assert 1 <= d <= 25

    def test_gerar_seed_respeita_ranking(self):
        """As dezenas do topo do ranking devem aparecer mais que as do fundo."""
        engine = EngineService()
        ranking = [(i, 25 - i) for i in range(1, 26)] # 1 é topo, 25 é fundo
        
        jogos = engine.gerar_seed_guloso(ranking, qtd_jogos=9, dezenas_por_jogo=16)
        
        # Conta a frequência de cada dezena
        freqs = {i: 0 for i in range(1, 26)}
        for jogo in jogos:
            for d in jogo:
                freqs[d] += 1
                
        # A dezena 1 (topo) deve ter uma frequência maior ou igual à dezena 25 (fundo)
        assert freqs[1] >= freqs[25]
        
        # A soma de todas as frequências deve ser 9 * 16 = 144
        assert sum(freqs.values()) == 144
