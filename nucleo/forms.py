from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm


class EstiloBootstrapMixin:
    """Aplica as classes do Bootstrap 5 aos widgets do formulário."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            widget = campo.widget
            if isinstance(widget, forms.CheckboxInput):
                classe = 'form-check-input'
            elif isinstance(widget, forms.Select | forms.SelectMultiple):
                classe = 'form-select'
            else:
                classe = 'form-control'
            widget.attrs['class'] = f'{widget.attrs.get("class", "")} {classe}'.strip()


class EntrarForm(EstiloBootstrapMixin, AuthenticationForm):
    pass


class TrocarSenhaForm(EstiloBootstrapMixin, PasswordChangeForm):
    pass
