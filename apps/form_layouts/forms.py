# forms.py
from django import forms
from .models import ContactForm

class ContactFormForm(forms.ModelForm):
    class Meta:
        model = ContactForm
        fields = '__all__'
