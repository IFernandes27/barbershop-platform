from django import forms
from .models import Marcacao

class BookingForm(forms.ModelForm):
    class Meta:
        model = Marcacao
        # aqui só escolhemos data/hora nesta etapa
        fields = ['inicio']
        widgets = {
            'inicio': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'style': 'max-width: 300px; margin: 0 auto;',
                }
            )
        }
