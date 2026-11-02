from django import forms

from cadastros import services
from cadastros.models import Categoria, FonteCredito, PeriodoSalario, Subcategoria, TipoPagamento
from nucleo.excecoes import RegraDeNegocioErro
from nucleo.forms import EstiloBootstrapMixin


class CategoriaForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'natureza', 'ativa']


class SubcategoriaForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = Subcategoria
        fields = ['categoria', 'nome', 'ativa']


class TipoPagamentoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = TipoPagamento
        fields = ['nome', 'eh_credito']


class FonteCreditoForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = FonteCredito
        fields = ['nome', 'tipo', 'dia_vencimento', 'dia_fechamento', 'ativa']


class PeriodoSalarioForm(EstiloBootstrapMixin, forms.ModelForm):
    class Meta:
        model = PeriodoSalario
        fields = [
            'nome',
            'dia_recebimento',
            'dia_inicio',
            'dia_fim',
            'descricao',
            'vigencia_inicio',
            'vigencia_fim',
        ]
        widgets = {
            'vigencia_inicio': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'vigencia_fim': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def clean(self):
        dados = super().clean()
        inicio, fim = dados.get('dia_inicio'), dados.get('dia_fim')
        vig_inicio, vig_fim = dados.get('vigencia_inicio'), dados.get('vigencia_fim')
        intervalos_validos = (
            inicio
            and fim
            and vig_inicio
            and inicio <= fim
            and (not vig_fim or vig_fim >= vig_inicio)
        )
        if intervalos_validos:
            periodo = PeriodoSalario(
                pk=self.instance.pk,
                dia_inicio=inicio,
                dia_fim=fim,
                vigencia_inicio=vig_inicio,
                vigencia_fim=vig_fim,
            )
            try:
                services.validar_sem_conflito(periodo)
            except RegraDeNegocioErro as erro:
                raise forms.ValidationError(str(erro)) from erro
        return dados


class EncerrarVigenciaForm(forms.Form):
    data_fim = forms.DateField()
