from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from api.models import GameBoard


@login_required(login_url="login")
def gameHistory(request):
    games = GameBoard.objects.filter(whiteUser = request.user.id) | GameBoard.objects.filter(blackUser = request.user.id)
    return render(request, "game_history.html", {'games': games.order_by('-id')})


@login_required(login_url="login")
def replay(request, game_id):
    game = GameBoard.objects.get(id=game_id)
    context = {
        'playingBlack': int(game.blackUser.id == request.user.id),
        'moves': game.moves,
        'promotions': game.promos,
        'captured': game.captured,
        'winner': game.winner
    }
    return render(request, "replay.html", context)