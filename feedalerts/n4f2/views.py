from django.shortcuts import render
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
        feedruns = Feedrun.objects.filter(last_received__gte=datetime.now()-timedelta(days=30))
        lateruns = Feedrun.objects.exclude(last_received__gte=datetime.now()-timedelta(days=30))
        context = {
            'feedruns': feedruns, 
            'lateruns': lateruns,
            'feed_run_report': feed_run_report,
        }
        return render(request, 'n4f2/index.html', context)
