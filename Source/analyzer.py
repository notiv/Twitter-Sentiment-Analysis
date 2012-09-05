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


class Analyzer:
	"""
	Analyzer implements a sentiment scoring algorithm based on words found in tweets and a comparison to an opinion lexicon (http://www.cs.uic.edu/~liub/FBS/opinion-lexicon-English.rar)
	"""
	
	def __init__( self ):
		"""
		Constructor
		"""
		
		self.score = 0.0
		self.negated = False # In case of sarcasm ("#not")

		# Open and read files with positive and negative words
		file_positive_words = os.path.join( sys.path[0], "Files", "positive-words.txt")
		file_negative_words = os.path.join( sys.path[0], "Files", "negative-words.txt")
	
		f = open( file_positive_words )
		self.pos_words = [ x.rstrip('\n') for x in f.readlines() ]
		f.close()
		
		f = open( file_negative_words )
		self.neg_words = [ x.rstrip('\n') for x in f.readlines() ]
		f.close()
		
		# Add some (missing) industry specific words 
		self.pos_words.extend( ['upgrade', '#ff'] )
		self.neg_words.extend( ['wait', 'waiting', 'wtf', 'epicfail', 'mechanical', 'missed', 'cancel'] )
		
	
	
	def score_text( self, text ):
		"""
		Assign a score to a piece of text based on the number of occurencies of words contained 
		in the opinion lexicon (positive/negative)
		"""
		
		self.score = 0.0
		self.negated = False
		
		# Detect "#not" sarcasm and then remove it 
		regex = re.compile( r"#not\b" )
		if regex.search(text):
			self.negated = True
			text = re.sub( r"#not\b", "", text)

		# Remove punctuation
#		text = text.translate( string.maketrans( "", "" ) , string.punctuation ) # Issue with unicode
		regex = re.compile('[%s]' % re.escape(string.punctuation))
		text = regex.sub('', text)
		
		# Remove digits
		text = re.sub( r"\b\d+\b", "", text )
		# Strip whitespace and convert to lower case
		text = text.strip().lower()
		
		# Split into words
		word_list = text.split()
		
		# Control whether a word is contained in the positive/negative list and score accordingly
		for k in word_list:
			if any( k == s for s in self.pos_words):
				self.score = self.score +1
			elif any( k == s for s in self.neg_words):
				self.score = self.score -1

		# In case of sarcasme invert score
		if self.negated:
			self.score = -self.score
		
		return [ self.score, len(word_list) ]
	