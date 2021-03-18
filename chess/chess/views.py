from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required(login_url="login")
def home(request):
    return render(request, "home.html")

@login_required(login_url="login")
def game(request, game_id):
    return render(request, "home.html", {'game_id': game_id})

def test(request):
    return render(request, "test.html")