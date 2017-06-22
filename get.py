import webbrowser
import time
import os
import shutil
import copy
import pandas as pd
import re
import csv
import numpy as np
from pandas import DataFrame
import pandas as pd
import sys
import json
import urllib
import datetime
from datetime import datetime, timedelta
import requests
import time
import calendar



""" Start Google Trends Scraper"""
def googleT_scraper(start_date, end_date, Input):  #returns dictionary
	#input example 
	# start_date="2016-01-01"
	# end_date="2017-02-18"
	# Input=['bitcoin']

	def get_buckets(start_date, end_date):
	    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
	    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

	    bucket_limits = [start_date_dt]
	    left_limit = start_date_dt
	    while left_limit <= end_date_dt:
	        new_limit = left_limit + timedelta(days=181)
	        if new_limit < end_date_dt:
	            bucket_limits.append(new_limit)
	        left_limit = new_limit
	    bucket_limits.append(end_date_dt)
	    return bucket_limits

	def get_data(bucket_start_date,bucket_end_date, keyword):
	    bucket_start_date_printed = datetime.strftime(bucket_start_date, '%Y-%m-%d')
	    bucket_end_date_printed = datetime.strftime(bucket_end_date, '%Y-%m-%d')
	    time_formatted = bucket_start_date_printed + '+' + bucket_end_date_printed

	    req = {"comparisonItem":[{"keyword":keyword, "geo":geo, "time": time_formatted}], "category":category,"property":""}
	    hl = "en-GB"
	    tz = "-120"

	    explore_URL = 'https://trends.google.com/trends/api/explore?hl={0}&tz={1}&req={2}'.format(hl,tz,json.dumps(req).replace(' ','').replace('+',' '))
	    return requests.get(explore_URL).text

	def get_token(response_text):
	    try:
	        return response_text.split('token":"')[1].split('","')[0]
	    except:
	        return None

	def get_csv_request(response_text):
	    try:
	        return response_text.split('"widgets":')[1].split(',"lineAnno')[0].split('"request":')[1]       
	    except:
	        return None

	def get_csv(response_text):
	    request = get_csv_request(response_text)
	    token = get_token(response_text)

	    csv = requests.get('https://www.google.com/trends/api/widgetdata/multiline/csv?req={0}&token={1}&tz=-120'.format(request,token))
	    return csv.text.encode('utf8')

	def parse_csv(csv_contents):
	    lines = csv_contents.split('\n')
	    df = pd.DataFrame(columns = ['date','value'])
	    dates = []
	    values = []
	    # Delete top 3 lines
	    for line in lines[3:-1]:
	        try:
	            dates.append(line.split(',')[0].replace(' ',''))
	            values.append(line.split(',')[1].replace(' ',''))
	        except:
	            pass
	    df['date'] = dates
	    df['value'] = values
	    return df   

	def get_daily_frames(start_date, end_date, keyword):

	    bucket_list = get_buckets(start_date, end_date)
	    frames = []
	    for i in range(0,len(bucket_list) - 1):
	        resp_text = get_data(bucket_list[i], bucket_list[i+1], keyword)
	        frames.append(parse_csv(get_csv(resp_text)))

	    return frames

	def get_weekly_frame(start_date, end_date, keyword):

	    if datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d') - timedelta(days=180):
	        print 'No need to stitch; your time interval is short enough. '
	        return None
	    else:
	        resp_text = get_data(datetime.strptime(start_date, '%Y-%m-%d'), datetime.strptime(end_date, '%Y-%m-%d'), keyword)
	        return parse_csv(get_csv(resp_text))

	def stitch_frames(daily_frames, weekly_frame):

	    daily_frame = pd.concat(daily_frames, ignore_index = True)

	    daily_frame.columns = ['Date', 'Daily_Volume']
	    pd.to_datetime(daily_frame['Date'])
	    
	    weekly_frame.columns = ['Week_Start_Date', 'Weekly_Volume']
	    daily_frame.index = daily_frame['Date']
	    weekly_frame.index = weekly_frame['Week_Start_Date']

	    bins = []

	    for i in range(0,len(weekly_frame)):
	        bins.append(pd.date_range(weekly_frame['Week_Start_Date'][i],periods=7,freq='d'))

	    final_data = {}

	    for i in range(0,len(bins)):
	        week_start_date = datetime.strftime(bins[i][0],'%Y-%m-%d')
	        for j in range(0,len(bins[i])):
	            this_date = datetime.strftime(bins[i][j],'%Y-%m-%d')
	            try:
	                this_val = int(float(weekly_frame['Weekly_Volume'][week_start_date])*float(daily_frame['Daily_Volume'][this_date])/float(daily_frame['Daily_Volume'][week_start_date]))
	                final_data[this_date] = this_val
	            except:
	                pass
		return final_data
	    # final_data_frame = DataFrame.from_dict(final_data,orient='index').sort()
	    # final_data_frame[0] = np.round(final_data_frame[0]/final_data_frame[0].max()*100,2)

	    # final_data_frame.columns=['Volume']
	    # final_data_frame.index.names = ['Date']

	    # """output to csv"""
	    # final_data_frame.to_csv('{0}.csv'.format(keywords.replace('+','')), sep=',')

	if __name__ == '__main__':

	    # start_date = sys.argv[1]
	    # end_date = sys.argv[2]
	    geo = ''
	    category = 22
	    keywords = '+'.join(Input)
	    print keywords

	    daily_frames = get_daily_frames(start_date, end_date, keywords)
	    weekly_frame = get_weekly_frame(start_date, end_date, keywords)
	    final_dictionary=stitch_frames(daily_frames, weekly_frame)

	return final_dictionary

