from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class RegisterForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)  # Add password input

    class Meta:
        model = User  # Specify that this form is for the User model
        fields = ['username', 'email']  # Only include fields that exist in the User model

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])  # Hash the password manually
        if commit:
            user.save()
        return user
