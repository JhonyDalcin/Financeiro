from datetime import date

import pytest
from django.urls import reverse

from cadastros.models import (
    Categoria,
    FonteCredito,
    Natureza,
    PeriodoSalario,
    Subcategoria,
    TipoPagamento,
)

pytestmark = pytest.mark.django_db

PREFIXOS = ['categoria', 'subcategoria', 'tipopagamento', 'fontecredito', 'periodosalario']
INATIVAVEIS = ['categoria', 'subcategoria', 'fontecredito']


def _urls_protegidas():
    urls = []
    for prefixo in PREFIXOS:
        urls.append((f'cadastros:{prefixo}_lista', (), 'get'))
        urls.append((f'cadastros:{prefixo}_criar', (), 'get'))
        urls.append((f'cadastros:{prefixo}_editar', (1,), 'get'))
        urls.append((f'cadastros:{prefixo}_excluir', (1,), 'get'))
        urls.append((f'cadastros:{prefixo}_excluir', (1,), 'post'))
    for prefixo in INATIVAVEIS:
        urls.append((f'cadastros:{prefixo}_inativar', (1,), 'post'))
    urls.append(('cadastros:periodosalario_encerrar', (), 'post'))
    return urls


@pytest.mark.parametrize(('nome', 'args', 'metodo'), _urls_protegidas())
def test_cadastros_exigem_login(client, nome, args, metodo):
    resposta = getattr(client, metodo)(reverse(nome, args=args))

    assert resposta.status_code == 302
    assert reverse('nucleo:entrar') in resposta.url


@pytest.mark.parametrize('prefixo', PREFIXOS)
def test_listas_e_formularios_abrem_para_usuario_logado(cliente_logado, prefixo):
    assert cliente_logado.get(reverse(f'cadastros:{prefixo}_lista')).status_code == 200
    assert cliente_logado.get(reverse(f'cadastros:{prefixo}_criar')).status_code == 200


def test_criar_categoria(cliente_logado):
    resposta = cliente_logado.post(
        reverse('cadastros:categoria_criar'),
        {'nome': 'Alimentação', 'natureza': Natureza.DESPESA, 'ativa': 'on'},
    )

    assert resposta.status_code == 302
    assert Categoria.objects.filter(nome='Alimentação', natureza=Natureza.DESPESA).exists()


def test_categoria_duplicada_mostra_mensagem_de_erro(cliente_logado, categoria):
    resposta = cliente_logado.post(
        reverse('cadastros:categoria_criar'),
        {'nome': 'Moradia', 'natureza': Natureza.DESPESA, 'ativa': 'on'},
    )

    assert resposta.status_code == 200
    assert 'Já existe uma categoria com este nome nesta natureza.' in resposta.content.decode()


def test_lista_de_subcategorias_exibe_categoria_traco_subcategoria(cliente_logado, subcategoria):
    resposta = cliente_logado.get(reverse('cadastros:subcategoria_lista'))

    assert 'Moradia – Aluguel' in resposta.content.decode()


def test_subcategoria_sem_categoria_nao_e_salva(cliente_logado):
    resposta = cliente_logado.post(
        reverse('cadastros:subcategoria_criar'), {'nome': 'Solta', 'ativa': 'on'}
    )

    assert resposta.status_code == 200
    assert not Subcategoria.objects.exists()


def test_excluir_categoria_em_uso_oferece_inativar(cliente_logado, categoria, subcategoria):
    resposta = cliente_logado.get(reverse('cadastros:categoria_excluir', args=[categoria.pk]))

    conteudo = resposta.content.decode()
    assert 'Inativar' in conteudo
    assert 'btn-danger' not in conteudo


def test_post_de_exclusao_de_categoria_em_uso_nao_exclui(cliente_logado, categoria, subcategoria):
    resposta = cliente_logado.post(
        reverse('cadastros:categoria_excluir', args=[categoria.pk]), follow=True
    )

    assert Categoria.objects.filter(pk=categoria.pk).exists()
    assert 'não pode ser excluído' in resposta.content.decode()


