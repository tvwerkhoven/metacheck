#!/usr/bin/env python2.7
# encoding: utf-8
"""
metacheck.py

Check texts for structural integrity.
"""

##  @file metacheck.py
# @author Tim van Werkhoven (t.i.m.vanwerkhoven@xs4all.nl)
# 
# Created by Tim van Werkhoven.
# Copyright (c) 2011 Tim van Werkhoven (t.i.m.vanwerkhoven@xs4all.nl)
# 
# This file is licensed under the Creative Commons Attribution-Share Alike
# license versions 3.0 or higher, see
# http://creativecommons.org/licenses/by-sa/3.0/

# Libraries
import sys
import liblog as log
import re
import string
import operator
import argparse

# Settings
mindist = 10 # Minimum distance between two words
log.VERBOSITY = 7


def show_help(err=""):
	log.prNot(log.NOTICE, "syntax: %s <file>" % (sys.argv[0]))
	if (len(err)):
		log.prNot(log.ERR, err)
		sys.exit(-1)

# Sanitize text for easier processing
#############################################################################
def sanitize(text):
	# Only lowercase
	_text = text.lower()
	# Remove punctuation
	# @todo Why does this fail for utf-8 text?
	#_text = re.compile('[^\w\s]', flags=re.UNICODE).sub('', _text)
	_text = re.compile('[\\\(\)!?_\.,:;]', flags=re.UNICODE).sub(' ', _text)
	_text = re.sub(r"\s+", " ", _text) # normalize space
	return _text


# Make histogram of all words.
#############################################################################
def mk_word_histo(text, cutoff=2):
	log.prNot(log.INFO, "mk_word_histo(text)")
	
	_text = sanitize(text)
	
	hist = {}
	for word in re.compile('\s').split(_text):
		if hist.has_key(word):
			hist[word] += 1
		else:
			hist[word] = 1
	
	# Convert to list of tuples, filter out
	hist_filt = filter(lambda x: x[1]>cutoff, hist.iteritems())
	
	# Sort list
	hist_filtsort = sorted(hist_filt, key=operator.itemgetter(1))
	
	print_word_histo(hist_filtsort)
	log.prNot(log.INFO, "mk_word_histo(text) done")
	return hist_filtsort


def print_word_histo(hist):
	for (k, v) in hist:
		print k, v


# Find words close together
#############################################################################
def find_close(text, close=10, minlen=4):
	log.prNot(log.INFO, "find_close(text)")
	
	_text = sanitize(text)
	prev = ['?']*close
	
	outlist = []
	outcount = 0
	
	for word in re.compile('\s').split(_text):
		if (len(word) >= minlen and word in prev):
			dist = prev[::-1].index(word)
			outlist.append([outcount, dist, word, ' '.join(prev)])
			outcount += 1
		
		prev.append(word)
		prev.pop(0)
	
	print_close_words(outlist)
	return outlist

def print_close_words(list):
	for (c, d, word, contxt) in list:
		log.prNot(log.WARNING,  "%d %d %s (%s)" % (c, d, word, contxt))

# Find similar word groups together
#############################################################################
def find_similar(text, groupsize=5, bysentence=False):
	log.prNot(log.INFO, "find_similar(text)")
	
	if (bysentence): 
		groups = re.compile('[\.?!] ').split(text)
		_text = text
	else:
		groups = []
		words = re.compile('\s').split(_text)
		for i in range(0, len(words), groupsize):
			groups.append(' '.join(words[i:i+groupsize]))
	
	simillist = []
	
	for group in groups:
		#print group
		c = _text.count(group)
		if (c > 1):
			simillist.append([c, group])
	
	print_simil(simillist)
	return simillist

def print_simil(list):
	for sim in list:
		log.prNot(log.WARNING, "%d %s" % (sim[0], sim[1]))

# Main routine
def main(*argv):
	# Helper string for this function
	parser = argparse.ArgumentParser(\
		description='Analyze text for inconsistencies, such as words close together, or repeating groups of words.')
	
	# Add positional argument (filepath)
	parser.add_argument('file', action='store', metavar='filename',\
		type=str, help='file to analyze')
	
	# Add optional arguments
	parser.add_argument('-c', '--cutoff', action='store', metavar='N',\
		type=int, help='cutoff value for histogram counting', default=2, dest='cutoff')
	
	parser.add_argument('-d', '--mindist', action='store', metavar='L',\
		type=int, help='mininum distance between words', default=10, dest='mindist')
	
	parser.add_argument('-l', '--minlen', action='store', metavar='L',\
		type=int, help='mininum wordlength to parse', default=4, dest='minlen')
	
	parser.add_argument('-g', '--groupsize', action='store', metavar='S',\
		type=int, help='number of words per group to compare for recurrence', default=6, dest='grpsize')
	
	parser.add_argument('-s', '--grpsentence', action='store_true', \
		help='group words by sentence (override groupsize)', default=False, dest='grpsent')
	
	args = parser.parse_args()
	
	log.prNot(log.NOTICE, "%s: analyzing file %s" % (argv[0], args.file))
	
	fd = open(args.file)
	text = fd.read()
	fd.close()
	
	# Histogram all words
	histwords = mk_word_histo(text, cutoff=args.cutoff)
	
	# Find words close together
	closewords = find_close(text, close=args.mindist, minlen=args.minlen)
	
	# Find similar sets of words
	similgroups = find_similar(text, groupsize=args.grpsize, bysentence=args.grpsent)
	



# Check if we are run from commandline
if __name__ == '__main__':
	sys.exit(main(*sys.argv))
