import sys
import os
import random
from collections import Counter

# Adiciona a raiz do projeto ao path para importar os modulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.engine_service import EngineService

def run_sanity_check():
    print("="*50)
    print(" SANITY CHECK - MOTOR MATEMÁTICO LOTOFÁCIL ")
    print("="*50)
    
    # 1. Mock Ranking
    # Criamos um ranking enviesado:
    # Top 5: Altíssima prioridade (Muitos votos positivos)
    # 6 a 15: Média prioridade (Alguns votos positivos)
    # 16 a 20: Neutras (Poucos votos ou saldo perto de zero)
    # 21 a 25: Rejeitadas (Votos negativos profundos)
    
    random.seed(42) # Seed fixa para o ranking ser reproduzível na apresentação
    
    ranking_nao_ordenado = []
    for d in range(1, 26):
        if d <= 5:
            saldo = random.randint(15, 25)
        elif d <= 15:
            saldo = random.randint(5, 14)
        elif d <= 20:
            saldo = random.randint(-4, 4)
        else:
            saldo = random.randint(-20, -5)
        ranking_nao_ordenado.append((d, saldo))
        
    # Ordenar ranking (maior saldo primeiro)
    ranking = sorted(ranking_nao_ordenado, key=lambda x: x[1], reverse=True)
    
    print("\n[+] Ranking Simulado (Top 5 e Bottom 5):")
    print("Top 5 favoritas:", ranking[:5])
    print("Bottom 5 rejeitadas:", ranking[-5:])
    
    qtd_jogos = 10
    dezenas_por_jogo = 16
    
    print(f"\n[+] Parâmetros: {qtd_jogos} Jogos de {dezenas_por_jogo} Dezenas")
    
    # 2. Gerar Jogos usando o motor (Greedy + SA)
    engine = EngineService()
    seed_jogos = engine.gerar_seed_guloso(ranking, qtd_jogos, dezenas_por_jogo)
    jogos = engine.otimizar_jogos(seed_jogos, ranking, iteracoes=2000)
    
    print("\n[+] Jogos Gerados:")
    for i, j in enumerate(jogos):
        print(f"Jogo {i+1:02d}: {sorted(j)}")
        
    # 3. Análise de Frequência
    todas_dezenas = []
    for j in jogos:
        todas_dezenas.extend(j)
    
    freq = Counter(todas_dezenas)
    print("\n[+] Análise de Frequência (Aparências por Dezena):")
    for d, saldo in ranking[:5]:
        print(f"  Top Dezena {d:02d} (Saldo {saldo:2d}): Apareceu {freq.get(d, 0):02d} vezes")
        
    print("  ...")
    for d, saldo in ranking[-5:]:
        print(f"  Bottom Dezena {d:02d} (Saldo {saldo:2d}): Apareceu {freq.get(d, 0):02d} vezes")
        
    # 4. Análise de Intersecção (Dispersão)
    interseccoes = []
    for i in range(len(jogos)):
        for j in range(i+1, len(jogos)):
            inter = len(set(jogos[i]).intersection(set(jogos[j])))
            interseccoes.append(inter)
            
    media_inter = sum(interseccoes) / len(interseccoes)
    max_inter = max(interseccoes)
    min_inter = min(interseccoes)
    
    print("\n[+] Análise de Ortogonalidade (Intersecção entre pares de jogos):")
    print(f"  Média Esperada p/ matriz aleatória: ~10.24")
    print(f"  Média Real (Motor): {media_inter:.2f}")
    print(f"  Mínima Intersecção: {min_inter}")
    print(f"  Máxima Intersecção: {max_inter} (Menor é melhor, evita sobreposição absurda)")
    
    # 5. Cobertura (Quantas dezenas únicas foram jogadas)
    cobertura = len(set(todas_dezenas))
    print(f"\n[+] Cobertura Global:")
    print(f"  {cobertura} dezenas únicas utilizadas na combinação dos {qtd_jogos} jogos.")
    print("="*50)

if __name__ == '__main__':
    run_sanity_check()
