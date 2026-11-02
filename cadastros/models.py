from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

DIA_DO_MES = [MinValueValidator(1), MaxValueValidator(31)]


class Natureza(models.TextChoices):
    RECEITA = 'RECEITA', 'Receita'
    DESPESA = 'DESPESA', 'Despesa'


class Categoria(models.Model):
    nome = models.CharField('nome', max_length=100)
    natureza = models.CharField('natureza', max_length=10, choices=Natureza.choices)
    ativa = models.BooleanField('ativa', default=True)

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'
        ordering = ['natureza', 'nome']
        constraints = [
            models.UniqueConstraint(
                fields=['natureza', 'nome'],
                name='categoria_nome_natureza_unico',
                violation_error_message='Já existe uma categoria com este nome nesta natureza.',
            ),
        ]

    def __str__(self):
        return self.nome

    def em_uso(self):
        return self.subcategorias.exists()


class Subcategoria(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        verbose_name='categoria',
        on_delete=models.PROTECT,
        related_name='subcategorias',
    )
    nome = models.CharField('nome', max_length=100)
    ativa = models.BooleanField('ativa', default=True)

    class Meta:
        verbose_name = 'subcategoria'
        verbose_name_plural = 'subcategorias'
        ordering = ['categoria__natureza', 'categoria__nome', 'nome']
        constraints = [
            models.UniqueConstraint(
                fields=['categoria', 'nome'],
                name='subcategoria_nome_categoria_unico',
                violation_error_message='Já existe uma subcategoria com este nome nesta categoria.',
            ),
        ]

    def __str__(self):
        return f'{self.categoria.nome} – {self.nome}'

    def em_uso(self):
        # Os lançamentos passam a referenciar a subcategoria na Fase 2.
        return False


class TipoPagamento(models.Model):
    nome = models.CharField('nome', max_length=100, unique=True)
    eh_credito = models.BooleanField(
        'é crédito',
        default=False,
        help_text='Exige fonte de crédito e parcelas no lançamento.',
    )

    class Meta:
        verbose_name = 'tipo de pagamento'
        verbose_name_plural = 'tipos de pagamento'
        ordering = ['nome']

    def __str__(self):
        return self.nome

    def em_uso(self):
        # Os lançamentos passam a referenciar o tipo na Fase 2.
        return False


class FonteCredito(models.Model):
    class Tipo(models.TextChoices):
        CARTAO = 'CARTAO', 'Cartão de crédito'
        EMPRESTIMO = 'EMPRESTIMO', 'Empréstimo'
        OUTRO = 'OUTRO', 'Outro'

    nome = models.CharField('nome', max_length=100, unique=True)
    tipo = models.CharField('tipo', max_length=12, choices=Tipo.choices)
    dia_vencimento = models.PositiveSmallIntegerField('dia de vencimento', validators=DIA_DO_MES)
    dia_fechamento = models.PositiveSmallIntegerField(
        'dia de fechamento',
        null=True,
        blank=True,
        validators=DIA_DO_MES,
        help_text='Somente cartão de crédito; opcional.',
    )
    ativa = models.BooleanField('ativa', default=True)

    class Meta:
        verbose_name = 'fonte de crédito'
        verbose_name_plural = 'fontes de crédito'
        ordering = ['nome']
        constraints = [
            models.CheckConstraint(
                condition=Q(dia_fechamento__isnull=True) | Q(tipo='CARTAO'),
                name='fonte_fechamento_somente_cartao',
            ),
        ]

    def __str__(self):
        return self.nome

    def clean(self):
        if self.dia_fechamento is not None and self.tipo != self.Tipo.CARTAO:
            raise ValidationError(
                {'dia_fechamento': 'Somente cartão de crédito tem dia de fechamento.'}
            )

    def em_uso(self):
        # Os lançamentos passam a referenciar a fonte na Fase 2.
        return False


class PeriodoSalario(models.Model):
    nome = models.CharField('nome', max_length=100)
    dia_recebimento = models.PositiveSmallIntegerField('dia de recebimento', validators=DIA_DO_MES)
    dia_inicio = models.PositiveSmallIntegerField('dia inicial', validators=DIA_DO_MES)
    dia_fim = models.PositiveSmallIntegerField('dia final', validators=DIA_DO_MES)
    descricao = models.CharField('descrição', max_length=200, blank=True)
    vigencia_inicio = models.DateField('início da vigência')
    vigencia_fim = models.DateField('fim da vigência', null=True, blank=True)

    class Meta:
        verbose_name = 'período de salário'
        verbose_name_plural = 'períodos de salário'
        ordering = ['-vigencia_inicio', 'dia_inicio']
        constraints = [
            models.CheckConstraint(
                condition=Q(dia_inicio__lte=models.F('dia_fim')),
                name='periodo_dia_inicio_ate_dia_fim',
            ),
            models.CheckConstraint(
                condition=Q(vigencia_fim__isnull=True)
                | Q(vigencia_fim__gte=models.F('vigencia_inicio')),
                name='periodo_vigencia_fim_apos_inicio',
            ),
        ]

    def __str__(self):
        return self.nome

    def clean(self):
        erros = {}
        if self.dia_inicio and self.dia_fim and self.dia_inicio > self.dia_fim:
            erros['dia_fim'] = 'O dia final não pode ser anterior ao dia inicial.'
        if self.vigencia_inicio and self.vigencia_fim and self.vigencia_fim < self.vigencia_inicio:
            erros['vigencia_fim'] = 'O fim da vigência não pode ser anterior ao início.'
        if erros:
            raise ValidationError(erros)

    def em_uso(self):
        # Os lançamentos de salário passam a referenciar o período na Fase 3.
        return False
