from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from nucleo.forms import EntrarForm, TrocarSenhaForm


class EntrarView(LoginView):
    template_name = 'nucleo/entrar.html'
    authentication_form = EntrarForm
    redirect_authenticated_user = True


class TrocarSenhaView(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    template_name = 'nucleo/trocar_senha.html'
    form_class = TrocarSenhaForm
    success_url = reverse_lazy('nucleo:inicio')
    success_message = 'Senha alterada com sucesso.'


class InicioView(LoginRequiredMixin, TemplateView):
    template_name = 'nucleo/inicio.html'
