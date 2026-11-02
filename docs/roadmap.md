# Roadmap

Marque `[x]` ao concluir. Cada etapa deve incluir testes.

## Fase 0 – Base do projeto

- [x] Ajustar `settings.py` (pt-br, fuso, variáveis de ambiente, `DATABASE_URL`, WhiteNoise, `STATIC_ROOT`)
- [x] Criar `requirements.txt` (execução) e `requirements-dev.txt` (pytest-django, ruff), `.env.example`, `.gitignore` (incluir `.env.local`), `pytest.ini`, `ruff.toml`
- [x] Criar `README.md`
- [x] Template `templates/base.html` com Bootswatch Flatly/Darkly e alternância de tema (assets em `static/vendor/`, sem CDN)

## Fase 1 – Fundação e cadastros (RF-001 a RF-006)

- [x] App `nucleo`: login/logout/troca de senha (sem auto-cadastro), templatetags de moeda/data, utilitário de datas (dia ajustado ao último dia do mês)
- [x] App `cadastros`: Categoria, Subcategoria, TipoPagamento, FonteCredito, PeriodoSalario (com vigência)
- [x] Testes: rotas anônimas redirecionam ao login; inativar em vez de excluir; períodos sem sobreposição
- [ ] Primeiro deploy na Vercel com PostgreSQL; `migrate` e usuário inicial no banco de produção

## Fase 2 – Lançamento (RF-007 a RF-010)

- [ ] App `lancamentos`: modelo com auditoria (RN-02) e validações (RN-07)
- [ ] Serviço de parcelamento e `mes_fatura` por parcela (R$ 100,00 em 3x = 33,33 + 33,33 + 33,34; fechamento dia 10/vencimento dia 20)
- [ ] Lançamento rápido (mobile)
- [ ] Testes de datas (meses curtos, bissexto) e centavos

## Fase 3 – Planejamento (RF-011 a RF-017, RF-026)

- [ ] App `planejamento`: criar, estados e planejamento ativo
- [ ] Grade com linha de Saldo e visões Ano/Mês/Temporal (HTMX)
- [ ] Inserção em lote e edição por alcance (`serie_lote`)
- [ ] Confirmar e revisar (histórico de revisões)
- [ ] Receitas de salário vinculadas a período
- [ ] Testes de imutabilidade no backend (RN-04) e de um único planejamento não confirmado por ano (Q14)

## Fase 4 – Acompanhamento (RF-019 a RF-021)

- [ ] App `acompanhamento`: grade de realizados reutilizando a grade da Fase 3
- [ ] Comparativo planejado × realizado (RF-020, média)
- [ ] Criação/edição de realizados respeitando meses finalizados

## Fase 5 – Fechamento mensal (RF-022 a RF-024)

- [ ] App `fechamento`: iniciar (idempotente), pago/reabrir, finalizar
- [ ] Testes de bloqueio após finalizar (por `mes_fatura`)

## Fase 6 – Simulação (RF-025)

- [ ] App `simulacao`: motor de cálculo anual (realizado + planejado + parcelas em curso + simulado)
- [ ] Tela de resultado com saldo com/sem simulação
- [ ] Conversão em lançamentos reais (média, opcional)

## Fase 7 – Importação CSV e refinamentos (RF-018)

- [ ] Template CSV, validação linha a linha, importação atômica (`;`, UTF-8 BOM, vírgula decimal)
- [ ] Refinamentos de interface e desempenho (grade anual em até 2 s)

## Backlog / ideias

- _Registrar aqui._
