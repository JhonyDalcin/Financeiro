---
description: "Convenções de testes (pytest-django) do app Financeiro."
applyTo: "**/{tests,test_*.py,*_test.py,conftest.py}"
---

- Usar `pytest` + `pytest-django`; fixtures em `conftest.py` (usuário logado, categoria, subcategoria, tipo de pagamento, fonte de crédito, planejamento).
- Nomes de testes descritivos em PT-BR: `test_parcelamento_aplica_centavos_na_ultima_parcela`.
- Cobrir: parcelamento (R$ 100,00 em 3x = 33,33 + 33,33 + 33,34), mês da 1ª fatura (fecha dia 10/vence dia 20: 05/10 → 20/10; 15/10 → 20/11), datas (meses curtos, bissexto), saldo, inserção em lote e edição por alcance, idempotência do fechamento.
- Testar no backend que planejamento confirmado, mês finalizado e lançamento pago recusam edição/exclusão.
- Testar que views exigem login (anônimo é redirecionado).
- Usar `Decimal("10.00")`, nunca `float`; datas fixas, sem depender de `date.today()`.
