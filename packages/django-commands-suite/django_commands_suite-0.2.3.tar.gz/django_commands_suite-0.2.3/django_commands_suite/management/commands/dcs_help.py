from django.core.management.base import BaseCommand
from django.core.management import get_commands, load_command_class
import inspect
import textwrap

class Command(BaseCommand):
    help = "Show all available commands in Django Commands Suite (DCS) with usage examples"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Django Commands Suite (DCS)"))
        self.stdout.write("Available commands:\n")

        commands = get_commands()

        for name, app in commands.items():
            if app == "django_commands_suite":
                try:
                    cmd_class = load_command_class(app, name)
                    usage = getattr(cmd_class, "help", "No description provided.")
                    doc = inspect.getdoc(cmd_class) or ""
                except Exception:
                    usage = "No description available."
                    doc = ""

                self.stdout.write("=" * 60)
                self.stdout.write(f"    {name}")
                self.stdout.write(f"    Description: {usage}")
                self.stdout.write(f"    Usage: python manage.py {name}")

                # extract examples from docstring if available
                if "Examples:" in doc:
                    self.stdout.write("")
                    self.stdout.write("    Examples:")
                    for line in doc.splitlines():
                        if line.strip().startswith("python manage.py"):
                            self.stdout.write("     " + textwrap.dedent(line))
                self.stdout.write("")
        self.stdout.write("=" * 60)
