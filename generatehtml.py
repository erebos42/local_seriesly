# -*- coding: utf-8 -*-

# ToDo:
# - sort data in html
# - add support for html datetime tags
# 
#
#
#


import urllib
import xml.dom.minidom as dom
import copy
import string
from string import Template
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import json
import os, sys

# data structure:
# - data {id, series}
# -- series {name, episodes}
# --- episodes {episode}
# ---- episode {epnum, title}

def filterData(data):
	last = []
	coming = []
	recently = []

	for i in range(len(data)):
		sid = data.keys()[i]
		name = data[sid][0]["name"]
		network = data[sid][0]["network"]
		airtime = data[sid][0]["airtime"]
		episodes = data[sid][0]["episodes"]
		for temp in episodes:
			tempepisode = temp.pop()
			tempepisode["name"] = name
			tempepisode["network"] = network
			# todo: sort episode by date and stuff!!!

			airdate = tempepisode["airdate"]

			tempairdate = airdate.split("-")
			year = tempairdate[0]
			month = tempairdate[1]
			day = tempairdate[2]
			hour = airtime.split(":")[0]
			minute = airtime.split(":")[1]


			if (int(year) == 0):
				year = 1
			if ((int(month) < 1) or (int(month) > 12)):
				month = 1
			if ((int(day) < 1) or (int(month) > 31)):
				day = 1

			airdatetime = datetime(int(year), int(month), int(day), int(hour), int(minute), 0, 0)

			# todo timezone adjustment
			airdatetime = airdatetime + timedelta(hours=6)

			now = datetime.now()
			temp = now - airdatetime

			if (temp < timedelta(days=0)):
				tempepisode["airdate"] = temp
				coming.append(tempepisode)
			elif ((temp >= timedelta(days=0)) and (temp < timedelta(days=1))):
				tempepisode["airdate"] = temp
				recently.append(tempepisode)
			elif ((temp >= timedelta(days=1)) and (temp < timedelta(days=7))):
				tempepisode["airdate"] = temp
				last.append(tempepisode)

	return {"last" : last, "coming" : coming, "recently" : recently}

def outputDataDebug(filteredData):
	last = filteredData["last"]
	coming = filteredData["coming"]
	recently = filteredData["recently"]

	print "=========="
	print "Last:"
	print "-----"
	for i in range(len(last)):
		print last[i]["name"] + " - " + last[i]["seasonnum"] + "x" + last[i]["epnum"] + " - " + last[i]["title"]

	print "=========="
	print "Coming:"
	print "-----"
	for i in range(len(coming)):
		print coming[i]["name"] + " - " + coming[i]["seasonnum"] + "x" + coming[i]["epnum"] + " - " + coming[i]["title"]

	print "=========="
	print "Recently:"
	print "-----"
	for i in range(len(recently)):
		print recently[i]["name"] + " - " + recently[i]["seasonnum"] + "x" + recently[i]["epnum"] + " - " + recently[i]["title"]




def outputData(filteredData, profile):
	recentlyTemplate = Template('\
		<li class=\"vevent episode-item\">\
			<div class=\"clearfix\" style=\"width:100%\">\
				<div class=\"left\">\
					<div class=\"vevent-meta\">\
						<time class=\"dtstart\" datetime=\"2011-11-12T01:00:00\"> $deltatime </time>\
						<time class=\"dtend\" datetime=\"2011-11-12T02:00:00\"></time> <span class=\"location\">on $network</span>, $seasonnum$epnum\
					</div>\
					<span title=\"Season $seasonnum, Episode $epnum\" class=\"summary\">$seriesname: &ldquo;$epname&rdquo;</span>\
				</div>\
			</div>\
		</li>\
	')

	lastsevendays_compingupTemplate = Template('\
		<li class=\"vevent episode-item\">\
			<div class=\"vevent-meta\">\
				<time class=\"dtstart\" datetime=\"2011-11-11T03:00:00\"> $deltatime </time>\
				<time class=\"dtend\" datetime=\"2011-11-11T04:00:00\"></time> <span class=\"location\">on $network</span>, $seasonnum$epnum\
			</div>\
			<span title=\"Season $seasonnum, Episode $epnum\" class=\"summary\">$seriesname: &ldquo;$epname&rdquo;</span>\
		</li>\
	')


	filteredData = sortData(filteredData)

	lastsevendays = ""
	recently = ""
	comingup = ""
	for i in range(len(filteredData["last"])-1,-1,-1):
		lastsevendays += lastsevendays_compingupTemplate.substitute(seasonnum=filteredData["last"][i]["seasonnum"] + "x", epnum=filteredData["last"][i]["epnum"], seriesname=filteredData["last"][i]["name"], epname=filteredData["last"][i]["title"], network=filteredData["last"][i]["network"], deltatime=airdateToString(filteredData["last"][i]["airdate"]))
	for i in range(len(filteredData["coming"])-1,-1,-1):
		comingup += lastsevendays_compingupTemplate.substitute(seasonnum=filteredData["coming"][i]["seasonnum"] + "x", epnum=filteredData["coming"][i]["epnum"], seriesname=filteredData["coming"][i]["name"], epname=filteredData["coming"][i]["title"], network=filteredData["coming"][i]["network"], deltatime=airdateToString(filteredData["coming"][i]["airdate"]))
	for i in range(len(filteredData["recently"])-1,-1,-1):
		recently += recentlyTemplate.substitute(seasonnum=filteredData["recently"][i]["seasonnum"] + "x", epnum=filteredData["recently"][i]["epnum"], seriesname=filteredData["recently"][i]["name"], epname=filteredData["recently"][i]["title"], network=filteredData["recently"][i]["network"], deltatime=airdateToString(filteredData["recently"][i]["airdate"]))

	fdwrite = open(currentdirpath + "/data/" + profile + ".html", "w")
	fdread = open(currentdirpath + "/media/template.html", "r")

	for line in fdread:
		if (line.count("<!-- RECENTLY -->") == 1):
			fdwrite.write(recently.encode("utf-8"))
		elif (line.count("<!-- LAST_SEVEN_DAYS -->") == 1):
			fdwrite.write(lastsevendays.encode("utf-8"))
		elif (line.count("<!-- COMING_UP -->") == 1):
			fdwrite.write(comingup.encode("utf-8"))
		else:
			fdwrite.write(line)





