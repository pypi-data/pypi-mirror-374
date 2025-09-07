from django.contrib import admin 
from .models import CommandLog



@admin.register(CommandLog)
class CommandLog(admin.ModelAdmin) : 
   list_display  = [ "id","name" , "status" ,"executed_at"]
   search_fields = ['name']
   list_filter = ["status"]

