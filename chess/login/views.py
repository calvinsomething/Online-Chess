from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth.views import LoginView


class Login_View(LoginView):
    template_name = 'login/login.html'
    authentication_form = LoginForm



def register_view(request):
    
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        #form.save()
        return redirect('login')

    for field in form.fields:
        if field == 'username': placeholder = 'Username'
        if field == 'email': placeholder = 'Email'
        if field == 'password1': placeholder = 'Password'
        if field == 'password2': placeholder = 'Re-Enter Password'
        form.fields[field].widget.attrs.update({'class': 'form-control', 'placeholder': placeholder})

    return render(request, "login/register.html", {'form': form})