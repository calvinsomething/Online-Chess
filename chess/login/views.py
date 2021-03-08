from django.shortcuts import render, redirect, reverse
from .forms import RegisterForm, LoginForm
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView


class Login_View(LoginView):
    template_name = 'login/login.html'
    authentication_form = LoginForm


class Register_View(CreateView):
    template_name = 'login/register.html'
    form_class = RegisterForm

    def get_success_url(self):
        return reverse("login")