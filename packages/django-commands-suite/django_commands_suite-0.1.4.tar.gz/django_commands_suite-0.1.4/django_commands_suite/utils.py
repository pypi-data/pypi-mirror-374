from .models import CommandLog

def log_command(name, args=None, status="success", message=""):
   CommandLog.objects.create(
      name=name,
      args=str(args),
      status=status,
      message=message
   )
