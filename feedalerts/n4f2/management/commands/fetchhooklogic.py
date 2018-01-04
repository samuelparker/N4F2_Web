from django.core.management.base import BaseCommand
from n4f2.models import Feedrun, Ignoredsite
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
        fr = Feedrun(
            run_id = hl_feed_response["runId"],
            site_name = hl_feed_response["siteName"],
            feed_profile = "hooklogic",
            feed_name = hl_feed_response['feedName'].split('using profile')[0],
            status_code = hl_feed_response['statusCode'],
            status_summary = hl_feed_response['statusSummary'],
            last_received = hl_feed_response['lastReceived'],
            last_success = hl_feed_response['lastSuccess'],
            run_link = 'https://portal.richrelevance.com/rrfeedherder/result.jsp?runId=' + str(hl_feed_response['runId']),
            console_link = 'https://portal.richrelevance.com/rrfeedherder/api/feed/output/' + str(hl_feed_response['runId']),
            notification_sent = False
        )

        verify = Feedrun.objects.filter(run_id=fr.run_id)
        if verify.exists() == False:
            fr.save()

    
    def handle(self, *args, **options):
        self.add_hook_feed_to_db()

        