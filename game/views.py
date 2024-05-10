from django.http import HttpRequest, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render

from game import models, services


def index(request: HttpRequest):
    """
    Show the first game page with the player creation form always visible.
    """

    games = models.Game.objects.all()

    if not games.exists():
        return HttpResponseNotFound("Game not found.")

    player = services.get_player(request.session.session_key)

    game = games.first()

    context = {
        "game": game,
        "game_choices": games,
        "player": player,
        "show_player_creation_form": True,
    }

    return render(request, "game/game.html", context)


def player(request: HttpRequest):

    if request.method == "POST":
        username = request.POST.get("username", "-")
        services.create_player(request, username)

    game = get_object_or_404(models.Game, slug=request.POST.get("game_slug"))

    return redirect("game", game.slug)


def game(request, game_slug):

    game = get_object_or_404(models.Game, slug=game_slug)

    player = services.get_player(request.session.session_key)

    context = {
        "game": game,
        "game_choices": [game],
        "player": player,
        "show_player_creation_form": player is None,
        "leaderboard_answer_count": services.LEADERBOARD_ANSWER_COUNT,
    }

    return render(request, "game/game.html", context)
