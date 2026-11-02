from decimal import Decimal

import pytest

from nucleo.templatetags.formatacao import moeda


@pytest.mark.parametrize(
    ('valor', 'esperado'),
    [
        (Decimal('1234.56'), 'R$ 1.234,56'),
        (Decimal('0'), 'R$ 0,00'),
        (Decimal('1234567.8'), 'R$ 1.234.567,80'),
        (Decimal('-1234.5'), '-R$ 1.234,50'),
        (Decimal('33.335'), 'R$ 33,34'),
        ('100', 'R$ 100,00'),
        (None, ''),
        ('', ''),
        ('abc', ''),
    ],
)
def test_moeda_formata_em_reais(valor, esperado):
    assert moeda(valor) == esperado
