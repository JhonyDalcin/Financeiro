from django.urls import path

from cadastros import views
from cadastros.forms import (
    CategoriaForm,
    FonteCreditoForm,
    PeriodoSalarioForm,
    SubcategoriaForm,
    TipoPagamentoForm,
)
from cadastros.models import Categoria, FonteCredito, PeriodoSalario, Subcategoria, TipoPagamento

app_name = 'cadastros'


def _vigencia(periodo):
    inicio = periodo.vigencia_inicio.strftime('%d/%m/%Y')
    if periodo.vigencia_fim is None:
        return f'desde {inicio}'
    return f'{inicio} a {periodo.vigencia_fim.strftime("%d/%m/%Y")}'


def _dias_cobertos(periodo):
    return f'{periodo.dia_inicio} a {periodo.dia_fim}'


def rotas(
    prefixo,
    slug,
    modelo,
    form,
    titulo,
    titulo_plural,
    colunas,
    relacionados=(),
    inativavel=False,
    lista=views.ListaView,
):
    base = {'model': modelo, 'prefixo': prefixo, 'titulo': titulo, 'titulo_plural': titulo_plural}
    urls = [
        path(
            f'{slug}/',
            lista.as_view(colunas=colunas, relacionados=relacionados, **base),
            name=f'{prefixo}_lista',
        ),
        path(
            f'{slug}/novo/',
            views.CriarView.as_view(form_class=form, **base),
            name=f'{prefixo}_criar',
        ),
        path(
            f'{slug}/<int:pk>/editar/',
            views.EditarView.as_view(form_class=form, **base),
            name=f'{prefixo}_editar',
        ),
        path(
            f'{slug}/<int:pk>/excluir/',
            views.ExcluirView.as_view(**base),
            name=f'{prefixo}_excluir',
        ),
    ]
    if inativavel:
        urls.append(
            path(
                f'{slug}/<int:pk>/inativar/',
                views.InativarView.as_view(**base),
                name=f'{prefixo}_inativar',
            )
        )
    return urls


urlpatterns = [
    *rotas(
        'categoria',
        'categorias',
        Categoria,
        CategoriaForm,
        'Categoria',
        'Categorias',
        [('Nome', 'nome'), ('Natureza', 'get_natureza_display'), ('Ativa', 'ativa')],
        inativavel=True,
    ),
    *rotas(
        'subcategoria',
        'subcategorias',
        Subcategoria,
        SubcategoriaForm,
        'Subcategoria',
        'Subcategorias',
        [('Categoria – Subcategoria', '__str__'), ('Ativa', 'ativa')],
        relacionados=('categoria',),
        inativavel=True,
    ),
    *rotas(
        'tipopagamento',
        'tipos-pagamento',
        TipoPagamento,
        TipoPagamentoForm,
        'Tipo de pagamento',
        'Tipos de pagamento',
        [('Nome', 'nome'), ('É crédito', 'eh_credito')],
    ),
    *rotas(
        'fontecredito',
        'fontes-credito',
        FonteCredito,
        FonteCreditoForm,
        'Fonte de crédito',
        'Fontes de crédito',
        [
            ('Nome', 'nome'),
            ('Tipo', 'get_tipo_display'),
            ('Vencimento', 'dia_vencimento'),
            ('Fechamento', 'dia_fechamento'),
            ('Ativa', 'ativa'),
        ],
        inativavel=True,
    ),
    *rotas(
        'periodosalario',
        'periodos-salario',
        PeriodoSalario,
        PeriodoSalarioForm,
        'Período de salário',
        'Períodos de salário',
        [
            ('Nome', 'nome'),
            ('Recebimento (dia)', 'dia_recebimento'),
            ('Dias cobertos', _dias_cobertos),
            ('Vigência', _vigencia),
        ],
        lista=views.PeriodoSalarioListaView,
    ),
    path(
        'periodos-salario/encerrar-vigencia/',
        views.EncerrarVigenciaView.as_view(),
        name='periodosalario_encerrar',
    ),
]
