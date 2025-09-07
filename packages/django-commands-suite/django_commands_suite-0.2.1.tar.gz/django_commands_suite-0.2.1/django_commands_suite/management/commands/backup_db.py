import os
import subprocess
import shutil
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django_commands_suite.utils import log_command

class Command(BaseCommand):
   """
      Backup the database into a `.sql` file.

      Supported databases:
      - SQLite
      - PostgreSQL
      - MySQL

      Examples:
         python manage.py backup_db --db=sqlite
   """
   help = "Backup your database (SQLite, PostgreSQL, or MySQL)."
   
   def add_arguments(self, parser):
         parser.add_argument(
            "--db",
            type=str,
            choices=["sqlite", "postgres", "mysql"],
            required=True,
            help="Database type: sqlite, postgres, or mysql",
         )

   def handle(self, *args, **options):
      db_type = options["db"]
      timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
      output_file = f"backup_db{timestamp}.sql"

      db = settings.DATABASES["default"]
      name = db["NAME"]
      user = db.get("USER", "")
      password = db.get("PASSWORD", "")
      host = db.get("HOST", "localhost")
      port = db.get("PORT", "")

      try:
         if db_type == "sqlite":
               output_file = f"backup_db{timestamp}.sqlite3"
               shutil.copy(name, output_file)

         elif db_type == "postgres":
            env = os.environ.copy()
            env["PGPASSWORD"] = password
            cmd = [
               "pg_dump",
               "-h", host,
               "-p", str(port or 5432),
               "-U", user,
               "-f", output_file,
               name,
            ]
            subprocess.run(cmd, env=env, check=True)

         elif db_type == "mysql":
            cmd = [
               "mysqldump",
               "-h", host,
               "-P", str(port or 3306),
               "-u", user,
               f"-p{password}",
               name,
            ]
            with open(output_file, "w") as f:
               subprocess.run(cmd, stdout=f, check=True)

         log_command("backup_db" , args , "success" ,f"backup saved in {output_file}")
         self.stdout.write(self.style.SUCCESS(f"Backup saved to {output_file}"))

      except Exception as e:
            log_command("backup_db" , args , "error" ,f"Backup failed: {e}")
            self.stdout.write(self.style.ERROR(f"Backup failed: {e}"))
