from n4f2.models import Site, FeedProfile, Feedrun
from datetime import datetime, timedelta
from pytz import timezone
import requests, pytz, time, json


def add_feed_runs_to_db(feed_run_report):
    for run in feed_run_report['feed_run_details']['feed_runs']:
            for key in run.keys():
                fr = Feedrun(
                    id = key,
                    feed_name = run[key]['feedName'],
                    status_code = run[key]['statusCode'],
                    status_summary = run[key]['statusSummary'],
                    run_link = run[key]['runLink'],
                    console_link = run[key]['consoleLink'],
                    feed_profile = FeedProfile.objects.get(name=run[key]['feedProfile']),
                )

                update_feed_profile_dates(run[key]['lastReceived'], run[key]['lastSuccess'], key)

                verify_feed = Feedrun.objects.filter(id=fr.id)
                if verify_feed.exists() == False:
                    fr.save()


def update_feed_profile_dates(last_received, last_success, feed_profile_id):
    fp = FeedProfile.objects.get(pk=feed_profile_id)
    if fp. last_received == None or fp.last_received < last_received:
        fp.last_received = last_received
    if last_success != None and (fp.last_success == None or fp.last_success < last_success):
        fp.last_success = last_success
    
    fp.save()


def add_sites_to_db(all_sites):
    for site in all_sites:
        s = Site(
            id = site['id'],
            name = site['name']            
        )

        verify_site = Site.objects.filter(pk=s.id)
        if verify_site.exists() == False:
            s.save()

def parse_feedherder_json_data(feedherder_json):
    data = json.load(open(feedherder_json))
    all_sites = []
    all_profiles = []
    for process in data['processes']:
        site = {
            'id': process['site']['id'],
            'name': process['site']['name']
        }
        profile = {
            'id': process['id'],
            'name': process['name'].rstrip('\n'),
            'watching': process['watching'],
            'site_id': process['site']['id']
        }
        all_sites.append(site)
        all_profiles.append(profile)

    return { 'all_sites': all_sites, 'all_profiles': all_profiles }

    
def add_profiles_to_db(all_profiles):
    for profile in all_profiles:
        verify_site = Site.objects.filter(pk=profile['site_id'])
        if verify_site.exists() == True:
            fp = FeedProfile(
                id = profile['id'],
                name = profile['feedname'],
                site = Site.objects.get(pk=profile['site_id'])
            )

            verify_profile = FeedProfile.objects.filter(pk=fp.id)
            if verify_profile.exists() == False:
                fp.save()
        else:
            print(profile)



def parse_site_json_data(site_json):
    data = json.load(open(site_json))
    all_sites = []
    for site in data['sites']:
        site_data = {
            'id': site['id'],
            'name': site['name']
        }
        all_sites.append(site_data)
    
    return all_sites

def parse_feed_profile_json_data(profile_json):
    data = json.load(open(profile_json))
    all_profiles = []
    for profile in data['feed_profiles']:
        profile_data = {
            'id': int(profile['profileid']),
            'feedname': profile['feedname'],
            'site_id': int(profile['site_id'])
        }
        all_profiles.append(profile_data)

    return all_profiles
        

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
        'now': datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(days = 1),
        'dontReport': datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(days = 30),
        'localtime': time.strftime('%a %b %d %Y %H:%M:%S'),
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
            # if feed_json[i]['lastSuccess'] == None:
            #     feed_json[i]['lastSuccess'] = '1969-01-01T00:00:00Z'
            feedName, feedProfile = feed_json[i]['feedName'].split(' using profile ')
            feed_run = { feed_json[i]['runId']: {
                'feedName': feedName,
                'feedProfile': feedProfile.rstrip('\n'),
                'statusCode': feed_json[i]['statusCode'],
                'statusSummary': feed_json[i]['statusSummary'],
                'lastReceived': feed_json[i]['lastReceived'],
                'lastSuccess': feed_json[i]['lastSuccess'],
                'siteName': feed_json[i]['siteName'],
                'runLink': 'https://portal.richrelevance.com/rrfeedherder/result.jsp?runId=' + str(feed_json[i]['runId']),
                'consoleLink': 'https://portal.richrelevance.com/rrfeedherder/api/feed/output/' + str(feed_json[i]['runId'])
                }
            }
                      
            i += 1

    
    return parsed_response
