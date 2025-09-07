from django.db import models
from django.utils import timezone

class CommandLog(models.Model):
   name = models.CharField(max_length=100)   
   args = models.TextField(blank=True, null=True)  
   executed_at = models.DateTimeField(default=timezone.now)  
   status = models.CharField(max_length=20, choices=[
      ("success", "Success"),
      ("error", "Error"),
   ])
   message = models.TextField(blank=True, null=True)  

   def __str__(self):
      return f"{self.name} - {self.status} @ {self.executed_at}"
