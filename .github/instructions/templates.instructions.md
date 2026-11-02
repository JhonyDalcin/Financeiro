---
description: "Convenções de templates e frontend do app Financeiro."
applyTo: "**/templates/**/*.html"
---

- Textos de interface em PT-BR; `{% load humanize l10n %}` quando necessário.
- Herdar de `base.html`; componentes reutilizáveis em `templates/componentes/`.
- Usar Bootstrap 5 com os temas Bootswatch **Flatly** (claro) e **Darkly** (escuro); a alternância fica em `base.html` e a escolha é guardada em `localStorage`.
- Preferir classes utilitárias do Bootstrap; não usar cores fixas que quebrem em um dos temas.
- Formatar moeda com filtro/templatetag único (`R$ 1.234,56`); datas `dd/mm/aaaa`.
- Todo formulário com `{% csrf_token %}`; nunca usar `|safe` em dados do usuário.
- Valores de saldo negativo e diferenças planejado × realizado destacados de forma acessível (cor + texto/ícone).
- Grades (planejamento/acompanhamento): Receita/Despesa → Categoria → Subcategoria, meses em colunas, linha **Saldo** fixa sob o cabeçalho; atualizações parciais via HTMX.
- Itens imutáveis (confirmado, finalizado, pago) sem ícone de edição, com indicação visual.
- Planejamento otimizado para telas largas; lançamento rápido, acompanhamento e fechamento responsivos (celular); seguir `docs/telas.md`.
