from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from n4f2 import utils

from .models import Feedrun, Ignoredsite

# Create your views here.
def index(request):
    feed_run_report = utils.create_feed_run_report()
    if type(feed_run_report) is str:
        return HttpResponse(feed_run_report)
    else:
        utils.add_feed_runs_to_db(feed_run_report)
        feedruns = Feedrun.objects.filter(last_received__gte=datetime.now()-timedelta(days=30)).order_by("site_name").order_by("feed_profile", "-last_received").distinct("feed_profile")
        lateruns = Feedrun.objects.exclude(last_received__gte=datetime.now()-timedelta(days=30)).order_by("site_name")
        hooklogicruns = Feedrun.objects.filter(site_name="HookLogic", last_received__gte=datetime.now()-timedelta(days=1)).order_by("-last_received")
        context = {
            'feedruns': feedruns, 
            'lateruns': lateruns,
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
        
