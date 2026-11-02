---
description: "Regras para models, migrations e services do Django no app Financeiro."
applyTo: "**/{models,services,selectors,managers}.py"
---

- Valores monetários: `DecimalField(max_digits=12, decimal_places=2)`; nunca `float`.
- Sem `Familia` nem FK de dono (multiusuário sem isolamento); definir `Meta.ordering` explícito.
- Lançamento: campos de auditoria `criado_em`, `modificado_em`, `criado_por`, `modificado_por` (RN-02); `situacao` PLANEJADO/REALIZADO.
- Usar `TextChoices` para `tipo` e `status`; `verbose_name` em PT-BR; `__str__` legível.
- Constraints e índices em `Meta` (ex.: valor > 0; nome de categoria único por natureza; subcategoria única por categoria; (ano, revisao) único em Planejamento; (ano, mes) único em FechamentoMensal).
- Regras de negócio em `services.py`, com `transaction.atomic` quando houver múltiplas escritas (parcelas, lote, confirmar/revisar, iniciar fechamento).
- Imutabilidade (planejamento confirmado, mês finalizado, lançamento pago) validada nos serviços; nunca confiar apenas na interface.
- Nunca excluir fisicamente categoria, subcategoria ou fonte em uso; usar `ativa = False`.
- Usar `select_related`/`prefetch_related` para evitar N+1.
- Compatível com PostgreSQL (produção na Vercel) e SQLite (dev); evitar recursos específicos de um só banco.
- Seguir `docs/dominio.md`; se o modelo mudar, atualizar o documento.
