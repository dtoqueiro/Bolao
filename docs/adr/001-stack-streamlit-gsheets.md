# ADR-001: Stack Streamlit + Google Sheets

**Status:** Aceito  
**Data:** 2026-08-17  

## Contexto

Necessidade de construir um MVP rápido e gratuito para coleta de palpites
e geração de jogos de Lotofácil. O público-alvo é um grupo pequeno (~24 pessoas)
e o deploy precisa ser simples e sem custo.

## Decisão

Utilizar **Streamlit** como framework full-stack (front-end + back-end) com
**Google Sheets** como camada de persistência, hospedado no **Streamlit Community Cloud**.

## Alternativas Consideradas

| Alternativa | Motivo da rejeição |
|---|---|
| Flask + SQLite | Mais código boilerplate, deploy manual |
| Next.js + Supabase | Stack mais robusta, porém complexidade desnecessária para MVP |
| Django | Overhead excessivo para escopo do projeto |

## Consequências

### Positivas
- Deploy em minutos via GitHub
- Hosting gratuito (Streamlit Community Cloud)
- Prototipagem rápida com componentes prontos
- Google Sheets editável manualmente como backup

### Negativas
- Sem suporte nativo a concorrência (mitigado com retry + verificação)
- Sem autenticação robusta nativa
- Performance limitada para muitos usuários simultâneos
- Reruns do script a cada interação (gerenciado via session_state)
