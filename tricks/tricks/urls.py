"""
URL configuration for tricks project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
# function based views
from main.views import (home, register)
# class based views
from main.views import (CreateGame, JoinGame, CurGame,
                        StartGame, Bet, PlayCard,
                        SidebarUpdate, GamePlayUpdate,
                        EndGameUpdate, EndGame)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(),
         name="logout"),
    path("register/", register, name="register"),
]

# django debug toolbar
urlpatterns += [path('__debug__/', include('debug_toolbar.urls')),]

# game starting views
urlpatterns += [path("", home, name="home"),
                path("create_game/", CreateGame.as_view(), name="create_game"),
                path("join_game/", JoinGame.as_view(), name="join_game"),]

# game play views
urlpatterns += [path("game/<int:game_id>/", CurGame.as_view(), name="game"),
                path("game/<int:game_id>/start_game", StartGame.as_view(),
                     name="start_game"),
                path("game/<int:game_id>/bet", Bet.as_view(), name="bet"),
                path("game/<int:game_id>/play_card", PlayCard.as_view(),
                     name="play_card")]

# transition views
urlpatterns += [path("game/<int:game_id>/next_trick", CurGame.as_view(),
                     name="next_trick"),
                path("game/<int:game_id>/next_round", CurGame.as_view(), 
                     name="next_round"),]

htmx_patterns = [path("game/<int:game_id>/sidebar_update", SidebarUpdate.as_view(),
                      name="sidebar_update"),
                 path("game/<int:game_id>/game_play_update", GamePlayUpdate.as_view(),
                      name="game_play_update"),
                 path("game/<int:game_id>/waiting_to_end", EndGameUpdate.as_view(),
                      name="waiting_to_end"),
                 path("game/<int:game_id>/end_game", EndGame.as_view(),
                      name="end_game"),]

urlpatterns += htmx_patterns