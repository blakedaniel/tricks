from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# function based views
from main.views import (home, register)
# class based views
from main.views import (CreateGame, JoinGame, CurGame,
                        StartGame, Bet, PlayCard,
                        SidebarUpdate, GamePlayUpdate,)


urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path("admin/", admin.site.urls),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(),
         name="logout"),
    path("register/", register, name="register"),
]

# django debug toolbar
#urlpatterns += [path('__debug__/', include('debug_toolbar.urls')),]

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


# django static files
urlpatterns += staticfiles_urlpatterns()

# htmc views
htmx_patterns = [path("game/<int:game_id>/sidebar_update", SidebarUpdate.as_view(),
                      name="sidebar_update"),
                 path("game/<int:game_id>/game_play_update", GamePlayUpdate.as_view(),
                      name="game_play_update"),]

urlpatterns += htmx_patterns