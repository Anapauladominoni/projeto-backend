from django import forms
from .models import Loja, Usuario

class LojaAdminForm(forms.ModelForm):
    class Meta:
        model = Loja
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra apenas usuários com role 'empreendedor'
        self.fields['empreendedor'].queryset = Usuario.objects.filter(role='empreendedor')