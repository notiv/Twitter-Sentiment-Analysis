#!/usr/bin/python

import datetime
import operator
from twitter_scraper import *
from analyzer import *
from html_creator import *

# Settings
search_terms = ["swissair", "swiss_us", "swiss_airlines"]
usernames = ["SwissAirLines", "swiss_us"]
pages = 1
results_per_page = 5
time_interval_h = 6 # Group tweets in intervals of 12 hours

# Initialize class for scraping tweets
scraper = TwitterScraper()

scraper.clear_collection()

scraper.twitter_search( search_terms = search_terms, username = usernames, pages = pages, results_per_page = results_per_page )
#scraper.twitter_search_old_tweets( search_terms = search_terms, username = usernames, pages = pages, results_per_page = results_per_page )

stored_tweets = scraper.retrieve_tweets( number_of_tweets = -1 )
stored_tweets = sorted(stored_tweets, key=operator.itemgetter('created_at'))
html = scraper.web_output( stored_tweets )

f = open("outw.html", "w")
f.write( html )
f.close()

#print stored_tweets

# Sort tweets based on the field "created at"
## NOTE: This is a sorting of a list of dictionaries by values of the dict
#stored_tweets = sorted(stored_tweets, key=operator.itemgetter('created_at'))
#
## Initialize class for analyzing tweets
#analyzer = Analyzer()
#
## Bins to store number of tweets and scores that correspond to a specific time interval
#counter = 0
#no_of_tweets_bin = [0]
#score_bin = [0.0]
#
#first_day = datetime.datetime.combine(stored_tweets[0]['created_at'].date(), datetime.time(0,0,))
#
#for tw in stored_tweets:
#	# Check if the next bin is to be processed
#	
##	print first_day + counter*datetime.timedelta(hours=time_interval_h), tw['created_at'], first_day + (counter+1)*datetime.timedelta(hours=time_interval_h)
#	
#	while not (first_day + counter*datetime.timedelta(hours=time_interval_h) <= tw['created_at'] < first_day + (counter+1)*datetime.timedelta(hours=time_interval_h)):
#		counter = counter+1
#		no_of_tweets_bin.append(0)
#		score_bin.append(0.0)
#	
#	# Analyze tweet
#	[ tscore, no_of_words ] = analyzer.score_text( tw['text'] )
#	# Update bins
#	no_of_tweets_bin[counter] = no_of_tweets_bin[counter]+1
#	score_bin[counter] = score_bin[counter] + tscore
#	
#
#for c in range(len(no_of_tweets_bin)):
#	print no_of_tweets_bin[c], '->', score_bin[c]

