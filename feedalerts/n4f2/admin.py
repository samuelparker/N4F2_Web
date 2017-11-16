from django.contrib import admin

# Register your models here.
from .models import Feedruns, Ignorelist

admin.site.register(Feedruns)
admin.site.register(Ignorelist)