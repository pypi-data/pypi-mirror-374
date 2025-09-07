import shutil, os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import now
from django_commands_suite.utils import log_command

class Command(BaseCommand):
   
   help = "Backup MEDIA_ROOT into a zip file."

   def handle(self, *args, **options):
      try:
         output_file = f"media_backup_{now().strftime('%Y%m%d%H%M%S')}.zip"
         shutil.make_archive(output_file.replace(".zip",""), 'zip', settings.MEDIA_ROOT)
         
         self.stdout.write(self.style.SUCCESS(f"Media backup created: {output_file}"))
         log_command("backup_media", args, "success", f"File: {output_file}")
      
      except Exception as e:
         self.stderr.write(str(e))
         log_command("backup_media", args, "error", str(e))
