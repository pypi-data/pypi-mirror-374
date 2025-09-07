from django.core.management.base import BaseCommand
from django.core.management import get_commands, load_command_class

class Command(BaseCommand):
   help = "Show all available commands in Django Commands Suite (DCS)"

   def handle(self, *args, **kwargs):
      self.stdout.write(self.style.SUCCESS("Django Commands Suite (DCS)"))
      self.stdout.write("Available commands:\n")

      commands = get_commands()

      for name, app in commands.items():
         if app == "django_commands_suite":
               try:
                  cmd = load_command_class(app, name)
                  usage = getattr(cmd, "help", "No description provided.")
               except Exception:
                  usage = "No description available."

               self.stdout.write("=" * 50)  
               self.stdout.write(f"👉 {name}")
               self.stdout.write(f"    Usage: python manage.py {name}")
               self.stdout.write(f"    {usage}\n")

      self.stdout.write("=" * 50)  
