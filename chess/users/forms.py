from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from .models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'username': placeholder = 'Username'
            if field == 'email':
                placeholder = 'Email'
                self.fields[field].required = True
            if field == 'password1': placeholder = 'Password'
            if field == 'password2': placeholder = 'Re-Enter Password'
            self.fields[field].widget.attrs.update({'class': 'form-control', 'placeholder': placeholder})


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    username = forms.CharField(
		max_length=50,
		widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
	)
    password = forms.CharField(
		max_length=50,
		widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
	)

