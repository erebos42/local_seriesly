# -*- coding: utf-8 -*-

# ToDo:
# - "Coming Up Soon" date calc fixen
# - sort data in html
# - add support for html datetime tags
# 
#
#
#


import urllib
import xml.dom.minidom as dom
import string
from string import Template
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import json
import os,sys

# data structure:
# - data {id, series}
# -- series {name, episodes}
# --- episodes {episode}
# ---- episode {epnum, title}

def getSeriesInfo(url):
	series = []

	done = 0

	while(done == 0):
		try:
			dict = dom.parse(urllib.urlopen(url))
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

def getEpisodesInfo(dict):
	episodes = []
	for node in dict.getElementsByTagName("episode"):
		episodes.append(getEpisodeInfo(node))
	return episodes

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

#	series_ids = {"11215", "8511", "18164", "15383", "19267", "15614", "7926", "3332", "3628", "24493", "21704", "3908", "3918", "8322", "6190", "5266", "12662", "6454", "20601", "25056", "7884", "6554", "18411", "25050"}
#	series_ids = {"8322", "15614", "11215", "8511", "18164", "15383", "19267"}
#	series_ids = {"5266"}

	# TODO: read config file

	fdcfg = open(currentdirpath + '/show_id.cfg', 'r')
	for line in fdcfg:
		temp = string.split(line, "=")[1]
		temp = string.split(temp, ",")
		for e in temp:
			series_ids.append(string.strip(e,"\n"))
		
	series_ids = list(set(series_ids))
	series_ids.sort()

	data = []

	for id in series_ids:
		print "Fetch Data for " + id
		data.append({
			id : getSeriesInfo("http://services.tvrage.com/feeds/full_show_info.php?sid=" + id)
		})


	json.dump(data, open(currentdirpath + '/data/seriesdb.json', 'wb'))

	print "Done!"

currentdirpath = os.path.dirname(os.path.realpath(sys.argv[0]))

if __name__ == '__main__':
    main()
