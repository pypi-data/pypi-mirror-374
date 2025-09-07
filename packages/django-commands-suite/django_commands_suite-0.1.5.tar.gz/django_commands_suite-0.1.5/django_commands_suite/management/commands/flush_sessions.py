from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand
from django_commands_suite.utils import log_command

class Command(BaseCommand):
   
   help = "Flush all sessions from database ."

   def handle(self, *args, **options):
      try:
         count, _ = Session.objects.all().delete()
         self.stdout.write(self.style.SUCCESS(f"Deleted {count} sessions."))
         log_command("flush_sessions", args, "success", f"{count} deleted")
      except Exception as e:
         self.stderr.write(str(e))
         log_command("flush_sessions", args, "error", str(e))
