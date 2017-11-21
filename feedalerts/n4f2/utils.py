from n4f2.models import Feedrun, Ignoredsite
from datetime import datetime, timedelta
from pytz import timezone
import requests, pytz, time


def add_feed_runs_to_db(feed_run_report):
    for run in feed_run_report['feed_run_details']['feed_runs']:
            for key in run.keys():
                fr = Feedrun(
                    run_id = key,
                    site_name = run[key]['siteName'],
                    feed_profile = run[key]['feedProfile'],
                    feed_name = run[key]['feedName'],
                    status_code = run[key]['statusCode'],
                    status_summary = run[key]['statusSummary'],
                    last_received = run[key]['lastReceived'],
                    last_success = run[key]['lastSuccess'],
                    run_link = run[key]['runLink']
                )

                verify = Feedrun.objects.filter(run_id=fr.run_id)
                if verify.exists():
                    print(str(verify[0].run_id) + " already exists. Skipping.")
                else:
                    fr.save()


def create_feed_run_report():
    feed_json = fetch_feed_status()
    if type(feed_json) is int:
        return "Feed Status API returned error code " + str(feed_json)

    ignore_list = create_ignored_site_list()
    time_settings = create_time_settings_json()
    feed_run_details = parse_api_response(feed_json, ignore_list, time_settings)

    return {'ignore_list': ignore_list, 'time_settings': time_settings, 'feed_run_details': feed_run_details }


def fetch_feed_status():
    response = requests.get('https://portal.richrelevance.com/feedstatus/v1/?feedType=catalog')

    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def create_ignored_site_list():
    ignored_site_list = []
    site_objects = Ignoredsite.objects.all()
    for site in site_objects:
        ignored_site_list.append(site.site_name)
    
    return ignored_site_list


def create_time_settings_json():
    time_settings = {
        'utcTimeFormat': '%Y-%m-%dT%H:%M:%SZ',
        'pacific': timezone('US/Pacific'),
        'now': datetime.utcnow() - timedelta(days = 1),
        'dontReport': datetime.utcnow() - timedelta(days = 30),
        'localtime': time.asctime(time.localtime(time.time())),
    }

    return time_settings


def parse_api_response(feed_json, ignore_list, time_settings):
    parsed_response = {
        'feed_runs': [],
        'late': [],
        'error': [],
        'interupt': [],
        'unfinished': [],
        'postponed': []
        }

    i = 0
    while i < len(feed_json):
        yes = 0
        for index in range(len(ignore_list)):
            if feed_json[i]['siteName'] == ignore_list[index]:
                i += 1
                yes = 1
        if yes == 1:
            continue
        if feed_json[i]['siteName'].startswith('ZZZ') or feed_json[i]['siteName'].startswith('YYY') or feed_json[i]['siteName'].startswith('Storre'):
            i += 1
        else:
            feedName, feedProfile = feed_json[i]['feedName'].split(' using profile ')
            feed_run = { feed_json[i]['runId']: {
                'feedName': feedName,
                'feedProfile': feedProfile.rstrip('\n'),
                'statusCode': feed_json[i]['statusCode'],
                'statusSummary': feed_json[i]['statusSummary'],
                'lastReceived': feed_json[i]['lastReceived'],
                'lastSuccess': feed_json[i]['lastSuccess'],
                'siteName': feed_json[i]['siteName'],
                'runLink': 'https://portal.richrelevance.com/rrfeedherder/result.jsp?runId=' + str(feed_json[i]['runId'])
                }
            }
                      
            # import pdb
            # pdb.set_trace()
            lastrecd_datetime = datetime.strptime(feed_json[i]['lastReceived'], time_settings['utcTimeFormat'])

            if lastrecd_datetime < time_settings['now']:
                if lastrecd_datetime < time_settings['dontReport']:
                    parsed_response['late'].append(feed_json[i]['runId'])
                    feed_run[feed_json[i]['runId']]['statusCode'] = feed_run[feed_json[i]['runId']]['statusCode'] + '_LATE'
            if feed_json[i]['statusCode'] == 'ERROR' or feed_json[i]['statusCode'] == 'COMPLETE_WITH_FATAL_ERRORS':
                parsed_response['error'].append(feed_json[i]['runId'])
            if feed_json[i]['statusCode'] == 'INTERRUPTED':
                parsed_response['interupt'].append(feed_json[i]['runId'])
            if feed_json[i]['statusCode'] == 'UNFINISHED':
                parsed_response['unfinished'].append(feed_json[i]['runId'])
            if feed_json[i]['statusCode'] == 'POSTPONED_SITE_CONFLICT':
                parsed_response['postponed'].append(feed_json[i]['runId'])
            
            parsed_response['feed_runs'].append(feed_run)
            i += 1

    
    return parsed_response
