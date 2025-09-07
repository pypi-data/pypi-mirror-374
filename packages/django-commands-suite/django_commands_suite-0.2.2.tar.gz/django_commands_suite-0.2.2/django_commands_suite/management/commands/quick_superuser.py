from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django_commands_suite.utils import log_command


class Command(BaseCommand):
   help = "Quickly create a default superuser (username=djadmin, password=djadmin, email=admin@dj.com)"

   def handle(self, *args, **options):
      User = get_user_model()
      if not User.objects.filter(username="djadmin").exists():
            User.objects.create_superuser(
               username="djadmin",
               email="admin@dj.com",
               password="djadmin"
            )
            log_command("quick_superuser", args ,"success","Superuser 'djadmin' created successfully")
            self.stdout.write(self.style.SUCCESS("Superuser 'djadmin' created successfully!"))
      else:
            log_command("quick_superuser", args ,"error", "Superuser 'djadmin' already exists.")
            self.stdout.write(self.style.WARNING("Superuser 'djadmin' already exists."))
