# ADR-003: Login sem Autenticação Forte

**Status:** Aceito (risco aceito)  
**Data:** 2026-08-17  

## Contexto

O sistema precisa identificar participantes para controlar quem votou.
O grupo é pequeno (~24 pessoas) e confiável. Segurança robusta não é
prioridade nesta versão.

## Decisão

Login por **telefone** ou **nome completo**, sem PIN, senha ou OTP.
O participante escolhe o método de identificação preferido.

- Telefone: limpo via Regex (11 dígitos)
- Nome: normalizado (sem acentos, case-insensitive)

## Alternativas Consideradas

| Alternativa | Motivo da rejeição |
|---|---|
| PIN por participante | Atrito desnecessário para grupo confiável |
| OTP via WhatsApp/SMS | Complexidade e custo desnecessários para MVP |
| Google OAuth | Overhead e nem todos têm conta Google |

## Consequências

### Positivas
- Zero atrito no login
- Implementação simples
- Duas opções de identificação para conveniência

### Negativas
- Qualquer pessoa com telefone/nome de outro pode votar em seu nome
- Sem proteção contra votos maliciosos (risco aceito pelo grupo)
