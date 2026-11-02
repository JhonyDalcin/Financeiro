# Requisitos

A especificação completa (RF-001 a RF-026, regras de negócio, critérios de aceite e decisões Q1–Q15) está em [App Finanças – Requisitos Funcionais.md](<App Finanças – Requisitos Funcionais.md>) e é a **fonte de verdade**. Este arquivo é apenas um índice, com decisões de projeto que complementam a especificação. Não duplicar critérios de aceite aqui.

## 1. Objetivo

Planejar o orçamento anual, acompanhar o realizado, fechar meses e simular compras. O objeto central é o **Lançamento**, planejado ou realizado.

## 2. Perfis de usuário

| Perfil                       | Descrição                                                           |
| ---------------------------- | ------------------------------------------------------------------- |
| Usuário autenticado          | Acessa todas as funções e vê os dados de todos (sem isolamento, Q1) |
| Administrador (Django admin) | Gerencia usuários; não há auto-cadastro                             |

Não há entidade nem cadastro de famílias.

## 3. Índice de requisitos

Prioridade: **A** = essencial, **M** = média, **B** = baixa.

| Módulo            | Requisitos                     | Prio. | Fase do roadmap |
| ----------------- | ------------------------------ | ----- | --------------- |
| Cadastros         | RF-001 a RF-005                | A     | 1               |
| Usuários          | RF-006                         | A     | 1               |
| Lançamento        | RF-007 a RF-010                | A     | 2               |
| Planejamento      | RF-011 a RF-017, RF-026        | A     | 3               |
| Acompanhamento    | RF-019, RF-021 (A); RF-020 (M) | A/M   | 4               |
| Fechamento mensal | RF-022 a RF-024                | A     | 5               |
| Simulação         | RF-025                         | A     | 6               |
| Importação CSV    | RF-018                         | M     | 7               |

## 4. Requisitos não funcionais

Da especificação (RNF-01 a RNF-06) mais as decisões de projeto:

- **Segurança:** todas as telas exigem login; CSRF; HTTPS (Vercel); cookies `Secure` em produção; sem isolamento de dados entre usuários (Q1).
- **Integridade:** imutabilidade (RN-04) validada no backend.
- **Precisão:** valores em `Decimal`; diferença de centavos na última parcela (RF-008).
- **Desempenho:** grades anuais em até 2 s para até 5.000 lançamentos por ano.
- **Usabilidade:** planejamento otimizado para desktop/laptop; lançamento rápido, acompanhamento e fechamento utilizáveis no celular; tema Bootswatch Flatly (claro) e Darkly (escuro).
- **Hospedagem:** Vercel (serverless); PostgreSQL externo, pois o disco não persiste.
- **Localização:** PT-BR, BRL, fuso America/Sao_Paulo.
- **Qualidade:** testes para parcelamento, datas (meses curtos, bissexto), saldo e bloqueios.

## 5. Fora de escopo

- Exportação de relatórios (Q8); mantém-se apenas a importação CSV.
- Integração bancária (Open Finance), investimentos, multi-moeda, cadastro de famílias, isolamento por usuário.

## 6. Decisões de usuários

Isolamento, cadastro e senha resolvidos na especificação (RF-001, RF-006, RNF-01, Q1, Q11, Q12, Q13): sem isolamento, usuários criados no Django admin e senha esquecida redefinida pelo admin (sem e-mail/SMTP).

## 7. Perguntas em aberto

Nenhuma no momento (ver [dominio.md](dominio.md), seção 5).
