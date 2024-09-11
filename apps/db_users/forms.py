from django import forms
from .models import ContactForm  # Importez le modèle AidRequest

class ContactFormForm(forms.ModelForm):
    class Meta:
        model = ContactForm
        fields = '__all__'
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-lg'}),
        }
