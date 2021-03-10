from django.shortcuts import render, redirect, reverse
from django.core.mail import send_mail
from .forms import RegisterForm, LoginForm
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView

class Login_View(LoginView):
    template_name = 'users/login.html'
    authentication_form = LoginForm


class Register_View(CreateView):
    template_name = 'users/register.html'
    form_class = RegisterForm

    def get_success_url(self):
        return reverse("login")
        
    def form_valid(self, form):
        send_mail(
            subject="Account Confirmation",
            message="Activate your account by clicking this link -> ",
            from_email="chess@online-chess.com",
            recipient_list=["test2@test.cs"]
        )
        return super().form_valid(form)