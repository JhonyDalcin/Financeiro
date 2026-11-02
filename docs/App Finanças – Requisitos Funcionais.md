# App Finanças – Especificação de Requisitos Funcionais

Documento derivado do `memorial.txt`, estruturado para ser usado como insumo de desenvolvimento assistido por IA (Claude Sonnet 5.5). Versão 1.1 (respostas às perguntas em aberto incorporadas) – 30/10/2026.

## 1. Visão geral

Aplicação web de finanças pessoais para planejar o orçamento anual, acompanhar o que foi realizado, fechar meses e simular compras. O objeto central é o **Lançamento**, que pode ser **planejado** ou **realizado**.

**Premissas técnicas (derivadas do memorial):**

- Backend em Django, com autenticação padrão do Django (`django.contrib.auth`).
- Interface web responsiva. A tela de Planejamento é otimizada para laptop e desktop; as demais (acompanhamento, fechamento, lançamento rápido) devem funcionar bem em celular.
- Moeda única: Real (BRL). Idioma da interface: português do Brasil.
- Sugestão (a confirmar): PostgreSQL, Django Templates com HTMX ou Django + API REST com front separado.

## 2. Glossário

| Termo                     | Definição                                                                               |
| ------------------------- | --------------------------------------------------------------------------------------- |
| Categoria                 | Agrupador de lançamentos (ex.: Moradia, Alimentação). Tem natureza Receita ou Despesa.  |
| Subcategoria              | Detalhe obrigatoriamente ligado a uma categoria (ex.: Moradia – Aluguel).               |
| Visão temporal de salário | Divisão do mês em períodos de recebimento (ex.: Vale dia 15 e Pagamento dia 30).        |
| Tipo de pagamento         | Forma de pagamento: Dinheiro, Digital, Crédito etc.                                     |
| Fonte de crédito          | Cartão ou fonte com dia de vencimento de fatura (ex.: Santander).                       |
| Planejamento              | Orçamento anual com revisões numeradas. Estados: Em elaboração, Em revisão, Confirmado. |
| Planejamento ativo        | O planejamento confirmado mais recente do ano.                                          |
| Fechamento mensal         | Processo que consolida os lançamentos realizados de um mês e o trava.                   |
| Simulação                 | Cenário hipotético de compra que não altera dados reais.                                |

## 3. Perfis de usuário

- **Usuário autenticado**: acessa todas as funções e enxerga os dados de todos os usuários (sem isolamento).
- **Administrador (Django admin)**: gerencia usuários.

_Decisão:_ o sistema é único e multiusuário, sem isolamento de dados. Categorias, planejamentos e lançamentos são compartilhados entre todos os usuários autenticados; a autoria é registrada pelos campos de criador e modificador (RN-02).

## 4. Regras de negócio transversais

- **RN-01** Todo valor monetário usa `Decimal` com 2 casas decimais; nunca `float`.
- **RN-02** Todo lançamento registra data de criação, data de modificação, usuário criador e usuário modificador.
- **RN-03** Lançamento planejado e lançamento realizado são entidades distintas conceitualmente, mesmo quando o realizado nasce de um planejado.
- **RN-04** Planejamento confirmado e mês finalizado são imutáveis (nem edição, nem exclusão de lançamentos).
- **RN-05** Saldo do período = soma das receitas – soma das despesas.
- **RN-06** Telas de grade (planejamento e acompanhamento) agrupam por Receita/Despesa, depois por Categoria, depois por Subcategoria, com meses em colunas.
- **RN-07** Lançamento com tipo de pagamento Crédito exige fonte de crédito e número de parcelas (≥ 1).
- **RN-08** O mês de um lançamento nas grades, visões, fechamento mensal e simulação é o **mês da fatura**, não o mês da data da compra (ver RF-007).

## 5. Requisitos funcionais

Prioridade: **A** = essencial, **M** = média, **B** = baixa.

### 5.1 Módulo Cadastros

**RF-001 – Cadastro de Categoria (A)**

