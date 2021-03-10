from django.shortcuts import render, redirect, reverse
from django.core.mail import send_mail
from .forms import RegisterForm, LoginForm
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import UserPassesTestMixin


class Login_View(UserPassesTestMixin, LoginView):
    template_name = 'users/login.html'
    authentication_form = LoginForm

    def handle_no_permission(self):
        return redirect("home")

    def test_func(self):
        return self.request.user.is_anonymous


class Register_View(UserPassesTestMixin, CreateView):
    template_name = 'users/register.html'
    form_class = RegisterForm

    def handle_no_permission(self):
        return redirect("home")

    def test_func(self):
        return self.request.user.is_anonymous

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