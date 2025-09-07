from .models import CommandLog
from django.shortcuts import render




def terminal_page(request):
   return render(request, "django_commands_suite/webterminal.html")