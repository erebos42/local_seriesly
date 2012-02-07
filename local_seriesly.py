#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import os
import sys
import string
from optparse import OptionParser

# remove html files and fetched data
def remove():
	print "Removing show data..."
	currentdirpath = os.path.dirname(os.path.realpath(sys.argv[0]))
	try:
		os.remove(currentdirpath + "/data/seriesdb.json")
	except OSError:
		pass
	# TODO: remove all html files. config must be parsed so the right files are deleted
	profiles = []
	fdcfg = open(currentdirpath + '/show_id.cfg', 'r')
	for line in fdcfg:
		line = string.replace(line, " ", "")
		if (string.find(line, "#") == -1):
			line = line.strip("\n")
			name = string.split(line,"=")[0]
			profiles.append(name)
	print "Removing profile data..."
	for profile in profiles:
		try:
			os.remove(currentdirpath + "/data/" + profile + ".html")
		except OSError:
			pass
	print "Removing compiled python scripts..."
	try:
		os.remove(currentdirpath + "/fetchdata.pyc")
	except OSError:
		pass
	try:
		os.remove(currentdirpath + "/generatehtml.pyc")
	except OSError:
		pass

# fetch data
def fetch():
	import fetchdata
	fetchdata.fetchdata()
	pass

# generate html files
def generate():
	import generatehtml
	generatehtml.generatehtml()
	pass

def main():
	parser = OptionParser()
	parser.add_option("-f", "--fetch", action="store_true", dest="fetch", help="fetch data")
	parser.add_option("-g", "--generate", action="store_true", dest="generate", help="generate the html documents")
#	parser.add_option("-c", "--configfile", dest="config_file", help="path to config file with the profiles and show ids", metavar="FILE")
	parser.add_option("-r", "--remove", action="store_true", dest="clean", help="remove html files and fetched data")
	(options, args) = parser.parse_args()

	if options.clean:
		remove()
	if options.fetch:
		fetch()
	if options.generate:
		generate()

if __name__ == '__main__':
    main()
