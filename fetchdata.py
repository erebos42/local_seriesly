#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

# ToDo:
# - add support for html datetime tags
# - optimize data structure
#
#
#


import urllib2
import xml.dom.minidom as dom
import string
from string import Template
from datetime import datetime, timedelta
from pytz import timezone
import json
import os
import sys

# data structure (more or less):
# - data {id, series}
# -- series {name, episodes}
# --- episodes {episode}
# ---- episode {epnum, title}

# This method fetches the data for a specific show (url)
def getSeriesInfo(url):
	series = []

	done = 0

	while(done == 0):
		try:
			dict = dom.parse(urllib2.urlopen(url))
			done = 1
		except IOError:
			print "Connection Timedout - retry"
			pass		

	seriesname = dict.getElementsByTagName('name')[0].toxml().replace("<name>", "").replace("</name>", "")
	network = dict.getElementsByTagName('network')[0].toxml().replace("<network country=US>", "").replace("</network>", "")
	airtime = dict.getElementsByTagName('airtime')[0].toxml().replace("<airtime>", "").replace("</airtime>", "")
	series.append({
		"name" : seriesname,
		"network" : network,
		"airtime" : airtime,
		"episodes" : getEpisodesInfo(dict)
	})

	return series

# parse dom dict for episodes
def getEpisodesInfo(dict):
	episodes = []
	for node in dict.getElementsByTagName("episode"):
		episodes.append(getEpisodeInfo(node))
	return episodes

# parse dom node for episode info
def getEpisodeInfo(node):
	children = node.childNodes
	episode = []
	epnum = 0
	title = ""
	seasonnum = 0
	airdate = ""

	for child in children:
		if (child.toxml().count("seasonnum") == 2):
			epnum = child.toxml()
		if (child.toxml().count("title") == 2):
			title = child.toxml()
		if (child.toxml().count("airdate") == 2):
			airdate = child.toxml()

	seasonnumtemp = ""
	try:
		seasonnumtemp = node.parentNode.attributes["no"].value
	except KeyError:
		pass

	episode.append({
		"epnum" : str(epnum).replace("<seasonnum>", "").replace("</seasonnum>", ""),
		"title" : str(title.encode("utf-8")).replace("<title>", "").replace("</title>", ""),
		"seasonnum" : seasonnumtemp,
		"airdate" : str(airdate).replace("<airdate>", "").replace("</airdate>", "")
	})
	return episode

def main():
	print "Start!"

	# http://services.tvrage.com/feeds/full_show_info.php?sid=8322
	series_ids = []

	# parse show_id config file
	fdcfg = open(currentdirpath + '/show_id.cfg', 'r')
	for line in fdcfg:
		line = string.replace(line, " ", "")
		if (string.find(line, "#") == -1):
			temp = string.split(line, "=")[1]
			temp = string.split(temp, ",")
			for e in temp:
				series_ids.append(string.strip(e,"\n"))
	# cast the series_ids to a set and back, so every show id appears only once
	series_ids = list(set(series_ids))
	series_ids.sort()

	data = []

	# fetch data for every show and store in data dict
	# TODO: maybe this can be multithreaded to improve the network performance
	for id in series_ids:
		print "Fetch Data for " + id
		data.append({
			id : getSeriesInfo("http://services.tvrage.com/feeds/full_show_info.php?sid=" + id)
		})

	# dump the data to the json database, so it can be used by the other script later
	json.dump(data, open(currentdirpath + '/data/seriesdb.json', 'wb'))

	print "Done!"


# get the script path, so the config- and json-file can be found
currentdirpath = os.path.dirname(os.path.realpath(sys.argv[0]))

if __name__ == '__main__':
    main()
