from django.contrib import admin

# Register your models here.
from .models import Site, FeedProfile, Feedrun

admin.site.register(Site)
admin.site.register(FeedProfile)
admin.site.register(Feedrun)