- CRUD de categorias com nome e natureza (Receita ou Despesa).
- Nome único por natureza (sem isolamento por usuário, Q1).
- _Critérios de aceite:_ não é possível excluir categoria que tenha subcategorias ou lançamentos; o sistema oferece inativá-la.

**RF-002 – Cadastro de Subcategoria (A)**

- CRUD de subcategorias com nome e categoria obrigatória.
- Nome único dentro da categoria.
- Exibição sempre no formato "Categoria – Subcategoria".
- _Critérios de aceite:_ não é possível salvar sem categoria; não é possível excluir subcategoria com lançamentos (apenas inativar).

**RF-003 – Cadastro de visão temporal de recebimento de salário (A)**

- CRUD de períodos, cada um com nome, dia do mês de recebimento, dia inicial e dia final do intervalo que cobre e descrição.
- Exemplos: _Vale_ – recebimento dia 15, cobre os dias 1–15; _Pagamento_ – recebimento dia 30, cobre os dias 16–31. Valores como o percentual do vale ou o desconto do adiantamento não são cadastrados: são digitados nos lançamentos de receita (RF-026).
- A regra de corte é definida no próprio cadastro, pois pode mudar com a empresa: o conjunto de períodos tem vigência (data inicial e final) e pode haver um único período (pagamento mensal único).
- Na visão temporal (RF-013), despesas entram no período pela data de vencimento (RF-007) e receitas de salário entram no período ao qual foram vinculadas (RF-026).
- _Critérios de aceite:_ dias entre 1 e 31; em meses curtos o dia é ajustado para o último dia do mês; os períodos vigentes não se sobrepõem e juntos cobrem todos os dias do mês; ao trocar de empresa, encerra-se a vigência atual e cria-se um novo conjunto, sem alterar meses passados.

**RF-004 – Cadastro de tipo de pagamento (A)**

- CRUD de tipos (ex.: Dinheiro, Digital, Crédito).
- Cada tipo possui o atributo "é crédito", que ativa os campos de fonte e parcelas no lançamento.

**RF-005 – Cadastro de fonte de crédito (A)**

- CRUD com: nome da fonte (ex.: Santander), tipo (Cartão de crédito, Empréstimo ou outro), dia de vencimento (1 a 31) e, apenas para cartão de crédito, dia de fechamento da fatura (melhor dia de compra).
- O mês de vencimento não é campo da fonte: o vencimento é mensal e recorrente, e o mês da primeira parcela é indicado no lançamento (RF-008).
- Empréstimos e demais fontes que não são cartão não têm dia de fechamento.
- _Critérios de aceite:_ os dias de vencimento e de fechamento devem existir no mês; se não existirem (ex.: 31 em abril), valem o último dia do mês; para cartão o dia de fechamento é opcional (se vazio, a compra entra na próxima fatura a vencer); fontes usadas em lançamentos só podem ser inativadas.

### 5.2 Módulo Usuários

**RF-006 – Autenticação e usuários (A)**

- Usar o padrão Django: login, logout e troca de senha pelo próprio usuário logado. Não há recuperação de senha por e-mail: em caso de esquecimento, a senha é redefinida pelo administrador no Django admin (Q13). Não há auto-cadastro: os usuários são criados e gerenciados no Django admin (Q11).
- Todas as telas exigem login.
- _Critérios de aceite:_ usuário não autenticado é redirecionado ao login; senhas seguem os validadores padrão do Django.

### 5.3 Módulo Lançamento (objeto principal)

**RF-007 – Entidade Lançamento (A)** Campos: data de criação, data de modificação, usuário que criou, usuário que modificou, situação (planejado ou realizado), categoria, subcategoria, data da compra, valor em reais, tipo de pagamento e, se crédito, fonte de pagamento, número de parcelas e mês da primeira fatura; nas receitas de salário, também o período de recebimento (ex.: Vale, Pagamento). Opcionais sugeridos: descrição e flag "pago" (usada no fechamento).

