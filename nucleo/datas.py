import calendar
from datetime import date


def ultimo_dia_do_mes(ano: int, mes: int) -> int:
    return calendar.monthrange(ano, mes)[1]


def ajustar_dia(ano: int, mes: int, dia: int) -> date:
    """Data com o dia pedido; se o dia não existir no mês, usa o último dia."""
    return date(ano, mes, min(dia, ultimo_dia_do_mes(ano, mes)))


def primeiro_dia_do_mes(data: date) -> date:
    return data.replace(day=1)
