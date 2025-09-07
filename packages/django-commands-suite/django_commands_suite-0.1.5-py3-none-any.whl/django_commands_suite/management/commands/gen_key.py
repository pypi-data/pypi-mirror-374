from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key
from django_commands_suite.utils import log_command

class Command(BaseCommand):
   
   help = "Generate a new Django SECRET_KEY."

   def handle(self, *args, **options):
      try:
         key = get_random_secret_key()
         self.stdout.write(self.style.SUCCESS(f"New SECRET_KEY: {key}"))
         log_command("generate_secret_key", args, "success", key)
      except Exception as e:
         self.stderr.write(str(e))
         log_command("generate_secret_key", args, "error", str(e))