- Todo lançamento tem um **mês da fatura** (competência), que define em que mês ele aparece nas grades, visões, fechamento e simulação (RN-08). Sem crédito, é o mês da data da compra; no crédito, cada parcela tem o seu (mês da primeira fatura + n − 1), enquanto a data da compra é a mesma em todas as parcelas.
- A **data de vencimento** (usada na visão temporal, RF-013) é: no crédito, o dia de vencimento da fonte no mês da fatura; nos demais casos, a data da compra.
- _Critérios de aceite:_ valor maior que zero; a subcategoria deve pertencer à categoria; a natureza (receita/despesa) vem da categoria.

**RF-008 – Parcelamento no crédito (A)**

- Ao informar tipo Crédito, o usuário informa fonte e número de parcelas.
- O mês da 1ª parcela (primeira fatura) é sugerido automaticamente e pode ser editado. Cartão com dia de fechamento: compra feita até o fechamento entra na fatura que vence logo após esse fechamento; compra posterior vai para a fatura seguinte. Empréstimo ou cartão sem fechamento: o usuário informa o mês da primeira parcela (padrão = próximo vencimento).
- As demais parcelas caem nas faturas dos meses seguintes (mês da fatura), com vencimento sempre no dia de vencimento da fonte; a data da compra é a mesma em todas as parcelas.
- O valor total é dividido em parcelas; a diferença de centavos é aplicada à última parcela.
- _Critérios de aceite:_ compra de R$ 100,00 em 3x gera 33,33 + 33,33 + 33,34; cartão que fecha dia 10 e vence dia 20: compra em 05/10 entra na fatura de 20/10 e compra em 15/10 na de 20/11; as parcelas ficam vinculadas entre si (mesmo grupo) e mostram "parcela n/N".

**RF-009 – Pontos de criação do lançamento (A)** O lançamento pode ser criado ou editado a partir de: Planejamento, Acompanhamento, Fechamento mensal e do lançamento rápido (RF-010). O formulário se adapta ao contexto (planejado ou realizado).

**RF-010 – Lançamento rápido (A)**

- Tela ou botão flutuante, otimizado para celular, para registrar uma compra assim que ela acontece.
- Campos mínimos: valor, subcategoria, tipo de pagamento (e fonte/parcelas se crédito). Data da compra padrão = hoje; situação padrão = realizado.
- _Critérios de aceite:_ registro em no máximo 4 toques/campos além do valor; a subcategoria e o tipo de pagamento mais recentes são sugeridos.

### 5.4 Módulo Planejamento Financeiro (desktop)

**RF-011 – Criar planejamento (A)**

- Ao acessar a área, o usuário escolhe: Criar planejamento, Revisar planejamento ou Importar CSV.
- Ao criar, seleciona o ano; o sistema abre a grade (RF-012) com o planejamento em estado "Em elaboração".
- _Critérios de aceite:_ não pode haver mais de um planejamento não confirmado ("em elaboração" ou "em revisão") para o mesmo ano; é permitido um novo ano mesmo sem planejamento do ano anterior.

**RF-012 – Grade do planejamento (A)**

- Colunas: Subcategorias (agrupadas por categoria, agrupadas por Receita/Despesa) e os meses (mês da fatura, RN-08).
- Linha fixa **Saldo** logo abaixo do cabeçalho, fixa ao rolar, com receita – despesa por mês.
- Totais por categoria e por grupo (Receita, Despesa).
- _Critérios de aceite:_ o Saldo se recalcula ao inserir, editar ou excluir lançamentos sem recarregar a página inteira.

**RF-013 – Modos de visualização (A)** Presente no planejamento e no acompanhamento:

- **Visão Ano**: lançamentos por mês do ano.
- **Visão Mês**: lançamentos de um mês escolhido.
- **Visão Temporal de salário**: lançamentos por mês, subdivididos conforme os períodos cadastrados em RF-003 (ex.: Vale / Pagamento).
- O usuário alterna entre as visões sem perder o contexto (ano, filtros).

