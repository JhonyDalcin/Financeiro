from datetime import date

import pytest

from cadastros.models import Categoria, Natureza, PeriodoSalario, Subcategoria


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(nome='Moradia', natureza=Natureza.DESPESA)


@pytest.fixture
def subcategoria(categoria):
    return Subcategoria.objects.create(categoria=categoria, nome='Aluguel')


@pytest.fixture
def criar_periodo(db):
    def _criar(
        nome, dia_inicio, dia_fim, vigencia_inicio=date(2027, 1, 1), vigencia_fim=None, **extra
    ):
        return PeriodoSalario.objects.create(
            nome=nome,
            dia_recebimento=extra.pop('dia_recebimento', dia_fim),
            dia_inicio=dia_inicio,
            dia_fim=dia_fim,
            vigencia_inicio=vigencia_inicio,
            vigencia_fim=vigencia_fim,
            **extra,
        )

    return _criar
