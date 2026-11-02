from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from cadastros import services
from cadastros.forms import EncerrarVigenciaForm
from nucleo.excecoes import RegraDeNegocioErro


class CadastroMixin(LoginRequiredMixin):
    model = None
    prefixo = None
    titulo = ''
    titulo_plural = ''

    def _url(self, acao):
        return f'cadastros:{self.prefixo}_{acao}'

    @property
    def url_lista(self):
        return self._url('lista')

    @property
    def url_criar(self):
        return self._url('criar')

    @property
    def url_editar(self):
        return self._url('editar')

    @property
    def url_excluir(self):
        return self._url('excluir')

    @property
    def url_inativar(self):
        return self._url('inativar')

    def get_success_url(self):
        return reverse(self.url_lista)


def _valor_da_coluna(objeto, coluna):
    valor = coluna(objeto) if callable(coluna) else getattr(objeto, coluna)
    if callable(valor):
        valor = valor()
    if valor is None or valor == '':
        return '—'
    if isinstance(valor, bool):
        return 'Sim' if valor else 'Não'
    if isinstance(valor, date):
        return valor.strftime('%d/%m/%Y')
    return valor


class ListaView(CadastroMixin, ListView):
    template_name = 'cadastros/lista.html'
    context_object_name = 'objetos'
    colunas = ()
    relacionados = ()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.relacionados:
            queryset = queryset.select_related(*self.relacionados)
        return queryset

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['rotulos'] = [rotulo for rotulo, _ in self.colunas]
        contexto['total_colunas'] = len(self.colunas) + 1
        contexto['linhas'] = [
            {
                'objeto': objeto,
                'inativo': getattr(objeto, 'ativa', True) is False,
                'valores': [_valor_da_coluna(objeto, coluna) for _, coluna in self.colunas],
            }
            for objeto in contexto['objetos']
        ]
        return contexto


class CriarView(CadastroMixin, SuccessMessageMixin, CreateView):
    template_name = 'cadastros/formulario.html'
    success_message = 'Registro criado com sucesso.'


class EditarView(CadastroMixin, SuccessMessageMixin, UpdateView):
    template_name = 'cadastros/formulario.html'
    success_message = 'Registro atualizado com sucesso.'


class ExcluirView(CadastroMixin, DeleteView):
    template_name = 'cadastros/confirmar_exclusao.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['em_uso'] = self.object.em_uso()
        contexto['pode_inativar'] = hasattr(self.object, 'ativa')
        return contexto

    def form_valid(self, form):
        try:
            services.excluir(self.object)
        except RegraDeNegocioErro as erro:
            messages.error(self.request, str(erro))
        else:
            messages.success(self.request, 'Registro excluído com sucesso.')
        return HttpResponseRedirect(self.get_success_url())


class InativarView(CadastroMixin, View):
    http_method_names = ['post']

    def post(self, request, pk):
        objeto = get_object_or_404(self.model, pk=pk)
        services.inativar(objeto)
        messages.success(request, f'"{objeto}" foi inativado.')
        return HttpResponseRedirect(self.get_success_url())


class PeriodoSalarioListaView(ListaView):
    template_name = 'cadastros/periodosalario_lista.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        lacunas = services.lacunas_de_cobertura(timezone.localdate())
        contexto['lacunas_texto'] = services.descrever_lacunas(lacunas)
        return contexto


class EncerrarVigenciaView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request):
        form = EncerrarVigenciaForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'Informe uma data válida para encerrar a vigência.')
        else:
            try:
                total = services.encerrar_vigencia(form.cleaned_data['data_fim'])
            except RegraDeNegocioErro as erro:
                messages.error(request, str(erro))
            else:
                messages.success(request, f'Vigência encerrada ({total} período(s)).')
        return redirect('cadastros:periodosalario_lista')
