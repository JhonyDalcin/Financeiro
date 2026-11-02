from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def moeda(valor):
    """Formata como moeda BRL: R$ 1.234,56."""
    if valor is None or valor == '':
        return ''
    try:
        decimal = Decimal(str(valor)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        return ''
    sinal = '-' if decimal < 0 else ''
    inteiro, centavos = f'{abs(decimal):.2f}'.split('.')
    inteiro = f'{int(inteiro):,}'.replace(',', '.')
    return f'{sinal}R$ {inteiro},{centavos}'
