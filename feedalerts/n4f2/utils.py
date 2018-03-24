from n4f2.models import Site, FeedProfile, FeedRun
from datetime import datetime, timedelta
from pytz import timezone
import requests, pytz, time, json


def add_feed_runs_to_db(feed_run_report):
    for feed_run in feed_run_report['feed_run_details']:
            for key in feed_run.keys():
                site = Site.objects.get_or_create(
                    id = feed_run[key]['siteId'], 
                    name = feed_run[key]['siteName']
                )

                profile = FeedProfile.objects.get_or_create(
                    id = feed_run[key]['feedProfileId'], 
                    name = feed_run[key]['feedProfile'], 
                    site = site[0]
                )

                try: 
                    fr = FeedRun.objects.get(pk = key)
                    if fr.last_success == None or fr.last_success < feed_run[key]['lastSuccess']:
                        fr.last_success = feed_run[key]['lastSuccess']
                        fr.save()
                    if fr.status_code == 'UNFINISHED' and feed_run[key]['statusCode'] != 'UNFINISHED':
                        fr.status_code = feed_run[key]['statusCode']
                        fr.save()
                except FeedRun.DoesNotExist:    
                    fr = FeedRun(id = key,
                        name = feed_run[key]['feedName'],
                        status_code = feed_run[key]['statusCode'],
                        status_summary = feed_run[key]['statusSummary'],
                        run_link = feed_run[key]['runLink'],
                        console_link = feed_run[key]['consoleLink'],
                        last_received = feed_run[key]['lastReceived'],
                        last_success = feed_run[key]['lastSuccess'],
                        feed_profile = profile[0]
                    )
                    fr.save()

       
def create_feed_run_report():
    feed_json = fetch_feed_status()
    if type(feed_json) is int:
        return "Feed Status API returned error code " + str(feed_json)

    time_settings = create_time_settings_json()
    feed_run_details = parse_api_response(feed_json, time_settings)

    return {'time_settings': time_settings, 'feed_run_details': feed_run_details }


def fetch_feed_status():
    response = requests.get('https://portal.richrelevance.com/feedstatus/v1/?feedType=catalog')

    if response.status_code == 200:
        return response.json()
    else:
        return response.status_code


def create_time_settings_json():
    time_settings = {
        'utcTimeFormat': '%Y-%m-%dT%H:%M:%SZ',
        'pacific': timezone('US/Pacific'),
        'now': datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(days = 1),
        'late': datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(days = 2),
        'dontReport': datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(days = 30),
        'localtime': time.strftime('%a %b %d %Y %H:%M:%S'),
    }

    return time_settings

def format_date_response(date_string):
    if date_string != None:
        date_string = datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.UTC)

    return date_string

def parse_api_response(feed_json, time_settings):
    feed_runs = []
    i = 0
    while i < len(feed_json):
        if feed_json[i]['siteName'].startswith('ZZZ') or feed_json[i]['siteName'].startswith('YYY') or feed_json[i]['siteName'].startswith('Storre'):
            i += 1
        elif format_date_response(feed_json[i]['lastReceived']) >= datetime.utcnow().replace(tzinfo=pytz.UTC) - timedelta(days = 90):
            i += 1
        else:
            feedName, feedProfile = feed_json[i]['feedName'].split(' using profile ')
            feed_run = { feed_json[i]['runId']: {
                'feedName': feedName,
                'feedProfile': feedProfile.rstrip('\n'),
                'statusCode': feed_json[i]['statusCode'],
                'statusSummary': feed_json[i]['statusSummary'],
                'lastReceived': format_date_response(feed_json[i]['lastReceived']),
                'lastSuccess': format_date_response(feed_json[i]['lastSuccess']),
                'siteName': feed_json[i]['siteName'],
                'siteId': feed_json[i]['siteId'],
                'feedProfileId': feed_json[i]['feedProfileId'],
                'runLink': 'https://portal.richrelevance.com/rrfeedherder/result.jsp?runId=' + str(feed_json[i]['runId']),
                'consoleLink': 'https://portal.richrelevance.com/rrfeedherder/api/feed/output/' + str(feed_json[i]['runId'])
                }
            }

            feed_runs.append(feed_run)   
            i += 1

    return feed_runs

'''
begin legacy methods for bulk import of site and profile data from Feed Herder

def add_sites_and_profiles_to_db(feedherder_data):
    add_sites_to_db(feedherder_data['all_sites'])
    add_profiles_to_db(feedherder_data['all_profiles'])


def update_feed_profile_dates(last_received, last_success, feed_profile_id):
    fp = FeedProfile.objects.get(pk=feed_profile_id)
    if fp.last_received == None or fp.last_received < last_received:
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


def add_profiles_to_db(all_profiles):
    for profile in all_profiles:
        verify_site = Site.objects.filter(pk=profile['site_id'])
        uniqify_profile_name(profile)
        if verify_site.exists() == True:
            fp = FeedProfile(
                id = profile['id'],
                name = profile['name'],
                site = Site.objects.get(pk=profile['site_id'])
            )

            verify_profile = FeedProfile.objects.filter(pk=fp.id)
            if verify_profile.exists() == False:
                fp.save()
        else:
            print(profile)


def uniqify_profile_name(profile):
    profile_query = FeedProfile.objects.filter(name=profile['name'])
    if profile_query.count() >= 1:
        profile['name'] = profile['name'] + '_' + str(profile['id'])

    return profile


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

end legacy methods for bulk import of site and profile data from Feed Herder
'''