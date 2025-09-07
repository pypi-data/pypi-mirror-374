from django.urls import path
from . import views

urlpatterns = [
   path("terminal/", views.terminal_page, name="dcs_terminal"),
   path("terminal/run/", views.run_command, name="dcs_run_command"),
]