"""End Google Trends Scraper"""

"""Start SQL push command"""
def push_sql(command): 
	# communicating with the sql
	commandArray=command.split(" ");
	output=""
	for i in commandArray:
		output=output+i+"+";
	output=output[0:len(output)-1]
	url="http://kevin.zapto.org:7331/sqlCommand?sqlCommand="+output+"&user=judson&password=iscrazy";
	response=urllib2.urlopen(url).read();
	response=json.loads(response);
	if(response["error"]==True):
			print(response);
			raise Exception("What the fuck")
	return; #specified to Kevin's website


""" Start Git Email Scraper"""
def gitE_scraper(cryptos ): 
		#cryptos in dictionary format 
	def month_string_to_number(string):
	    m = {
	        'jan': 1,
	        'feb': 2,
	        'mar': 3,
	        'apr':4,
	         'may':5,
	         'jun':6,
	         'jul':7,
	         'aug':8,
	         'sep':9,
	         'oct':10,
	         'nov':11,
	         'dec':12
	        }
	    s = string.strip()[:3].lower()

	    try:
	        out = m[s]
	        return out
	    except:
	        raise ValueError('Not a month')
	def offset(tz):
		# +0100 is one hour ahead of UTC
		hour=tz[2]
		hour=int(hour)
		sign=tz[0]

		if sign == "+":
			hour = -1*hour
		return hour

	def removeDatabase():
		push_sql("drop database if exists "+dbName+";");

	def convertTime(date):
		try:
			time=date.split(' ')
			month=time[1]
			month=int(month_string_to_number(month))
			day=int(time[2])

			clock=time[3]

			clock=clock.split(':')
			hour=int(clock[0])
			minute=int(clock[1])
			second=int(clock[2])

			year=int(time[4])
			tz=(time[5])
			hour=hour +offset(tz)

			if hour > 24:
				hour -= 24
			if hour < 0:
				hour = 24+hour
			if hour == 24:
				hour=0

			date=datetime.datetime(year,month,day,hour,minute,second,0).strftime("%s")

			date=float(date)
			return date;
		except:
			return 0 # sometimes date is blank 


	coin=[]
	commits=[]

	# while(True):
	for e in cryptos:
		#try:
		folder=e["url"].split("/")[len(e["url"].split("/"))-1];
		coinName=e["url"].split("/")[len(e["url"].split("/"))-2];
		#push_sql("create table if not exists "+dbName+"."+coinName+" (timestamp decimal(16.5) NOT NULL Primary key);");
		cmdStr="git clone "+e["url"]+".git;";
		cmdStr=cmdStr+"cd "+folder+";";
		cmdStr=cmdStr+"git log --all --format='%cd' | sort -u;";
		cmdStr=cmdStr+"cd ../; rm -rf "+folder+";"
		output = os.popen(cmdStr).read();
		output=output.split('\n');

		for o in range(0,len(output)):	
			output[o]=convertTime(output[o]);

		output=np.array(output)
		output.sort()	
		commits.append(output)
		coin.append(coinName)
		
	coin_tickers=zip(coin,commits)

	final_dictionary={}
	for coin,commits in coin_tickers:
		final_dictionary[coin]=commits
	return final_dictionary
"End Git Email Scraper"






