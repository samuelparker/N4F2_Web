from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from n4f2 import utils

from .models import Site, FeedProfile, FeedRun

# Create your views here.
def index(request):
    request.session.set_expiry(600)
    feed_run_report = utils.create_feed_run_report()

    if type(feed_run_report) is str:
        return HttpResponse(feed_run_report)
    else:
        utils.add_feed_runs_to_db(feed_run_report)
        feedruns = FeedRun.objects.order_by("feed_profile__name", "-last_received").distinct("feed_profile__name")
        hooklogicruns = FeedRun.objects.filter(feed_profile__name="hooklogic").order_by("-last_received")
        context = {
            'feedruns': feedruns, 
            'hooklogicruns': hooklogicruns,
            'feed_run_report': feed_run_report,
        }
        return render(request, 'n4f2/index.html', context)

def notify(request, feedrun_pk):
    feedrun = get_object_or_404(Feedrun, pk=feedrun_pk)
    if feedrun.notification_sent == True:
        feedrun.notification_sent = False
    else:
        feedrun.notification_sent = True
    feedrun.save()
    return HttpResponse(status=200)
        
