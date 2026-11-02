from django.conf import settings
from django.template.loader import render_to_string


def test_idioma_fuso_e_usa_tz_configurados():
    assert settings.LANGUAGE_CODE == 'pt-br'
    assert settings.TIME_ZONE == 'America/Sao_Paulo'
    assert settings.USE_TZ is True


def test_base_carrega_temas_flatly_e_darkly_localmente():
    html = render_to_string('base.html')

    assert 'vendor/bootswatch/flatly.min.css' in html
    assert 'vendor/bootswatch/darkly.min.css' in html
    assert 'vendor/htmx/htmx.min.js' in html
    assert 'id="alternar-tema"' in html
    assert 'lang="pt-br"' in html


def test_base_envia_token_csrf_nas_requisicoes_htmx():
    html = render_to_string('base.html', {'csrf_token': 'token-de-teste'})

    assert 'token-de-teste' in html
    assert 'hx-headers' in html
