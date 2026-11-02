import pytest
from django.contrib.auth import get_user_model


@pytest.fixture(autouse=True)
def _hasher_rapido(settings):
    settings.PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']


@pytest.fixture
def senha():
    return 'senha-forte-2027'


@pytest.fixture
def usuario(db, senha):
    return get_user_model().objects.create_user('maria', password=senha)


@pytest.fixture
def cliente_logado(client, usuario):
    client.force_login(usuario)
    return client
