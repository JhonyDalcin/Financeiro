import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_inicio_exige_login(client):
    resposta = client.get(reverse('nucleo:inicio'))

    assert resposta.status_code == 302
    assert resposta.url == f'{reverse("nucleo:entrar")}?next=/'


def test_entrar_com_credenciais_validas_redireciona_ao_inicio(client, usuario, senha):
    resposta = client.post(
        reverse('nucleo:entrar'), {'username': usuario.username, 'password': senha}
    )

    assert resposta.status_code == 302
    assert resposta.url == reverse('nucleo:inicio')


def test_entrar_com_senha_errada_mostra_erro(client, usuario):
    resposta = client.post(
        reverse('nucleo:entrar'), {'username': usuario.username, 'password': 'errada'}
    )

    assert resposta.status_code == 200
    assert 'alert-danger' in resposta.content.decode()


def test_sair_encerra_a_sessao(cliente_logado):
    resposta = cliente_logado.post(reverse('nucleo:sair'))

    assert resposta.status_code == 302
    assert cliente_logado.get(reverse('nucleo:inicio')).status_code == 302


def test_trocar_senha_pelo_proprio_usuario(cliente_logado, usuario, senha):
    nova = 'NovaSenha#2027x'

    resposta = cliente_logado.post(
        reverse('nucleo:trocar_senha'),
        {'old_password': senha, 'new_password1': nova, 'new_password2': nova},
    )

    assert resposta.status_code == 302
    assert get_user_model().objects.get(pk=usuario.pk).check_password(nova)


def test_trocar_senha_exige_login(client):
    resposta = client.get(reverse('nucleo:trocar_senha'))

    assert resposta.status_code == 302
    assert reverse('nucleo:entrar') in resposta.url


def test_trocar_senha_aplica_validadores_do_django(cliente_logado, senha):
    resposta = cliente_logado.post(
        reverse('nucleo:trocar_senha'),
        {'old_password': senha, 'new_password1': '12345678', 'new_password2': '12345678'},
    )

    assert resposta.status_code == 200
    assert 'text-danger' in resposta.content.decode()


@pytest.mark.parametrize('caminho', ['/cadastrar/', '/registrar/', '/signup/', '/cadastro/'])
def test_nao_existe_rota_de_auto_cadastro(client, caminho):
    assert client.get(caminho).status_code == 404
