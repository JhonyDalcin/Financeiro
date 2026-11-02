from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from cadastros.models import Categoria, FonteCredito, Natureza, PeriodoSalario, Subcategoria

pytestmark = pytest.mark.django_db


def test_categoria_com_mesmo_nome_e_naturezas_diferentes_e_permitida(categoria):
    Categoria.objects.create(nome='Moradia', natureza=Natureza.RECEITA)

    assert Categoria.objects.filter(nome='Moradia').count() == 2


def test_categoria_duplicada_na_mesma_natureza_e_recusada(categoria):
    duplicada = Categoria(nome='Moradia', natureza=Natureza.DESPESA)

    with pytest.raises(ValidationError):
        duplicada.full_clean()
    with pytest.raises(IntegrityError), transaction.atomic():
        duplicada.save()


def test_subcategoria_e_exibida_como_categoria_traco_subcategoria(subcategoria):
    assert str(subcategoria) == 'Moradia – Aluguel'


def test_subcategoria_nome_unico_dentro_da_categoria(categoria, subcategoria):
    with pytest.raises(ValidationError):
        Subcategoria(categoria=categoria, nome='Aluguel').full_clean()


def test_subcategoria_com_mesmo_nome_em_outra_categoria_e_permitida(subcategoria):
    outra = Categoria.objects.create(nome='Lazer', natureza=Natureza.DESPESA)

    Subcategoria(categoria=outra, nome='Aluguel').full_clean()


def test_subcategoria_exige_categoria(db):
    with pytest.raises(ValidationError) as erro:
        Subcategoria(nome='Sem categoria').full_clean()

    assert 'categoria' in erro.value.message_dict


def test_fonte_emprestimo_nao_aceita_dia_de_fechamento():
    fonte = FonteCredito(
        nome='Banco', tipo=FonteCredito.Tipo.EMPRESTIMO, dia_vencimento=10, dia_fechamento=5
    )

    with pytest.raises(ValidationError) as erro:
        fonte.full_clean()

    assert 'dia_fechamento' in erro.value.message_dict


def test_fonte_cartao_aceita_fechamento_opcional():
    com_fechamento = FonteCredito(
        nome='Santander', tipo=FonteCredito.Tipo.CARTAO, dia_vencimento=20, dia_fechamento=10
    )
    sem_fechamento = FonteCredito(nome='Nubank', tipo=FonteCredito.Tipo.CARTAO, dia_vencimento=20)

    com_fechamento.full_clean()
    sem_fechamento.full_clean()


@pytest.mark.parametrize('dia', [0, 32])
def test_fonte_dia_de_vencimento_deve_estar_entre_1_e_31(dia):
    fonte = FonteCredito(nome='Cartão', tipo=FonteCredito.Tipo.CARTAO, dia_vencimento=dia)

    with pytest.raises(ValidationError) as erro:
        fonte.full_clean()

    assert 'dia_vencimento' in erro.value.message_dict


def test_periodo_com_dia_inicial_maior_que_final_e_recusado():
    periodo = PeriodoSalario(
        nome='Vale',
        dia_recebimento=15,
        dia_inicio=20,
        dia_fim=10,
        vigencia_inicio=date(2027, 1, 1),
    )

    with pytest.raises(ValidationError) as erro:
        periodo.full_clean()

    assert 'dia_fim' in erro.value.message_dict


def test_periodo_com_vigencia_final_anterior_ao_inicio_e_recusado():
    periodo = PeriodoSalario(
        nome='Vale',
        dia_recebimento=15,
        dia_inicio=1,
        dia_fim=15,
        vigencia_inicio=date(2027, 6, 1),
        vigencia_fim=date(2027, 5, 31),
    )

    with pytest.raises(ValidationError) as erro:
        periodo.full_clean()

    assert 'vigencia_fim' in erro.value.message_dict
