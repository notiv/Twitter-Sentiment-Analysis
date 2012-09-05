#!/usr/bin/python
# encoding: utf-8

"""
twitter_scraper.py

Viton Vitanis 
August 2012
"""

import sys
import os
import re
import string
import operator
import time
import json
import twitter
import pymongo

#from dateutil import parser as dateparser

class TwitterScraper:
	"""
	TwitterScraper searches Twitter based on the parameters given to it. The returned tweets are saved into a MongoDB database.
	"""	
	
	def __init__( self ):
		"""
		Constructor
		"""
		
		self.search_results = {}
		self.dbconnection = pymongo.Connection("localhost", 27017)
		self.db = self.dbconnection.tweet
		self.db.tweets.ensure_index("id_str", pymongo.DESCENDING, unique = True, dropDups = True )
		self.tweet_count = 0
		english_file = os.path.join( sys.path[0], "Files", "Nielsen2010_english.csv")
		self.analyzeEnglish = dict(map(lambda (w,e): (w, int(e)), [ line.strip().lower().split('\t') for line in open( english_file ) ] ))
	
	def __del__( self ):
		""" 
			Destructor 
		"""
		
		self.dbconnection.disconnect()	
		
	def clear_collection( self ):
		"""
			Clear collection
		"""
		self.db.tweets.remove()
		if self.retrieve_tweets():
			print "Error clearing collection."
		else:
			print "Collection clear."
	
	def twitter_search( self, search_terms = [], username = [], pages = 1, results_per_page = 100, eng_only = True ):
		"""
			twitter_search( self, search_terms[], pages = 1, results_per_page = 100 )
			Input: search_terms: A list of terms to be searched for
			Input: pages: A number defining how many pages of tweets should be searched for
			Input: results_per_page: A number defining how many tweet results should be on each page.
			Searches twitter for the terms listed and saves the data returned in a MongoDB database.
		"""	 
		
		if search_terms == []: return ''
		
		self.pages = pages
		self.results_per_page = results_per_page
		
		twitter_api = twitter.Twitter(domain="api.twitter.com", api_version='1')
		twitter_search = twitter.Twitter(domain="search.twitter.com")
		
		# Loop through all search terms
		for term in search_terms:
			search_results = []
			self.tweet_count = 0
			for page in range( 1, pages+1 ):
				search_results.append(twitter_search.search( q=term, rpp=results_per_page, page = page, result_type = "recent"))
		
			# For each result
			for result in search_results:
				# For each tweet
				for tweet in result['results']:
					# Skip tweets that are not in English
					if eng_only and (not self.__language_is_eng( tweet['text'] ) ):
						continue
					
					# If tweet is sent by username ignore
					if ( not username == [] ) and tweet['from_user'] in username:
						continue
					
#					try:
#	'Wed, 05 Sep 2012 15:51:37 +0000' does not match format '%a, %b %d %H:%M:%S +0000 %Y %Z'
#	ts = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(tweet['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
#'2012-09-05 15:51:37' does not match format '%a, %d %b %Y %H:%M:%S +0000'
#					tweet['created_at'] = time.strftime( '%Y-%m-%d %H:%M:%S', time.strptime( tweet['created_at'], '%a, %d %b %Y %H:%M:%S +0000' )	)
					print tweet

					tweet['created_at'] = time.strftime( '%Y-%m-%d %H:%M:%S', time.strptime( tweet['created_at'], '%a, %d %b %Y %H:%M:%S +0000' )	)

