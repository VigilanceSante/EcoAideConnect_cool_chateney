from django import forms
from .models import HelpRequest

class HelpForm(forms.ModelForm):  # This is the actual form class
    class Meta:
        model = HelpRequest
        fields = ['first_name', 'last_name', 'phone']