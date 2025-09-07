from .models import CommandLog
from django.shortcuts import render




def terminal_page(request):
   return render(request, "webterminal.html")