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
    
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    remember_me = forms.BooleanField(required=False, label='Remember me')

    # Initialize user to None
    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError('Invalid username or password.')
            else:
                self.user = user

        return cleaned_data

    def get_user(self):
        return self.user
