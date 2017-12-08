from datetime import datetime, timedelta
from dateutil import parser
from pytz import timezone
import requests, pytz, pdb, os, os.path, sys, re, struct, copy, time, shutil

def write_feed_info(feedList, feedRuns, feedCheck, listType):
	if len(feedList) >= 1:
		i = 0
		while i < len(feedList):
			runId = str(feedList[i])
			siteName = feedRuns[feedList[i]]['siteName']
			feedProfile = feedRuns[feedList[i]]['feedProfile']
			feedName = feedRuns[feedList[i]]['feedName']
			statusCode = feedRuns[feedList[i]]['statusCode']
			statusSummary = feedRuns[feedList[i]]['statusSummary']
			lastReceived = feedRuns[feedList[i]]['lastReceived']
			if feedRuns[feedList[i]]['lastSuccess'] == None:
				lastSuccess = 'NO PRIOR SUCESS.'
			else:
				lastSuccess = feedRuns[feedList[i]]['lastSuccess']
			runLink = feedRuns[feedList[i]]['runLink']

			if listType == 'error':
				feedCheck.write('<tr class="bad">\n')
			if listType == 'postponed':
				feedCheck.write('<tr class="bad">\n')
			if listType == 'late':
				feedCheck.write('<tr class="delayed">\n')
			feedCheck.write('<td><center><a href="' +runLink + '">' + runId + '</center></td>\n')
			feedCheck.write('<td><center><strong>' + siteName + '</strong><br>Using Feed Profile: ' + feedProfile + '</center></td>\n')
			feedCheck.write('<td><center>' + lastReceived + '</center></td>\n')
			feedCheck.write('<td><center>' + statusCode + '</center></td>\n')
			feedCheck.write('</tr>\n')
			i += 1