**RF-014 – Inserir lançamentos no planejamento (A)**

- O usuário informa os dados do lançamento e seleciona os meses em que ele ocorre.
- O sistema gera um lançamento planejado por mês selecionado, preservando o **dia** da data da compra informada.
- Exemplo: data 15/01/2027 com meses Janeiro, Fevereiro e Março gera 15/01/2027, 15/02/2027 e 15/03/2027.
- _Critérios de aceite:_ se o dia não existe no mês (ex.: 31 em fevereiro), usa o último dia do mês; os meses devem pertencer ao ano do planejamento.

**RF-015 – Editar lançamento do planejamento (A)**

- Ícone de edição discreto (pequeno) ao lado de cada lançamento.
- Edição permitida somente com planejamento "Em elaboração" ou "Em revisão"; nunca em "Confirmado" (o ícone fica oculto e o backend recusa).
- Em lançamentos criados em lote (RF-014), ao salvar o sistema pergunta o alcance da edição, como nas ocorrências do Google Agenda: "Somente este lançamento", "Este e os seguintes" ou "Todos os lançamentos da série".
- _Critérios de aceite:_ lançamentos criados na mesma inserção em lote compartilham um identificador de série; a edição altera apenas os campos modificados no formulário, preservando os demais campos de cada ocorrência; nas opções "Este e os seguintes" e "Todos os lançamentos da série", os campos alterados sobrescrevem também ajustes feitos individualmente nas ocorrências afetadas; a data de cada mês mantém o dia conforme RF-014.

**RF-016 – Confirmar planejamento (A)**

- Ação que muda o estado para "Confirmado" e o define como planejamento ativo do ano.
- Após confirmado, torna-se somente leitura.
- _Critérios de aceite:_ pede confirmação explícita; ao confirmar uma revisão, a anterior deixa de ser ativa e fica no histórico.

**RF-017 – Revisar planejamento (A)**

- Gera uma nova revisão numerada (Rev. 1, 2, 3...) copiando o planejamento ativo anterior.
- Pode ser editada e receber novos lançamentos; depois é confirmada pela mesma função de RF-016.
- _Critérios de aceite:_ a revisão não altera a anterior; o histórico de revisões é listado com data e usuário; a revisão copia apenas lançamentos planejados; não é possível criar revisão enquanto houver outro planejamento não confirmado no mesmo ano.

**RF-018 – Importação e template CSV (M)**

- Download de template CSV preenchível no Excel (colunas: ano, mês da fatura, data da compra, categoria, subcategoria, valor, tipo de pagamento, fonte, parcelas).
- Upload do arquivo preenchido para criar lançamentos em um planejamento em elaboração.
- _Critérios de aceite:_ validação linha a linha com relatório de erros (linha e motivo) antes de gravar; importação atômica (tudo ou nada) ou com confirmação das linhas válidas; aceita separador `;` e codificação UTF-8 com BOM, comum no Excel brasileiro, e vírgula decimal.

**RF-026 – Lançamento de receitas de salário (A)**

- Receitas de salário são lançadas manualmente, sem geração automática nem cálculo: o usuário cria um lançamento de receita para cada recebimento (ex.: um do tipo Vale e outro do tipo Pagamento), com a data em que ocorre e o valor.
- Cada receita de salário é vinculada a um período do RF-003 (Vale, Pagamento...) e, na visão temporal, aparece no período ao qual foi vinculada.
- Com pagamento único, basta um período.
- _Critérios de aceite:_ o valor do Pagamento é digitado já com o desconto do vale; a inserção em lote (RF-014) permite repetir a receita em vários meses; a receita de salário exige período vinculado.

### 5.5 Módulo Acompanhamento Financeiro

**RF-019 – Tela de acompanhamento (A)**

- Abre automaticamente a grade com as mesmas colunas e linha de Saldo do RF-012, com os valores **realizados**.
- Suporta as 3 visões do RF-013.
- Planejado e realizado são tratados como coisas diferentes.

