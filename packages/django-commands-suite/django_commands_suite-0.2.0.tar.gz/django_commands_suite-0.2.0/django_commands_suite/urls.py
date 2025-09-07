from django.urls import path
from . import views

urlpatterns = [
   path("terminal/", views.terminal_page, name="terminal"),
   #path("dcs_terminal/run/", views.run_command, name="dcs_run_command"),
]
