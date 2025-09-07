from django.apps import apps
from django.core.management.base import BaseCommand
from faker import Faker
from django.db import models
from django_commands_suite.utils import log_command

fake = Faker()

class Command(BaseCommand):
    """
    Insert dummy data into a model with realistic fake values.

    Examples:
        python manage.py dummy_data --model app_label.ModelName --count 10
    """

    help = "Insert dummy data into a model with realistic fake values using mapping instead of if-else."

    def add_arguments(self, parser):
        parser.add_argument("--model", type=str, required=True, help="app.ModelName")
        parser.add_argument("--count", type=int, default=2)

    def handle(self, *args, **options):
        try:
            app_label, model_name = options["model"].split(".")
            model = apps.get_model(app_label, model_name)

            generators = {
                models.CharField: lambda f: fake.text(getattr(f, "max_length", 20))[: getattr(f, "max_length", 20)],
                models.TextField: lambda f: fake.paragraph(),
                models.EmailField: lambda f: fake.email(),
                models.URLField: lambda f: fake.url(),
                models.IntegerField: lambda f: fake.random_int(),
                models.FloatField: lambda f: fake.pyfloat(left_digits=3, right_digits=2),
                models.DateField: lambda f: fake.date(),
                models.DateTimeField: lambda f: fake.date_time(),
                models.BooleanField: lambda f: fake.boolean(),
                models.DecimalField: lambda f: fake.pydecimal(
                    left_digits=f.max_digits - f.decimal_places,
                    right_digits=f.decimal_places,
                ),
            }

            fields = [f for f in model._meta.get_fields() if getattr(f, "editable", False) and not f.auto_created]

            created_count = 0
            for _ in range(options["count"]):
                data = {}
                for field in fields:
                    generator = next(
                        (gen for field_type, gen in generators.items() if isinstance(field, field_type)),
                        None,
                    )
                    if generator:
                        data[field.name] = generator(field)

                obj = model.objects.create(**data)
                created_count += 1

            self.stdout.write(self.style.SUCCESS(f"{created_count} dummy objects created for {options['model']}"))
            log_command("create_dummy_data", options, "success", f"{created_count} objects created")

        except Exception as e:
            self.stderr.write(self.style.ERROR(str(e)))
            log_command("create_dummy_data", options, "error", str(e))
