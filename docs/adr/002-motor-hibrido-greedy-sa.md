# ADR-002: Motor Híbrido Greedy + Simulated Annealing

**Status:** Aceito  
**Data:** 2026-08-17  

## Contexto

O sistema precisa gerar jogos de Lotofácil otimizados a partir de um ranking
de dezenas votadas pelos participantes. O motor deve respeitar a preferência
coletiva (ranking) e maximizar a dispersão entre jogos para cobrir o maior
número de combinações possíveis.

## Decisão

Utilizar um **motor híbrido** em duas etapas:
1. **Greedy Ponderado:** Gera uma distribuição inicial determinística respeitando
   quotas de aparição baseadas no ranking.
2. **Simulated Annealing:** Refina a distribuição greedy otimizando uma função
   de energia com 3 componentes: aderência ao ranking, dispersão de pares e
   cobertura combinatória.

## Alternativas Consideradas

| Alternativa | Motivo da rejeição |
|---|---|
| Greedy puro | Boa aderência ao ranking, mas dispersão subótima |
| Covering Design formal C(v,k,t) | NP-difícil para parâmetros genéricos, difícil generalizar |
| SA puro (sem seed greedy) | Convergência mais lenta, mais iterações necessárias |

## Consequências

### Positivas
- Qualidade superior de distribuição vs. greedy puro
- Execução rápida (~2 segundos para 9 jogos × 16 dezenas)
- Extensível (basta ajustar pesos da função de energia)
- Reproduzível com random.seed fixa
- Métricas de qualidade derivadas da função de energia

### Negativas
- ~110 linhas extras de código vs. greedy puro
- Não-determinístico por padrão (mitigado com seed fixa)
- Parâmetros do SA (temperatura, resfriamento) podem precisar de tuning
