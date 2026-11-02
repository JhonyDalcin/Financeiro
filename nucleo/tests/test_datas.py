from datetime import date

import pytest

from nucleo.datas import ajustar_dia, primeiro_dia_do_mes, ultimo_dia_do_mes


@pytest.mark.parametrize(
    ('ano', 'mes', 'esperado'),
    [
        (2027, 1, 31),
        (2027, 4, 30),
        (2027, 2, 28),
        (2028, 2, 29),
    ],
)
def test_ultimo_dia_do_mes_considera_meses_curtos_e_bissexto(ano, mes, esperado):
    assert ultimo_dia_do_mes(ano, mes) == esperado


@pytest.mark.parametrize(
    ('ano', 'mes', 'dia', 'esperado'),
    [
        (2027, 1, 15, date(2027, 1, 15)),
        (2027, 4, 31, date(2027, 4, 30)),
        (2027, 2, 29, date(2027, 2, 28)),
        (2028, 2, 29, date(2028, 2, 29)),
        (2028, 2, 31, date(2028, 2, 29)),
    ],
)
def test_ajustar_dia_usa_ultimo_dia_quando_o_dia_nao_existe(ano, mes, dia, esperado):
    assert ajustar_dia(ano, mes, dia) == esperado


def test_primeiro_dia_do_mes():
    assert primeiro_dia_do_mes(date(2027, 3, 17)) == date(2027, 3, 1)