**RF-020 – Comparativo planejado × realizado (M)**

- Exibir, por subcategoria e mês, planejado, realizado e diferença.
- _Premissa:_ não está explícito no memorial, mas decorre do objetivo de acompanhar o plano.

**RF-021 – Registro de lançamentos na tela de acompanhamento (A)**

- Permitir criar e editar lançamentos realizados, respeitando o bloqueio de meses finalizados (RF-023).

### 5.6 Módulo Fechamento Mensal

**RF-022 – Iniciar fechamento (A)**

- O usuário escolhe o mês e clica em **Iniciar**.
- O sistema carrega os lançamentos do mês (mês da fatura, RN-08) como **realizados**, copiados do planejamento ativo com as mesmas informações.
- O usuário pode escolher a visão temporal de salário dentro do mês (RF-003).
- _Critérios de aceite:_ a ação é idempotente (não duplica lançamentos se executada de novo); lançamentos já realizados no mês não são sobrescritos.

**RF-023 – Edição e pagamento durante o fechamento (A)**

- Cada lançamento executado tem ícone de editar.
- Ao editar ou criar um lançamento no mês, há a opção **Pago**; ao marcar, o lançamento é concluído e não pode mais ser editado.
- _Critérios de aceite:_ lançamento marcado como pago é somente leitura (backend também recusa); ele pode ser reaberto (desmarcar Pago) enquanto o mês não estiver finalizado, voltando a ser editável.

**RF-024 – Finalizar mês (A)**

- Ação **Finalizar mês** que torna o mês definitivamente não editável.
- _Critérios de aceite:_ pede confirmação; exibe aviso se houver lançamentos não pagos; após finalizar, nenhum lançamento daquele mês (mês da fatura) pode ser criado, editado ou excluído.

### 5.7 Módulo Simulação

**RF-025 – Simulação de lançamento (A)**

- O usuário cria uma compra hipotética (valor, data da compra, categoria/subcategoria, tipo de pagamento, fonte e parcelas) sem gravá-la como lançamento real.
- Ex.: compra parcelada em março, paga nas faturas de abril a dezembro.
- A tela de resultado mostra o ano completo combinando:
  1. meses já passados: valores **realizados**;
  2. meses futuros: valores **planejados**;
  3. mais as **parcelas já realizadas** de compras parceladas ainda em curso;
  4. mais a **simulação**.
- Saldo por mês com e sem a simulação, e a diferença.
- _Critérios de aceite:_ a simulação não altera planejamento nem realizado; é possível simular várias compras em conjunto e descartá-las; opcionalmente é possível convertê-la em lançamentos reais (M).

## 6. Requisitos não funcionais essenciais

- **RNF-01 Segurança:** acesso apenas autenticado; proteção CSRF; sem isolamento de dados entre usuários (Q1).
- **RNF-02 Integridade:** regras de imutabilidade (RN-04) aplicadas no backend, não só na interface.
- **RNF-03 Desempenho:** grades anuais carregam em até 2 segundos para até 5.000 lançamentos por ano.
- **RNF-04 Usabilidade:** planejamento otimizado para telas largas; lançamento rápido e acompanhamento utilizáveis em celular.
- **RNF-05 Auditoria:** registro de quem criou e alterou (RN-02); histórico das revisões.
- **RNF-06 Qualidade:** testes automatizados para regras de parcelamento, datas (meses curtos, bissexto), saldo e bloqueios.

## 7. Modelo de dados sugerido (alto nível)

