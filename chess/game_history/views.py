from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from api.models import GameBoard


@login_required(login_url="login")
def gameHistory(request):
    games = GameBoard.objects.filter(whiteUser = request.user.id) | GameBoard.objects.filter(blackUser = request.user.id)
    return render(request, "game_history.html", {'games': games})
