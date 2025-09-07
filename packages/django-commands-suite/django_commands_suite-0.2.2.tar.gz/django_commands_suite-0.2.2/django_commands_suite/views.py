from .models import CommandLog
from django.shortcuts import render


import io
from django.core.management import call_command
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django_commands_suite.utils import log_command

@csrf_exempt
def run_command(request):
    if request.method == "POST":
        command = request.POST.get("command", "").strip()
        out = io.StringIO()

        if not command:
            return JsonResponse({"status": "error", "output": "No command provided."})

        try:
            parts = command.split()
            call_command(*parts, stdout=out)

            # log to CommandLog
            log_command(parts[0], {"args": parts[1:]}, "success", out.getvalue())

            return JsonResponse({"status": "success", "output": out.getvalue()})
        except Exception as e:
            log_command(command.split()[0], {}, "error", str(e))
            return JsonResponse({"status": "error", "output": str(e)})

    return JsonResponse({"status": "error", "output": "Invalid request method."})





def terminal_page(request):
   return render(request, "django_commands_suite/webterminal.html")