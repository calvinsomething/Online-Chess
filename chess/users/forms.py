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

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            if User.objects.get(username__iexact=username):
                raise forms.ValidationError('Username is unavailable.')
        except User.DoesNotExist:
            return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        try:
            if User.objects.get(email=email):
                raise forms.ValidationError('An account with that email already exists.')
        except User.DoesNotExist:
            return email


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