- `Categoria(nome, natureza, ativa)`
- `Subcategoria(nome, categoria, ativa)`
- `PeriodoSalario(nome, dia_recebimento, dia_inicio, dia_fim, vigencia_inicio, vigencia_fim)`
- `TipoPagamento(nome, eh_credito)`
- `FonteCredito(nome, tipo, dia_vencimento, dia_fechamento?)`
- `Planejamento(ano, revisao, estado, ativo)`
- `FechamentoMensal(ano, mes, estado)`
- `Lancamento(situacao, planejamento?, fechamento?, categoria, subcategoria, data_compra, valor, tipo_pagamento, fonte?, mes_fatura, periodo_salario?, parcela_numero?, parcela_total?, grupo_parcelas?, serie_lote?, pago, criado_em, modificado_em, criado_por, modificado_por)`
- `Simulacao(nome)` e `LancamentoSimulado(...)`, separados do lançamento real.

## 8. Ordem de implementação recomendada para desenvolvimento com IA

Cada fase deve ser pedida à IA separadamente, com o trecho relevante deste documento, e validada com testes antes de seguir.

1. **Fundação:** projeto Django, autenticação, modelos de cadastro (RF-001 a RF-006) com testes.
2. **Lançamento:** modelo, parcelamento e lançamento rápido (RF-007 a RF-010), com testes de datas e centavos.
3. **Planejamento:** criação, grade, visões, inserção em lote, estados e revisões (RF-011 a RF-017).
4. **Acompanhamento:** grade de realizados e comparativo (RF-019 a RF-021).
5. **Fechamento mensal:** iniciar, pagar, finalizar (RF-022 a RF-024).
6. **Simulação:** motor de cálculo e tela (RF-025).
7. **Importação CSV** (RF-018) e refinamentos de interface.

**Dicas de prompt:** informe sempre as regras transversais (seção 4), peça testes junto com o código, mantenha as regras de cálculo em uma camada de serviços (não nas views) e peça migrações pequenas por fase.

## 9. Decisões de projeto

| Ref. | Tema                     | Decisão                                                                                                                                             |
| ---- | ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Q1   | Usuários                 | Sistema único e multiusuário, sem isolamento: todos veem os mesmos dados.                                                                           |
| Q2   | Visão temporal           | A regra de corte (dias cobertos por cada período) é definida no cadastro, com vigência, e aceita pagamento único (RF-003).                          |
| Q3   | Mês de vencimento        | Removido da fonte; o mês da primeira parcela é indicado no lançamento (RF-005, RF-008).                                                             |
| Q4   | Fechamento da fatura     | Novo dia de fechamento, somente para cartão de crédito; empréstimos não têm (RF-005, RF-008).                                                       |
| Q5   | Edição em lote           | Escolha de alcance como no Google Agenda: este, este e os seguintes, ou todos (RF-015).                                                             |
| Q6   | Reabrir pago             | Permitido enquanto o mês não estiver finalizado (RF-023).                                                                                           |
| Q7   | Receitas de salário      | Lançadas manualmente, uma por recebimento (Vale, Pagamento), vinculadas a um período; sem geração automática (RF-026).                              |
| Q8   | Exportação de relatórios | Fora do escopo; mantém-se apenas a importação CSV (RF-018).                                                                                         |
| Q9   | Valor do Pagamento       | Digitado manualmente, já com o desconto do vale, sem cálculo (RF-026).                                                                              |
| Q10  | "Este e os seguintes"    | Sobrescreve ajustes individuais feitos nas ocorrências afetadas (RF-015).                                                                           |
| Q11  | Criação de usuários      | Sem auto-cadastro nem famílias; usuários são criados e gerenciados no Django admin (RF-006).                                                        |
| Q12  | Unicidade de categoria   | Nome único por natureza, sem escopo por usuário, coerente com Q1 (RF-001).                                                                          |
| Q13  | Senha esquecida          | Sem recuperação por e-mail; a senha é redefinida pelo administrador no Django admin (RF-006).                                                       |
| Q14  | Revisão x elaboração     | No mesmo ano só pode haver um planejamento não confirmado (em elaboração ou em revisão) (RF-011, RF-017).                                           |
| Q15  | Data e mês do lançamento | `data_pagamento` foi renomeada para `data_compra`; o mês nas grades, no fechamento e na simulação é o mês da fatura (`mes_fatura`) (RF-007, RN-08). |
