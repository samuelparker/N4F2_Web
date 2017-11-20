from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from n4f2 import utils

from .models import Feedrun, Ignoredsite

# Create your views here.
def index(request):
    feed_run_report = utils.create_feed_run_report()
    if type(feed_run_report) is str:
        return HttpResponse(feed_run_report)
    else:
        utils.add_feed_runs_to_db(feed_run_report)
        feedruns = Feedrun.objects.all()
        context = {
            'feedruns': feedruns, 
            'feed_run_report': feed_run_report,
        }
        return render(request, 'n4f2/index.html', context)