#					except:
#						print "Error: ", tweet['created_at'], ' ', type( tweet['created_at'])
					
					self.tweet_count += 1
					self.db.tweets.insert(tweet)
			
			print "Tweets for term", term, ": ", self.tweet_count 

	def twitter_search_old_tweets( self, search_terms = [], username = [], pages = 1, results_per_page=100, eng_only = True ):
		"""
			twitter_search( self, search_terms[], pages = 1, results_per_page = 100 )
			Input: search_terms: A list of terms to be searched for
			Input: pages: A number defining how many pages of tweets should be searched for
			Input: results_per_page: A number defining how many tweet results should be on each page.
			Searches twitter for the terms listed and saves the data returned in a MongoDB database.
		"""	 
		
		if search_terms == []: return ''
		
		# Retrieve all tweets
		stored_tweets = self.retrieve_tweets( number_of_tweets = -1 )

		# If there are no tweets in the database
		if not stored_tweets:
			print "No stored tweets"
			self.twitter_search(search_terms = search_terms, username = username, pages = pages, results_per_page = results_per_page, eng_only = eng_only)
		else:
			# Sort tweets based on the field "created at"
			# NOTE: This is a sorting of a list of dictionaries by values of the dict
			stored_tweets = sorted(stored_tweets, key=operator.itemgetter('created_at'))
			
			tweet_max_id = stored_tweets[0]['id']
			
			self.pages = pages
			self.results_per_page = results_per_page
					
			twitter_api = twitter.Twitter(domain="api.twitter.com", api_version='1')
			twitter_search = twitter.Twitter(domain="search.twitter.com")
		
			# Loop through all search terms
			for term in search_terms:
				search_results = []
				self.tweet_count = 0
				for page in range( 1, pages+1 ):
					search_results.append(twitter_search.search( q=term, rpp=results_per_page, page = page, max_id = tweet_max_id ))
			
				# For each result
				for result in search_results:
					# For each tweet
					for tweet in result['results']:
						# Skip tweets that are not in English
						if eng_only and (not self.__language_is_eng( tweet['text'] ) ):
							continue
						
						# If tweet is sent by username ignore
						if ( not username == [] ) and tweet['from_user'] in username:
							continue
						
						tweet['created_at'] = dateparser.parse(tweet['created_at'])
						
						self.tweet_count += 1
						print tweet
						self.db.tweets.insert(tweet)
				
				print "Tweets for term", term, ": ", self.tweet_count 
		
	def retrieve_tweets( self, number_of_tweets = -1 ):
		"""
		retrieve_tweets( self, number_of_tweets ):
		Input: number_of_tweets. The number of tweets to be returned.
		Retrieves tweets from the database.
		"""
		returnList = []
		
		if number_of_tweets > 0:
			returnList = list(self.db.tweets.find().limit(number_of_tweets))
		else:
			returnList = list(self.db.tweets.find())
			
		print len(returnList), " tweets returned.\n"	
		return returnList
		
	def web_output( self, stored_tweets ):
		"""
		web_output( self, stored_tweets )
		Input: stored_tweets. The tweets in the database
		Creates simple html file with tweets
		NOTE: Check http://stackoverflow.com/questions/799479/python-html-output-first-attempt-several-questions-code-included
		"""
		
		results_html = ""
		
		# Loop over each index of data, storing the item in "result"
		for tw in stored_tweets:
			# Append to string
			results_html += "    <p style='font-size:90%%'>%(time)s \t  %(user)s \t %(twtext)s</p>\n" % {'time': tw['created_at'].encode('utf-8'), 'user': tw['from_user'].encode('utf-8'), 'twtext': tw['text'].encode('utf-8')}
		
		html = """<html>
			<head>
		    <title>python newb's twitter search</title>
		    </head>
		    <body>
		        <h1 style='font-size:150%%'>Twitter Search Results</h1>
		    %(results_html)s
		    </body>
		    </html>
		""" % {'results_html': results_html}
		
		return html
	
	def __language_is_eng( self, tweet_text ):
		"""
			__language_is_eng( self, tweet ):
			Input: tweet_text. A string containing a tweet to check.
			Determines whether the tweet is in English or not. This function 
			was found in https://github.com/ellioman/Twitter-Sentiment-Analysis.
			Return: True if English, False if not English
		"""

		lang = sum(map(lambda w: self.analyzeEnglish.get(w, 0), \
			re.sub(r'[^\w]', ' ', string.lower(tweet_text)).split()))

		if lang >= 1.0: return True
		else: return False
			