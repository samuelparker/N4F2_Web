#!/usr/bin/env python

from datetime import datetime, timedelta
from dateutil import parser
from pytz import timezone
import requests, pytz, pdb, os, os.path, sys, re, struct, copy, time, shutil, feedAPIparseFunction



utcTimeFormat = '%Y-%m-%dT%H:%M:%SZ'
pacific = timezone('US/Pacific')
now = datetime.utcnow() - timedelta(days = 1)
# now = datetime.utcnow() - timedelta(days = 7)

dontReport = datetime.utcnow() - timedelta(days = 30)

openIgnoreList = open('ignoreList.txt')
ignoreList = openIgnoreList.readlines()
openIgnoreList.close()

for index in range(len(ignoreList)):
	ignoreList[index] = ignoreList[index].rstrip('\n')


feedJson = requests.get('https://portal.richrelevance.com/feedstatus/v1/?feedType=catalog').json()

feedRuns = {}
late = []
error = []
interupt = []
unfinn = []
postponed = []

i = 0
while i < len(feedJson):
	yes = 0
	for index in range(len(ignoreList)):
		if feedJson[i]['siteName'] == ignoreList[index]:
			i += 1
			yes = 1
	if yes == 1:
		continue
	if feedJson[i]['siteName'].startswith('ZZZ') or feedJson[i]['siteName'].startswith('YYY') or feedJson[i]['siteName'].startswith('Storre'):
		i += 1
	else:
		feedName, feedProfile = feedJson[i]['feedName'].split(' using profile ')
		feedRuns[feedJson[i]['runId']] = {
			'feedName': feedName,
			'feedProfile': feedProfile.rstrip('\n'),
			'statusCode': feedJson[i]['statusCode'],
			'statusSummary': feedJson[i]['statusSummary'],
			'lastReceived': feedJson[i]['lastReceived'],
			'lastSuccess': feedJson[i]['lastSuccess'],
			'siteName': feedJson[i]['siteName'],
			'runLink': 'https://portal.richrelevance.com/rrfeedherder/result.jsp?runId=' + str(feedJson[i]['runId'])
			}
		if feedJson[i]['lastReceived'] < now.strftime(utcTimeFormat):
			if feedJson[i]['lastReceived'] > dontReport.strftime(utcTimeFormat):
				late.append(feedJson[i]['runId'])
		if feedJson[i]['statusCode'] == 'ERROR' or feedJson[i]['statusCode'] == 'COMPLETE_WITH_FATAL_ERRORS':
			error.append(feedJson[i]['runId'])
		if feedJson[i]['statusCode'] == 'INTERRUPTED':
			interupt.append(feedJson[i]['runId'])
		if feedJson[i]['statusCode'] == 'UNFINISHED':
			unfinn.append(feedJson[i]['runId'])
		if feedJson[i]['statusCode'] == 'POSTPONED_SITE_CONFLICT':
			postponed.append(feedJson[i]['runId'])
		i += 1

for index in range(len(error)):
	try:
		late.remove(error[index])
	except ValueError:
		continue
	else:
		continue

print(len(late))

localtime = time.asctime(time.localtime(time.time()))
filename = 'Feed Runs '+ localtime
filename = filename.replace(' ', '_')
filename = filename.replace(':', '_')
fileNameSplit = filename.split('_')
fileNameSplit.pop(8)
fileNameSplit.pop(7)
fileNameSplit.pop(6)
fileNameSplit.pop(4)
filename = '_'.join(fileNameSplit)
filename = filename.replace('_', " ")


print(filename)
feedCheck = open('index.html', 'w+')

feedCheck.write('''
<html><head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1"><title>N4F 2.0</title>
<style type="text/css">
html {background-color: white;}
h1 {font-family: "Times Roman", serif; font-size: 15pt; font-weight: bold;}
body {margin: 10px; font-family: "Times Roman", serif; font-size: 10pt; color: black; background-color: white;}
table.n4f2 {border-collapse: collapse; border: 1px solid; border-color: #E1EEF4; width: 800px;}
th {font-family: "Times Roman", serif; font-size: 13pt; border: 1px solid; border-color: #E1EEF4; font-weight: bold; padding: 5px 5px; color: white; background-color: #003E5C; text-align: center;}
td {font-family: "Times Roman", serif; font-size: 10pt; border: 1px solid; border-color: #E1EEF4; padding: 3px 3px;}
tr.ok {background-color: #c0ffc0; border-color: #E1EEF4;}
tr.bad {font-weight: bold; color: white; background-color: #dd6060; border-color: #ffc0c0;}
tr.delayed {font-weight: bold; color: #404040; background-color: #F5A61D; border-color: #E1EEF4;}
tr.abandon {color: #808080; background-color: #e0e0e0; border-color: #E1EEF4;}
span.sp {font-family: "Times Roman", serif; font-size: 15pt; color: #780000;}
table.legend {border-collapse: collapse; border: 1px solid; border-color: #E1EEF4; width: 300px;}
</style>
</head>
<body>
<center>
<p><h1>''' + filename + '''</h1></p>
<table class="n4f2">
<tr>
<th>Run ID</th>
<th>Site Name (ID)</th>
<th>Feed&nbsp;Date</th>
<th>Status Message (Code)</th>
</tr>
''')
feedAPIparseFunction.write_feed_info(error, feedRuns, feedCheck, 'error')
feedAPIparseFunction.write_feed_info(postponed, feedRuns, feedCheck, 'postponed')
feedAPIparseFunction.write_feed_info(late, feedRuns, feedCheck, 'late')
feedCheck.write('''
</center>
</body>
</html>
''')

feedCheck.close()

