#!/usr/bin/env python

from datetime import datetime, timedelta
from dateutil import parser
from pytz import timezone
import requests, pytz, pdb, os, os.path, sys, re, struct, copy, time, shutil



utcTimeFormat = '%Y-%m-%dT%H:%M:%SZ'
pacific = timezone('US/Pacific')
now = datetime.utcnow() - timedelta(days = 1)
# now = datetime.utcnow() - timedelta(days = 7)

dontReport = datetime.utcnow() - timedelta(days = 90)



feedJson = requests.get('https://portal.richrelevance.com/feedstatus/v1/?feedType=catalog').json()

feedRuns = {}
late = []
error = []
interupt = []
unfinn = []
postponed = []

i = 0
while i < len(feedJson):
	if feedJson[i]['siteName'].startswith('ZZZ') or feedJson[i]['siteName'].startswith('YYY') or feedJson[i]['siteName'].startswith('Storre'):
		i += 1
	else:
		feedName, feedProfile = feedJson[i]['feedName'].split(' using profile ')
		feedRuns[feedJson[i]['runId']] = {
			'feedName': feedName,
			'feedProfile': feedProfile,
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
		if feedJson[i]['statusCode'] == 'ERROR':
			error.append(feedJson[i]['runId'])
		if feedJson[i]['statusCode'] == 'INTERRUPTED':
			interupt.append(feedJson[i]['runId'])
		if feedJson[i]['statusCode'] == 'UNFINISHED':
			unfinn.append(feedJson[i]['runId'])
		if feedJson[i]['statusCode'] == 'POSTPONED_SITE_CONFLICT':
			postponed.append(feedJson[i]['runId'])
		i += 1


print(len(late))
print(late[0])

# testTime = time.asctime(time.localtime(feedRuns[late[j]]['lastReceived']))
# pdb.set_trace()

localtime = time.asctime(time.localtime(time.time()))
filename = 'Feed Runs '+ localtime + '.txt'
filename = filename.replace(' ', '_')
filename = filename.replace(':', '_')
fileNameSplit = filename.split('_')
fileNameSplit.pop(8)
fileNameSplit.pop(7)
fileNameSplit.pop(6)
filename = '_'.join(fileNameSplit)
filename = filename.replace('__', '_')

print(filename)
feedCheck = open(filename, 'w+')

if len(error) >= 1:
	j = 0
	feedCheck.write(str(len(error)) + ' feeds in ERROR state.\n')
	while j < len(error):
		runId = str(error[j])
		siteName = feedRuns[error[j]]['siteName']
		feedProfile = feedRuns[error[j]]['feedProfile']
		feedName = feedRuns[error[j]]['feedName']
		statusCode = feedRuns[error[j]]['statusCode']
		statusSummary = feedRuns[error[j]]['statusSummary']
		lastReceived = feedRuns[error[j]]['lastReceived']
		if feedRuns[error[j]]['lastSuccess'] == None:
			lastSuccess = 'NO PRIOR SUCESS.'
		else:
			lastSuccess = feedRuns[error[j]]['lastSuccess']
		runLink = feedRuns[error[j]]['runLink']

		feedCheck.write('\t' + runId +': {\t\'siteName\': ' + siteName + '\n')
		feedCheck.write('\t\t\t\t\'feedName\': ' + feedName + '\n')
		feedCheck.write('\t\t\t\t\'feedProfile\': ' + feedProfile +'\n')
		feedCheck.write('\t\t\t\t\'statusCode\': ' + statusCode + '\n')
		feedCheck.write('\t\t\t\t\'statusSummary\': ' + statusSummary + '\n')
		feedCheck.write('\t\t\t\t\'lastReceived\': ' + lastReceived + '\n')
		feedCheck.write('\t\t\t\t\'lastSuccess\': ' + lastSuccess + '\n')
		feedCheck.write('\t\t\t\t\'runLink\': ' + runLink + '\n')
		feedCheck.write('\t\t\t }' + '\n')
		j += 1

if len(error) >= 1:
	feedCheck.write('\n\n\n')

if len(postponed) >= 1:
	k = 0
	feedCheck.write(str(len(postponed)) + ' postponed feeds.\n')
	while k < len(postponed):
		runId = str(postponed[k])
		siteName = feedRuns[postponed[k]]['siteName']
		feedProfile = feedRuns[postponed[k]]['feedProfile']
		feedName = feedRuns[postponed[k]]['feedName']
		statusCode = feedRuns[postponed[k]]['statusCode']
		statusSummary = feedRuns[postponed[k]]['statusSummary']
		lastReceived = feedRuns[postponed[k]]['lastReceived']
		if feedRuns[postponed[k]]['lastSuccess'] == None:
			lastSuccess = 'NO PRIOR SUCESS.'
		else:
			lastSuccess = feedRuns[postponed[k]]['lastSuccess']
		runLink = feedRuns[postponed[k]]['runLink']

		feedCheck.write('\t' + runId +': {\t\'siteName\': ' + siteName + '\n')
		feedCheck.write('\t\t\t\t\'feedName\': ' + feedName + '\n')
		feedCheck.write('\t\t\t\t\'feedProfile\': ' + feedProfile +'\n')
		feedCheck.write('\t\t\t\t\'statusCode\': ' + statusCode + '\n')
		feedCheck.write('\t\t\t\t\'statusSummary\': ' + statusSummary + '\n')
		feedCheck.write('\t\t\t\t\'lastReceived\': ' + lastReceived + '\n')
		feedCheck.write('\t\t\t\t\'lastSuccess\': ' + lastSuccess + '\n')
		feedCheck.write('\t\t\t\t\'runLink\': ' + runLink + '\n')
		feedCheck.write('\t\t\t }' + '\n')
		k += 1

if len(postponed) >= 1:
	feedCheck.write('\n\n\n')

l = 0
feedCheck.write(str(len(late)) + ' late feeds.\n')
while l < len(late):
	runId = str(late[l])
	siteName = feedRuns[late[l]]['siteName']
	feedProfile = feedRuns[late[l]]['feedProfile']
	feedName = feedRuns[late[l]]['feedName']
	statusCode = feedRuns[late[l]]['statusCode']
	statusSummary = feedRuns[late[l]]['statusSummary']
	lastReceived = feedRuns[late[l]]['lastReceived']
	if feedRuns[late[l]]['lastSuccess'] == None:
		lastSuccess = 'NO PRIOR SUCESS.'
	else:
		lastSuccess = feedRuns[late[l]]['lastSuccess']
	runLink = feedRuns[late[l]]['runLink']

	feedCheck.write('\t' + runId +': {\t\'siteName\': ' + siteName + '\n')
	feedCheck.write('\t\t\t\t\'feedName\': ' + feedName + '\n')
	feedCheck.write('\t\t\t\t\'feedProfile\': ' + feedProfile +'\n')
	feedCheck.write('\t\t\t\t\'statusCode\': ' + statusCode + '\n')
	feedCheck.write('\t\t\t\t\'statusSummary\': ' + statusSummary + '\n')
	feedCheck.write('\t\t\t\t\'lastReceived\': ' + lastReceived + '\n')
	feedCheck.write('\t\t\t\t\'lastSuccess\': ' + lastSuccess + '\n')
	feedCheck.write('\t\t\t\t\'runLink\': ' + runLink + '\n')
	feedCheck.write('\t\t\t }' + '\n')
	l += 1

feedCheck.close()

