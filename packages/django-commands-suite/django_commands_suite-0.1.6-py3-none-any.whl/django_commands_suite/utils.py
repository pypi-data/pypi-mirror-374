from django.core.management import call_command
from .models import CommandLog
import io

def log_command(name, args=None, status="success", message=""):
   CommandLog.objects.create(
      name=name,
      args=str(args),
      status=status,
      message=message
   )





def run_command(command_name: str, *args, **kwargs):
    """
    Run a Django management command from code (instead of CLI).
    It will capture output and log it automatically into CommandLog.
    """
    out = io.StringIO()
    try:
        call_command(command_name, *args, stdout=out, stderr=out, **kwargs)
        output = out.getvalue()
        CommandLog.objects.create(
            command=command_name,
            status="success",
            message=output,
            options=str(kwargs)
        )
        return output
    except Exception as e:
        CommandLog.objects.create(
            command=command_name,
            status="error",
            message=str(e),
            options=str(kwargs)
        )
        raise e
