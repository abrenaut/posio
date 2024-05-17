import django_eventstream
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("player", views.player, name="player"),
    path("<game_slug>", views.game, name="game"),
]
