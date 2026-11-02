# Arquitetura

## 1. Decisões

| Tema         | Decisão                                                                                                      |
| ------------ | ------------------------------------------------------------------------------------------------------------ |
| Framework    | Django 6.1 (monólito com templates)                                                                          |
| Banco        | SQLite (dev); PostgreSQL externo (produção, via `DATABASE_URL`)                                              |
| Frontend     | Templates + HTMX + Bootstrap 5 com Bootswatch Flatly/Darkly                                                  |
| Autenticação | `django.contrib.auth`; multiusuário sem isolamento (Q1); usuários criados no Django admin, sem auto-cadastro |
| Hospedagem   | Vercel (Python runtime, função serverless)                                                                   |
| Estáticos    | WhiteNoise; `collectstatic` automático na Vercel                                                             |
| Testes       | pytest + pytest-django                                                                                       |
| Lint/format  | ruff                                                                                                         |
| Config       | variáveis de ambiente (`.env`)                                                                               |

## 2. Apps Django planejados

| App              | Responsabilidade                                                                                                               | RFs                     |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------ | ----------------------- |
| `nucleo`         | Login/logout/troca de senha, templatetags (moeda/data), mixins, datas utilitárias (o `base.html` fica em `templates/` na raiz) | RF-006                  |
| `cadastros`      | Categoria, Subcategoria, PeriodoSalario, TipoPagamento, FonteCredito                                                           | RF-001 a RF-005         |
| `lancamentos`    | Lancamento, parcelamento, lançamento rápido, auditoria                                                                         | RF-007 a RF-010         |
| `planejamento`   | Planejamento, grade, visões, lote, revisões, receitas de salário, importação CSV                                               | RF-011 a RF-018, RF-026 |
| `acompanhamento` | Grade de realizados e comparativo planejado x realizado                                                                        | RF-019 a RF-021         |
| `fechamento`     | FechamentoMensal: iniciar, pagar, finalizar                                                                                    | RF-022 a RF-024         |
| `simulacao`      | Simulacao e LancamentoSimulado; motor de cálculo anual                                                                         | RF-025                  |

A grade (RN-06) e o cálculo de saldo são compartilhados por planejamento, acompanhamento e simulação; ficam em `selectors.py` reutilizáveis (ex.: `lancamentos/selectors.py`).

## 3. Estrutura de cada app

```
app/
  models.py
  services.py     # regras de negócio
  selectors.py    # consultas/agregações
  forms.py
  views.py
  urls.py
  templates/app/
  tests/
```

## 4. Fluxo de dependência

`views → services/selectors → models`. Models não importam views. Dependências entre apps: `planejamento`, `acompanhamento`, `fechamento` e `simulacao` dependem de `cadastros` e `lancamentos`; `lancamentos` depende de `cadastros`. Regras de imutabilidade (RN-04) e de parcelamento ficam em `services.py`, nunca nas views.

## 4.1 Interface dinâmica

- HTMX para recalcular a linha de Saldo e os totais sem recarregar a página (RF-012) e para os modais de edição com escolha de alcance (RF-015).
- A tela de planejamento é otimizada para telas largas; lançamento rápido, acompanhamento e fechamento devem funcionar no celular.
- Importação CSV (RF-018): processar em memória (sem gravar em disco, por causa da Vercel), separador `;`, UTF-8 com BOM, vírgula decimal.

## 5. Segurança

- Multiusuário **sem isolamento** (Q1): sem filtro por dono; autoria em `criado_por`/`modificado_por` (RN-02), preenchida pelo serviço a partir do `request.user`.
- Sem rota de auto-cadastro; usuários no Django admin (restringir `/admin/` a superusuários).
- Sem recuperação de senha por e-mail (Q13): não configurar SMTP; a senha esquecida é redefinida pelo admin; o usuário pode trocar a própria senha logado.
- Todas as views exigem login (`LoginRequiredMixin`), inclusive em produção pública.
- Em produção: `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT` e `CSRF_TRUSTED_ORIGINS` com o domínio da Vercel.
- Testes devem garantir que rotas anônimas redirecionam para o login e que o backend recusa edição de itens imutáveis.

## 5.1 Frontend e tema

- Bootstrap 5 com temas **Bootswatch Flatly** (claro) e **Darkly** (escuro).
- Carregar o CSS do tema a partir de arquivos locais em `static/vendor/` (Bootswatch 5.3.8, Bootstrap JS 5.3.8, HTMX 2.0.11), sem CDN; alternar entre os dois temas por botão (`static/js/tema.js`), guardando a escolha em `localStorage`.
- Não misturar com customizações pesadas; ajustes mínimos em `static/css/app.css`.

## 6. Configurações a ajustar em `financeiro/settings.py`

- `LANGUAGE_CODE = 'pt-br'`, `TIME_ZONE = 'America/Sao_Paulo'`.
- Ler `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` e `DATABASE_URL` do ambiente (SQLite se `DATABASE_URL` não existir).
- `WSGI_APPLICATION = 'financeiro.wsgi.application'`; `STATIC_ROOT` definido e WhiteNoise no middleware.

## 7. Implantação na Vercel

- A Vercel detecta `manage.py` e usa `WSGI_APPLICATION`; o app roda como uma única função serverless.
- **Banco:** SQLite não persiste na Vercel. Usar PostgreSQL (ex.: Neon/Supabase via Marketplace); a integração define `DATABASE_URL`. Dependência: `psycopg[binary]`.
- **Estáticos:** com `STATIC_ROOT` configurado, a Vercel executa `collectstatic` e serve pela CDN.
- **Migrations:** não rodam automaticamente; executar localmente apontando para o banco de produção (`vercel pull` gera `.env.local`; nunca versionar) e então `python manage.py migrate`.
- **Variáveis de ambiente (Vercel):** `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` (domínio `.vercel.app`/próprio), `CSRF_TRUSTED_ORIGINS`, `DATABASE_URL`.
- **Arquivos:** `requirements.txt` (ou `pyproject.toml`) na raiz; `vercel.json` só se precisar configurar a função (ex.: `maxDuration`).
- **Backups:** usar o backup do provedor do PostgreSQL; _definir periodicidade_.
- Limites serverless: sem tarefas em segundo plano nem gravação em disco; uploads, se houver, em storage externo.
