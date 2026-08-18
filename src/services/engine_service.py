"""
Motor Matemático para geração de jogos da Lotofácil.

Responsável por agregar votos, calcular o ranking de dezenas, 
gerar um seed guloso (greedy) e otimizá-lo via Simulated Annealing.
"""
from typing import List, Tuple
from collections import defaultdict

from src.models.voto import Voto


class EngineService:
    """Motor de geração e otimização de jogos."""

    def calcular_ranking(self, votos: List[Voto]) -> List[Tuple[int, int]]:
        """Calcula o ranking de todas as 25 dezenas com base nos votos.
        
        Regra:
        - Dezena positiva em um voto: +1 ponto
        - Dezena negativa em um voto: -1 ponto
        - Dezenas não votadas: 0 pontos
        
        Args:
            votos: Lista de todos os votos registrados.
            
        Returns:
            Lista de tuplas (dezena, score), ordenada do maior score para o menor.
            O tamanho da lista será sempre 25.
        """
        # Inicializa todas as 25 dezenas com score 0
        scores = {d: 0 for d in range(1, 26)}
        
        # Agrega os votos
        for voto in votos:
            for d in voto.dezenas_positivas:
                scores[d] += 1
            for d in voto.dezenas_negativas:
                scores[d] -= 1
                
        # Converte para lista de tuplas e ordena (score desc, dezena asc para desempate determinístico)
        # O `-score` garante ordem decrescente, e `d` crescente para empates
        ranking = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        
        return ranking

    def gerar_seed_guloso(self, ranking: List[Tuple[int, int]], qtd_jogos: int, dezenas_por_jogo: int) -> List[List[int]]:
        """Gera um conjunto inicial de jogos baseado no ranking.
        
        Usa uma abordagem gulosa com alocação proporcional aos pesos do ranking,
        garantindo que dezenas mais bem ranqueadas apareçam mais vezes.
        """
        total_slots = qtd_jogos * dezenas_por_jogo
        
        # Pesos lineares: o 1º do ranking tem peso 25, o último tem peso 1
        weights = [25 - i for i in range(25)]
        
        # Alocar as quotas para cada dezena
        quotas = {d: 0 for d, _ in ranking}
        for _ in range(total_slots):
            best_d = None
            min_prop = float('inf')
            for i, (d, _) in enumerate(ranking):
                if quotas[d] >= qtd_jogos:
                    continue # Cap: não pode aparecer mais vezes que o número de jogos
                
                # Proporção de preenchimento atual em relação ao peso desejado
                prop = quotas[d] / weights[i]
                if prop < min_prop:
                    min_prop = prop
                    best_d = d
                    
            if best_d is not None:
                quotas[best_d] += 1
                
        # Agora, distribuir as dezenas alocadas nos jogos
        jogos = [[] for _ in range(qtd_jogos)]
        dezenas_ordenadas = sorted(quotas.keys(), key=lambda x: -quotas[x])
        
        for d in dezenas_ordenadas:
            count = quotas[d]
            for _ in range(count):
                # Encontrar os jogos que ainda não têm essa dezena e não estão cheios
                jogos_validos = [g for g in jogos if d not in g and len(g) < dezenas_por_jogo]
                if not jogos_validos:
                    # Fallback caso não encontre (não deve ocorrer matematicamente se quotas bem distribuídas, mas por segurança)
                    jogos_validos = [g for g in jogos if d not in g]
                
                # Escolhe o jogo com menos dezenas atualmente para balancear
                jogos_validos.sort(key=len)
                jogos_validos[0].append(d)
                
        # Ordenar as dezenas dentro de cada jogo para ficar legível
        for jogo in jogos:
            jogo.sort()
            
        return jogos

    def _calcular_energia(self, jogos: List[List[int]], ranking: List[Tuple[int, int]]) -> float:
        """Função de custo para o Simulated Annealing (menor é melhor)."""
        qtd_jogos = len(jogos)
        if not jogos: return 0.0
        dezenas_por_jogo = len(jogos[0])
        total_slots = qtd_jogos * dezenas_por_jogo
        
        # 1. Calcular quotas ideais (usando mesma lógica do guloso)
        weights = [25 - i for i in range(25)]
        ideal_quotas = {d: 0 for d, _ in ranking}
        for _ in range(total_slots):
            best_d = None
            min_prop = float('inf')
            for i, (d, _) in enumerate(ranking):
                if ideal_quotas[d] >= qtd_jogos:
                    continue
                prop = ideal_quotas[d] / weights[i]
                if prop < min_prop:
                    min_prop = prop
                    best_d = d
            if best_d is not None:
                ideal_quotas[best_d] += 1
                
        # Frequências reais
        freqs = {i: 0 for i in range(1, 26)}
        for jogo in jogos:
            for d in jogo:
                freqs[d] += 1
                
        # Penalidade 1: Desvio das quotas ideais (Ranking)
        energia_quotas = sum((freqs[d] - ideal_quotas.get(d, 0)) ** 2 for d in range(1, 26))
        
        # Penalidade 2: Cobertura incompleta (todas as 25 dezenas devem idealmente aparecer)
        energia_cobertura = sum(50 for d in range(1, 26) if freqs[d] == 0)
        
        # Penalidade 3: Dispersão de pares
        from collections import defaultdict
        pair_counts = defaultdict(int)
        for jogo in jogos:
            for i in range(len(jogo)):
                for j in range(i + 1, len(jogo)):
                    pair = tuple(sorted([jogo[i], jogo[j]]))
                    pair_counts[pair] += 1
                    
        energia_pares = sum(count ** 2 for count in pair_counts.values())
        
        return energia_quotas + energia_cobertura + energia_pares * 0.1

    def otimizar_jogos(self, jogos: List[List[int]], ranking: List[Tuple[int, int]], iteracoes: int = 5000, temp_inicial: float = 10.0, taxa_resfriamento: float = 0.99) -> List[List[int]]:
        """Otimiza um conjunto de jogos usando Simulated Annealing."""
        import random
        import math
        import copy
        
        estado_atual = copy.deepcopy(jogos)
        energia_atual = self._calcular_energia(estado_atual, ranking)
        
        melhor_estado = copy.deepcopy(estado_atual)
        melhor_energia = energia_atual
        
        temp = temp_inicial
        
        for _ in range(iteracoes):
            if temp <= 0.01:
                break
                
            # Mutação
            novo_estado = copy.deepcopy(estado_atual)
            idx_jogo = random.randint(0, len(novo_estado) - 1)
            jogo_alvo = novo_estado[idx_jogo]
            
            dezena_remover = random.choice(jogo_alvo)
            disponiveis = [d for d in range(1, 26) if d not in jogo_alvo]
            dezena_adicionar = random.choice(disponiveis)
            
            jogo_alvo.remove(dezena_remover)
            jogo_alvo.append(dezena_adicionar)
            jogo_alvo.sort()
            
            nova_energia = self._calcular_energia(novo_estado, ranking)
            delta_e = nova_energia - energia_atual
            
            # Critério de aceitação de Metropolis
            if delta_e < 0 or random.random() < math.exp(-delta_e / temp):
                estado_atual = novo_estado
                energia_atual = nova_energia
                
                if energia_atual < melhor_energia:
                    melhor_energia = energia_atual
                    melhor_estado = copy.deepcopy(estado_atual)
                    
            temp *= taxa_resfriamento
            
        return melhor_estado
