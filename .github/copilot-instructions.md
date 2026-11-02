# Instruções do Copilot – Financeiro

## Visão geral

Aplicativo web de finanças pessoais/familiares: **planejar o orçamento anual, acompanhar o realizado, fechar meses e simular compras**. O objeto central é o **Lançamento**, planejado ou realizado.
Sistema **multiusuário sem isolamento de dados** (todos os usuários autenticados veem os mesmos dados); usuários são criados no Django admin. Não há cadastro de famílias nem auto-cadastro.

**Fonte de verdade dos requisitos:** `docs/App Finanças – Requisitos Funcionais.md` (RF-001 a RF-026, RN-01 a RN-07, decisões Q1–Q15). Demais documentos em `docs/`: `requisitos.md` (índice), `dominio.md` (modelo e algoritmos), `arquitetura.md`, `telas.md`, `roadmap.md`. Consulte-os antes de implementar e atualize-os quando o comportamento mudar; se divergirem da especificação, a especificação prevalece.

## Stack

- Python 3 + Django 6.1 (projeto `financeiro`, `manage.py` na raiz).
- Banco: SQLite em desenvolvimento; PostgreSQL em produção via `DATABASE_URL` (SQLite se a variável não existir).
- Frontend: templates Django + HTMX + Bootstrap 5 com temas **Bootswatch Flatly (claro) e Darkly (escuro)** (sem SPA, salvo decisão em `docs/arquitetura.md`).
- Hospedagem: **Vercel** (função serverless; ver `docs/arquitetura.md`, seção Implantação). Estáticos com WhiteNoise.
- Testes: `pytest` + `pytest-django`. Lint/format: `ruff`.
- Ambiente virtual em `venv/` (não editar nem versionar).

## Idioma

- Interface, mensagens, textos de documentação, commits e comentários: **PT-BR**.
- Nomes de modelos, campos, funções e variáveis: **português sem acentos** (ex.: `Lancamento`, `data_compra`), para manter consistência com `docs/dominio.md`.
- `LANGUAGE_CODE = 'pt-br'`, `TIME_ZONE = 'America/Sao_Paulo'`, `USE_TZ = True`.
- Datas `dd/mm/aaaa`; moeda BRL formatada `R$ 1.234,56`.

## Regras financeiras (obrigatórias)

- Valores monetários sempre em `DecimalField(max_digits=12, decimal_places=2)`. **Nunca `float`** (RN-01).
- Lançamento tem `situacao` PLANEJADO ou REALIZADO (entidades distintas, RN-03); a natureza (RECEITA/DESPESA) vem da categoria; valores são positivos.
- Todo lançamento registra `criado_em`, `modificado_em`, `criado_por` e `modificado_por` (RN-02), preenchidos pela camada de serviço.
- Saldo do período = receitas − despesas (RN-05). Grades agrupam Receita/Despesa → Categoria → Subcategoria, com meses em colunas (RN-06).
- Crédito exige fonte e parcelas ≥ 1 (RN-07). Parcelamento: centavos de diferença na última parcela (R$ 100,00 em 3x = 33,33 + 33,33 + 33,34); parcelas no dia de vencimento da fonte.
- Dia inexistente no mês (31 em abril, 29/02) usa o último dia do mês.
- O mês de um lançamento nas grades, no fechamento e na simulação é o **mês da fatura** (`mes_fatura`), não o mês de `data_compra` (RN-08).
- No mesmo ano só pode haver um planejamento não confirmado (em elaboração ou em revisão).
- Planejamento confirmado, mês finalizado e lançamento pago são **imutáveis** (RN-04): validar no backend (`services.py`), não só ocultar ícones.
- Categoria, subcategoria e fonte de crédito em uso só podem ser inativadas, nunca excluídas.
- Simulação usa tabelas próprias e nunca altera planejamento nem realizado.
- Não existe entidade `Familia` nem FK de dono. Não criar telas de cadastro de usuário/família.

## Arquitetura e convenções

- Apps: `nucleo`, `cadastros`, `lancamentos`, `planejamento`, `acompanhamento`, `fechamento`, `simulacao` (ver `docs/arquitetura.md`). A lógica de grade e saldo é compartilhada, não duplicada.
- Lógica de negócio em `services.py` de cada app; views finas; consultas complexas em `selectors.py`/managers.
- Preferir class-based views; formulários em `forms.py`; URLs com `app_name` e nomes em português (`lancamento_criar`).
- Evitar N+1 (`select_related`/`prefetch_related`) e usar `transaction.atomic` em operações com mais de uma escrita.
- Toda alteração de modelo gera migration; nunca editar migrations já aplicadas.
- Segredos e configurações sensíveis via variáveis de ambiente (`.env`, com `.env.example` versionado). Não commitar `SECRET_KEY`.
- Respeitar proteções do Django: CSRF, `LoginRequiredMixin` em todas as views, validação em forms (OWASP Top 10).
- Compatível com Vercel: não gravar em disco, não depender de processos em segundo plano, migrations executadas manualmente contra o banco de produção, nenhum segredo versionado (`.env.local` no `.gitignore`).
- Frontend: usar classes do Bootstrap 5 e os temas Flatly/Darkly; evitar CSS próprio além de ajustes mínimos. Planejamento otimizado para desktop; lançamento rápido, acompanhamento e fechamento utilizáveis no celular. HTMX para recalcular saldo e totais sem recarregar a página.
- Importação CSV processada em memória (sem gravar em disco).

## Testes

- Toda funcionalidade nova ou correção inclui testes (`pytest`), com nomes descritivos em PT-BR.
- Cobrir parcelamento e centavos, datas (meses curtos, ano bissexto), saldo, bloqueios de imutabilidade no backend e acesso protegido por login.
- Rodar: `pytest` e `ruff check .` antes de concluir.

## Comandos

```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
python manage.py makemigrations; python manage.py migrate
pytest
ruff check . ; ruff format .
```

## Como trabalhar

- Implemente uma fase/requisito por vez, seguindo `docs/roadmap.md` e citando o ID (ex.: RF-008) da especificação; inclua testes junto com o código e migrations pequenas por fase.
- Em caso de ambiguidade de regra de negócio, consulte a especificação e `docs/dominio.md`; se ainda faltar informação, pergunte antes de assumir.
- Não adicionar funcionalidades fora do escopo do roadmap sem confirmação.