def test_excluir_categoria_sem_uso(cliente_logado, categoria):
    resposta = cliente_logado.post(reverse('cadastros:categoria_excluir', args=[categoria.pk]))

    assert resposta.status_code == 302
    assert not Categoria.objects.filter(pk=categoria.pk).exists()


def test_inativar_categoria(cliente_logado, categoria):
    cliente_logado.post(reverse('cadastros:categoria_inativar', args=[categoria.pk]))

    categoria.refresh_from_db()
    assert categoria.ativa is False


def test_inativar_nao_aceita_get(cliente_logado, categoria):
    resposta = cliente_logado.get(reverse('cadastros:categoria_inativar', args=[categoria.pk]))

    assert resposta.status_code == 405


def test_criar_tipo_pagamento_de_credito(cliente_logado):
    cliente_logado.post(
        reverse('cadastros:tipopagamento_criar'), {'nome': 'Crédito', 'eh_credito': 'on'}
    )

    assert TipoPagamento.objects.get(nome='Crédito').eh_credito is True


def test_fonte_emprestimo_com_fechamento_mostra_erro(cliente_logado):
    resposta = cliente_logado.post(
        reverse('cadastros:fontecredito_criar'),
        {
            'nome': 'Banco',
            'tipo': FonteCredito.Tipo.EMPRESTIMO,
            'dia_vencimento': 10,
            'dia_fechamento': 3,
            'ativa': 'on',
        },
    )

    assert resposta.status_code == 200
    assert 'Somente cartão de crédito tem dia de fechamento.' in resposta.content.decode()
    assert not FonteCredito.objects.exists()


def _dados_periodo(**extra):
    dados = {
        'nome': 'Vale',
        'dia_recebimento': 15,
        'dia_inicio': 1,
        'dia_fim': 15,
        'descricao': '',
        'vigencia_inicio': '2027-01-01',
        'vigencia_fim': '',
    }
    dados.update(extra)
    return dados


def test_criar_periodo_de_salario(cliente_logado):
    resposta = cliente_logado.post(reverse('cadastros:periodosalario_criar'), _dados_periodo())

    assert resposta.status_code == 302
    assert PeriodoSalario.objects.get(nome='Vale').vigencia_inicio == date(2027, 1, 1)


def test_periodo_sobreposto_mostra_erro(cliente_logado, criar_periodo):
    criar_periodo('Vale', 1, 15)

    resposta = cliente_logado.post(
        reverse('cadastros:periodosalario_criar'),
        _dados_periodo(nome='Outro', dia_inicio=10, dia_fim=20),
    )

    assert resposta.status_code == 200
    assert 'se sobrepõem' in resposta.content.decode()
    assert PeriodoSalario.objects.count() == 1


def test_lista_de_periodos_avisa_dias_sem_cobertura(cliente_logado, criar_periodo, monkeypatch):
    criar_periodo('Vale', 1, 15)
    monkeypatch.setattr('cadastros.views.timezone.localdate', lambda: date(2027, 3, 10))

    resposta = cliente_logado.get(reverse('cadastros:periodosalario_lista'))

    assert '16–31' in resposta.content.decode()


def test_encerrar_vigencia_pela_tela(cliente_logado, criar_periodo):
    periodo = criar_periodo('Vale', 1, 15)

    resposta = cliente_logado.post(
        reverse('cadastros:periodosalario_encerrar'), {'data_fim': '2027-06-30'}
    )

    periodo.refresh_from_db()
    assert resposta.status_code == 302
    assert periodo.vigencia_fim == date(2027, 6, 30)


def test_encerrar_vigencia_com_data_invalida_nao_altera(cliente_logado, criar_periodo):
    periodo = criar_periodo('Vale', 1, 15)

    cliente_logado.post(reverse('cadastros:periodosalario_encerrar'), {'data_fim': 'abc'})

    periodo.refresh_from_db()
    assert periodo.vigencia_fim is None
