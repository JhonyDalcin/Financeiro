from django.contrib.auth.views import LogoutView
from django.urls import path

from nucleo import views

app_name = 'nucleo'

urlpatterns = [
    path('', views.InicioView.as_view(), name='inicio'),
    path('entrar/', views.EntrarView.as_view(), name='entrar'),
    path('sair/', LogoutView.as_view(), name='sair'),
    path('senha/', views.TrocarSenhaView.as_view(), name='trocar_senha'),
]
