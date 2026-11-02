from datetime import date

import pytest

from cadastros import services
from cadastros.models import Categoria, PeriodoSalario, Subcategoria
from nucleo.excecoes import RegraDeNegocioErro

pytestmark = pytest.mark.django_db


def test_excluir_categoria_com_subcategoria_e_recusado(categoria, subcategoria):
    with pytest.raises(RegraDeNegocioErro):
        services.excluir(categoria)

    assert Categoria.objects.filter(pk=categoria.pk).exists()


def test_excluir_categoria_sem_uso_remove_o_registro(categoria):
    services.excluir(categoria)

    assert not Categoria.objects.filter(pk=categoria.pk).exists()


def test_excluir_subcategoria_sem_uso_mantem_a_categoria(categoria, subcategoria):
    services.excluir(subcategoria)

    assert not Subcategoria.objects.filter(pk=subcategoria.pk).exists()
    assert Categoria.objects.filter(pk=categoria.pk).exists()


def test_inativar_marca_como_inativa_sem_excluir(categoria):
    services.inativar(categoria)

    categoria.refresh_from_db()
    assert categoria.ativa is False


def test_periodos_vigentes_que_cobrem_o_mes_nao_tem_lacunas(criar_periodo):
    criar_periodo('Vale', 1, 15)
    criar_periodo('Pagamento', 16, 31)

    assert services.lacunas_de_cobertura(date(2027, 3, 10)) == []


def test_pagamento_unico_cobre_todos_os_dias(criar_periodo):
    criar_periodo('Pagamento', 1, 31)

    assert services.lacunas_de_cobertura(date(2027, 3, 10)) == []


def test_lacunas_listam_os_dias_sem_periodo(criar_periodo):
    criar_periodo('Vale', 1, 15)

    assert services.lacunas_de_cobertura(date(2027, 3, 10)) == [(16, 31)]


def test_sem_periodos_todos_os_dias_estao_descobertos(db):
    assert services.lacunas_de_cobertura(date(2027, 3, 10)) == [(1, 31)]


def test_lacunas_ignoram_periodos_fora_da_vigencia(criar_periodo):
    criar_periodo(
        'Antigo', 1, 31, vigencia_inicio=date(2026, 1, 1), vigencia_fim=date(2026, 12, 31)
    )

    assert services.lacunas_de_cobertura(date(2027, 3, 10)) == [(1, 31)]


def test_descrever_lacunas():
    assert services.descrever_lacunas([(1, 5), (10, 10), (20, 31)]) == '1–5, 10, 20–31'


def test_periodo_sobreposto_em_dias_e_vigencia_e_recusado(criar_periodo):
    criar_periodo('Vale', 1, 15)
    novo = PeriodoSalario(
        nome='Meio', dia_recebimento=20, dia_inicio=10, dia_fim=20, vigencia_inicio=date(2027, 6, 1)
    )

    with pytest.raises(RegraDeNegocioErro):
        services.validar_sem_conflito(novo)


def test_periodo_com_dias_diferentes_nao_conflita(criar_periodo):
    criar_periodo('Vale', 1, 15)
    novo = PeriodoSalario(
        nome='Pagamento',
        dia_recebimento=30,
        dia_inicio=16,
        dia_fim=31,
        vigencia_inicio=date(2027, 1, 1),
    )

    services.validar_sem_conflito(novo)


def test_periodo_com_mesmos_dias_em_outra_vigencia_nao_conflita(criar_periodo):
    criar_periodo('Vale', 1, 15, vigencia_fim=date(2027, 6, 30))
    novo = PeriodoSalario(
        nome='Pagamento novo',
        dia_recebimento=5,
        dia_inicio=1,
        dia_fim=15,
        vigencia_inicio=date(2027, 7, 1),
    )

    services.validar_sem_conflito(novo)


def test_editar_o_proprio_periodo_nao_gera_conflito(criar_periodo):
    vale = criar_periodo('Vale', 1, 15)

    services.validar_sem_conflito(vale)


def test_encerrar_vigencia_preserva_os_periodos_e_define_o_fim(criar_periodo):
    vale = criar_periodo('Vale', 1, 15)
    pagamento = criar_periodo('Pagamento', 16, 31)

    total = services.encerrar_vigencia(date(2027, 6, 30))

    vale.refresh_from_db()
    pagamento.refresh_from_db()
    assert total == 2
    assert vale.vigencia_fim == date(2027, 6, 30)
    assert pagamento.vigencia_fim == date(2027, 6, 30)


def test_novo_conjunto_apos_encerrar_nao_altera_meses_passados(criar_periodo):
    criar_periodo('Vale', 1, 15)
    criar_periodo('Pagamento', 16, 31)
    services.encerrar_vigencia(date(2027, 6, 30))
    criar_periodo('Mensal', 1, 31, vigencia_inicio=date(2027, 7, 1))

    assert services.lacunas_de_cobertura(date(2027, 3, 10)) == []
    assert services.lacunas_de_cobertura(date(2027, 8, 10)) == []
    assert (
        PeriodoSalario.objects.filter(
            vigencia_inicio__lte=date(2027, 3, 10), vigencia_fim__isnull=True
        ).count()
        == 0
    )


def test_encerrar_vigencia_sem_periodos_em_aberto_e_recusado(db):
    with pytest.raises(RegraDeNegocioErro):
        services.encerrar_vigencia(date(2027, 6, 30))


def test_encerrar_vigencia_antes_do_inicio_e_recusado(criar_periodo):
    criar_periodo('Vale', 1, 15, vigencia_inicio=date(2027, 7, 1))

    with pytest.raises(RegraDeNegocioErro):
        services.encerrar_vigencia(date(2027, 6, 30))
