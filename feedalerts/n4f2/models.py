from django.db import models

# Create your models here.
class Site(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class FeedProfile(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    watched = models.BooleanField(default=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class FeedRun(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    status_code = models.CharField(max_length=200)
    status_summary = models.CharField(max_length=200)
    run_link = models.CharField(max_length=200)
    console_link = models.CharField(max_length=200)
    notification_sent = models.BooleanField(default=False)
    last_received = models.DateTimeField('date received', null=True)
    last_success = models.DateTimeField('date published', null=True)    
    feed_profile = models.ForeignKey(FeedProfile, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)