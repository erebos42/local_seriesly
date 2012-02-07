#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from optparse import OptionParser

# remove html files and fetched data
#def remove():
#	pass

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
#	parser.add_option("-r", "--remove", action="store_true", dest="clean", help="remove html files and fetched data")
	(options, args) = parser.parse_args()

	if options.clean:
		remove()
	if options.fetch:
		fetch()
	if options.generate:
		generate()

if __name__ == '__main__':
    main()
