from django.core.management.base import BaseCommand
from n4f2.models import Site, FeedProfile, FeedRun
from n4f2 import utils
import requests

class Command(BaseCommand):
    
    def fetch_hook_feed_status(self):
        response = requests.get('https://portal.richrelevance.com/feedstatus/v1/?feedType=catalog&siteId=852')
        if response.status_code != 200:
            for i in range(10):
                self.fetch_hook_feed_status()
        else:
            return response.json()

    
    def add_hook_feed_to_db(self):
        hl_feed_response = self.fetch_hook_feed_status()
        hl_feed_response = hl_feed_response[0]
        try: 
            fr = FeedRun.objects.get(pk = hl_feed_response["runId"])
            if fr.last_success == None or fr.last_success < utils.format_date_response(hl_feed_response['lastSuccess']):
                fr.last_success = hl_feed_response['lastSuccess']
                fr.save()
            if fr.status_code == 'UNFINISHED' and hl_feed_response['statusCode'] != 'UNFINISHED':
                fr.status_code = hl_feed_response['statusCode']
                fr.save()
        except FeedRun.DoesNotExist:    
            fr = FeedRun(id = key,
                name = hl_feed_response['feedName'],
                status_code = hl_feed_response['statusCode'],
                status_summary = hl_feed_response['statusSummary'],
                run_link = hl_feed_response['runLink'],
                console_link = hl_feed_response['consoleLink'],
                last_received = hl_feed_response['lastReceived'],
                last_success = hl_feed_response['lastSuccess'],
                feed_profile = FeedProfile.objects.get(name="hooklogic")
            )
            fr.save()

    
    def handle(self, *args, **options):
        self.add_hook_feed_to_db()

        