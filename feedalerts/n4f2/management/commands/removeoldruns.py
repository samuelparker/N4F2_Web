from django.core.management.base import BaseCommand
from n4f2.models import Site, FeedProfile, FeedRun
from datetime import datetime, timedelta

class Command(BaseCommand):
    
    def remove_old_runs(self):
        old_runs = FeedRun.objects.filter(last_received__lte=datetime.today()-timedelta(days=90))

        for run in old_runs:
            run.delete()

    
    def handle(self, *args, **options):
        self.remove_old_runs()
        