def airdateToString(airdate):

# -2 days, 10:29:04.862377

	ret = ""
	days = 0
	temp = str(airdate).split(" ")
	if ((len(temp) > 1) and ((temp[1] == "days,") or (temp[1] == "day,"))):
		days = int(temp[0])
		temp = temp[2].split(":")
		hours = int(temp[0])
		mins = int(temp[1])
		if (days < 0):
			days = days + 1 
			hours = 23 - hours
			mins = 59 - mins
	else:
		temp = temp[0].split(":")
		hours = int(temp[0])
		mins = int(temp[1])

	if (days == 0):
		ret = str(hours) + " hour(s), " + str(mins) + " min ago "
	elif (days > 0):
		ret = str(days) + " day(s), " + str(hours) + " hour(s) ago "
	elif (days < 0):
		ret = "in " + str(-days) + " day(s), " + str(hours) + " hour(s) "

	return ret




def sortData(filteredData):


	done = 0
	sortedcoming = []
	while (done != 1):
		maxdate = timedelta(hours=0)
		maxindex = -1
		for i in range(len(filteredData["coming"])):
			if (filteredData["coming"][i]["airdate"] < maxdate):
				maxdate = filteredData["coming"][i]["airdate"]
				maxindex = i
		if (maxindex != -1):
			sortedcoming.append(filteredData["coming"].pop(maxindex))
		if (len(filteredData["coming"]) == 0):
			done = 1

	done = 0
	sortedrecently = []
	while (done != 1):
		maxdate = timedelta(hours=0)
		maxindex = -1
		for i in range(len(filteredData["recently"])):
			if (filteredData["recently"][i]["airdate"] > maxdate):
				maxdate = filteredData["recently"][i]["airdate"]
				maxindex = i
		if (maxindex != -1):
			sortedrecently.append(filteredData["recently"].pop(maxindex))
		if (len(filteredData["recently"]) == 0):
			done = 1

	done = 0
	sortedlast = []
	while (done != 1):
		maxdate = timedelta(hours=0)
		maxindex = -1
		for i in range(len(filteredData["last"])):
			if (filteredData["last"][i]["airdate"] > maxdate):
				maxdate = filteredData["last"][i]["airdate"]
				maxindex = i
		if (maxindex != -1):
			sortedlast.append(filteredData["last"].pop(maxindex))
		if (len(filteredData["last"]) == 0):
			done = 1

	return {"last" : sortedlast, "coming" : sortedcoming, "recently" : sortedrecently}
	

def filterprofile(data, ids):
	tempdata = {}
	for i in range(len(data)):
		if (ids.count(data[i].keys()[0]) > 0):
			tempdata.update(data[i])
	return tempdata


def main():
	print "Start!"

	data = json.load(open(currentdirpath + '/data/seriesdb.json', 'rb'))

	# load cfg and store in dict
	profiles = {}
	fdcfg = open(currentdirpath + '/show_id.cfg', 'r')
	for line in fdcfg:
		line = string.replace(line, " ", "")
		if (string.find(line, "#") == -1):
			line = line.strip("\n")
			name = string.split(line,"=")[0]
			ids = string.split(line,"=")[1]
			ids = string.split(ids,",")
			profiles.update({name : ids})

	for profile in profiles:
		print "Generate HTML for: " + profile
		tempdata = copy.deepcopy(data)
		profiledata = filterprofile(tempdata, profiles[profile])
		filteredData = filterData(profiledata)
		outputData(filteredData, profile)
		#outputDataDebug(filteredData)

	print "Done!"

currentdirpath = os.path.dirname(os.path.realpath(sys.argv[0]))

if __name__ == '__main__':
    main()
