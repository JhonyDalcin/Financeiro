from django.db import transaction
from django.db.models import Q

from cadastros.models import PeriodoSalario
from nucleo.excecoes import RegraDeNegocioErro


def excluir(objeto):
    """Exclui o cadastro; itens em uso só podem ser inativados."""
    if objeto.em_uso():
        raise RegraDeNegocioErro(f'"{objeto}" está em uso e não pode ser excluído; inative-o.')
    objeto.delete()


def inativar(objeto):
    if objeto.ativa:
        objeto.ativa = False
        objeto.save(update_fields=['ativa'])


def periodos_conflitantes(periodo):
    """Períodos que se sobrepõem em dias e em vigência ao informado."""
    conflitantes = PeriodoSalario.objects.exclude(pk=periodo.pk).filter(
        dia_inicio__lte=periodo.dia_fim,
        dia_fim__gte=periodo.dia_inicio,
    )
    conflitantes = conflitantes.filter(
        Q(vigencia_fim__isnull=True) | Q(vigencia_fim__gte=periodo.vigencia_inicio)
    )
    if periodo.vigencia_fim:
        conflitantes = conflitantes.filter(vigencia_inicio__lte=periodo.vigencia_fim)
    return conflitantes


def validar_sem_conflito(periodo):
    nomes = ', '.join(p.nome for p in periodos_conflitantes(periodo))
    if nomes:
        raise RegraDeNegocioErro(
            f'Os dias e a vigência se sobrepõem a outro(s) período(s) vigente(s): {nomes}.'
        )


def lacunas_de_cobertura(data):
    """Faixas de dias do mês (1 a 31) sem período vigente na data informada."""
    vigentes = PeriodoSalario.objects.filter(vigencia_inicio__lte=data).filter(
        Q(vigencia_fim__isnull=True) | Q(vigencia_fim__gte=data)
    )
    cobertos = set()
    for periodo in vigentes:
        cobertos.update(range(periodo.dia_inicio, periodo.dia_fim + 1))

    lacunas = []
    inicio = None
    for dia in range(1, 32):
        if dia not in cobertos and inicio is None:
            inicio = dia
        elif dia in cobertos and inicio is not None:
            lacunas.append((inicio, dia - 1))
            inicio = None
    if inicio is not None:
        lacunas.append((inicio, 31))
    return lacunas


def descrever_lacunas(lacunas):
    return ', '.join(str(i) if i == f else f'{i}–{f}' for i, f in lacunas)


@transaction.atomic
def encerrar_vigencia(data_fim):
    """Encerra a vigência dos períodos em aberto (troca de empresa); não altera o passado."""
    abertos = PeriodoSalario.objects.filter(vigencia_fim__isnull=True)
    if not abertos.exists():
        raise RegraDeNegocioErro('Não há vigência em aberto para encerrar.')
    if abertos.filter(vigencia_inicio__gt=data_fim).exists():
        raise RegraDeNegocioErro('A data de fim não pode ser anterior ao início da vigência atual.')
    return abertos.update(vigencia_fim=data_fim)
