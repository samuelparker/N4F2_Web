from django.contrib import admin

# Register your models here.
from .models import Feedrun, Ignoredsite

admin.site.register(Feedrun)
admin.site.register(Ignoredsite)