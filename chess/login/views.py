from django.shortcuts import render
from .forms import RegisterForm

def login_view(request):
    if request.method == 'POST':
        pass
    return render(request, "login/login.html")

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
    form = RegisterForm()

    for field in form.fields:
        if field == 'username': placeholder = 'Username'
        if field == 'email': placeholder = 'Email'
        if field == 'password1': placeholder = 'Password'
        if field == 'password2': placeholder = 'Re-Enter Password'
        form.fields[field].widget.attrs.update({'class': 'form-control', 'placeholder': placeholder})

    return render(request, "login/register.html", {'form': form})