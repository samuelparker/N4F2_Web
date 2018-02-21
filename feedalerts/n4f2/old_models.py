from django.db import models

# Create your models here.
class Feedrun(models.Model):
    run_id = models.IntegerField()
    site_name = models.CharField(max_length=200)
    feed_profile = models.CharField(max_length=200)
    feed_name = models.CharField(max_length=200)
    status_code = models.CharField(max_length=200)
    status_summary = models.CharField(max_length=200)
    run_link = models.CharField(max_length=200)
    console_link = models.CharField(max_length=200)
    notification_sent = models.BooleanField(default=False)
    last_received = models.DateTimeField('date received')
    last_success = models.DateTimeField('date published')

    def __str__(self):
        return str(self.run_id)

class Ignoredsite(models.Model):
    site_name = models.CharField(max_length=200)

    def __str__(self):
        return self.site_name
