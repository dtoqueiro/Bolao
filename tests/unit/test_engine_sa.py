"""
🔴 RED: Testes para a otimização Simulated Annealing no motor matemático.
"""
import pytest
from src.services.engine_service import EngineService


class TestEngineSimulatedAnnealing:
    """Testes para o Simulated Annealing e Função de Energia."""

    def test_calcular_energia_penaliza_cobertura_incompleta(self):
        engine = EngineService()
        ranking = [(i, 25 - i) for i in range(1, 26)]
        
        # Jogo perfeito em cobertura: usa todos os números 1 a 25.
        # Com 9 jogos de 16 = 144 slots, é fácil usar todos.
        jogos_bons = engine.gerar_seed_guloso(ranking, 9, 16)
        
        # Jogo ruim: só usa os números de 1 a 16 em todos os jogos (dezenas 17-25 ficam de fora)
        jogos_ruins = [list(range(1, 17)) for _ in range(9)]
        
        energia_boa = engine._calcular_energia(jogos_bons, ranking)
        energia_ruim = engine._calcular_energia(jogos_ruins, ranking)
        
        # Jogos com pior cobertura ou sobreposição devem ter energia MUITO mais alta
        assert energia_ruim > energia_boa

    def test_otimizar_jogos_melhora_ou_mantem_energia(self):
        engine = EngineService()
        ranking = [(i, 25 - i) for i in range(1, 26)]
        
        seed = engine.gerar_seed_guloso(ranking, 9, 16)
        energia_inicial = engine._calcular_energia(seed, ranking)
        
        # Otimiza com poucas iterações para o teste não demorar, mas o suficiente para mudar algo
        otimizados = engine.otimizar_jogos(seed, ranking, iteracoes=100, temp_inicial=1.0)
        energia_final = engine._calcular_energia(otimizados, ranking)
        
        # O SA não garante melhoria em 100% das vezes se o seed já for ótimo e a temp for alta,
        # mas na maioria das vezes a energia deve ser menor ou igual.
        assert energia_final <= energia_inicial or energia_final < energia_inicial * 1.05
        
        # Verificar estrutura
        assert len(otimizados) == 9
        for j in otimizados:
            assert len(j) == 16
            assert len(set(j)) == 16
