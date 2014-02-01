#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""generate html takes the fetched data and generates the profile html files"""

# ToDo:
# - add support for html datetime tags
#
#
#
#


import copy
from string import Template
from datetime import datetime, timedelta
import json
import os
import sys
import parse_cfg

# data structure:
# - data {id, series}
# -- series {name, episodes}
# --- episodes {episode}
# ---- episode {epnum, title}


class GenerateHTML(object):
    """generates the html files from the fetched data"""

    # Find the script path, so later we can find the show id file and json db

    currentdirpath = ""
    parsecfg_obj = None

    def __init__(self):
        self.currentdirpath = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.parsecfg_obj = parse_cfg.ParseCFG()

    # filter data for air date: last seven days, recently and coming up soon
    @classmethod
    def filter_data(cls, data):
        """filter data for air date"""
        last = []
        coming = []
        recently = []

        # go through all shows in data
        for i in range(len(data)):
            sid = data.keys()[i]
            name = data[sid][0]["name"]
            network = data[sid][0]["network"]
            airtime = data[sid][0]["airtime"]
            episodes = data[sid][0]["episodes"]

            # go through the episodes
            for temp in episodes:
                tempepisode = temp.pop()
                tempepisode["name"] = name
                tempepisode["network"] = network

                airdate = tempepisode["airdate"]

                tempairdate = airdate.split("-")
                year = tempairdate[0]
                month = tempairdate[1]
                day = tempairdate[2]
                hour = airtime.split(":")[0]
                minute = airtime.split(":")[1]

                # what follows here is some weird time mojo.
                # this should really be done accurately
                if (int(year) == 0):
                    year = 1
                if ((int(month) < 1) or (int(month) > 12)):
                    month = 1
                if ((int(day) < 1) or (int(month) > 31)):
                    day = 1

                airdatetime = (datetime(int(year), int(month), int(day), int(hour), int(minute), 0, 0))

                # for now we just assume one timezone
                # TODO: implement real timezone stuff
                airdatetime = airdatetime + timedelta(hours=6)

                # calculate relative airtime
                temp = datetime.now() - airdatetime

                # filter depending on relative airtime
                if (temp < timedelta(days=0)):
                    tempepisode["airdate"] = temp
                    coming.append(tempepisode)
                elif ((temp >= timedelta(days=0)) and (temp < timedelta(days=1))):
                    tempepisode["airdate"] = temp
                    recently.append(tempepisode)
                elif ((temp >= timedelta(days=1)) and (temp < timedelta(days=7))):
                    tempepisode["airdate"] = temp
                    last.append(tempepisode)

        # return the sorted episodes
        return {"last": last, "coming": coming, "recently": recently}

    # output the data on the console for debug purposes
    # hasn't been updated in quiet a while and probably won't show all data
    @classmethod
    def output_data_debug(cls, filtered_data):
        """output data on the console for debug purposes"""
        last = filtered_data["last"]
        coming = filtered_data["coming"]
        recently = filtered_data["recently"]

        print "=========="
        print "Last:"
        print "-----"
        for i in range(len(last)):
            print (last[i]["name"] + " - " + last[i]["seasonnum"] + "x" + last[i]["epnum"] + " - " + last[i]["title"])

        print "=========="
        print "Coming:"
        print "-----"
        for i in range(len(coming)):
            print (coming[i]["name"] + " - " + coming[i]["seasonnum"] + "x" + coming[i]["epnum"] + " - " + coming[i]["title"])

        print "=========="
        print "Recently:"
        print "-----"
        for i in range(len(recently)):
            print (recently[i]["name"] + " - " + recently[i]["seasonnum"] + "x" + recently[i]["epnum"] + " - " + recently[i]["title"])

    # output data for a profile in html format
    # TODO: use these <time> tags
    def output_data(self, filtered_data, profile):
        """output data to html files"""
        recently_template = Template('\
            <li class=\"vevent episode-item\">\
                <div class=\"clearfix\" style=\"width:100%\">\
                    <div class=\"left\">\
                        <div class=\"vevent-meta\">\
                            <time class=\"dtstart\" \
                                datetime=\"2011-11-12T01:00:00\">\
                                    $deltatime </time>\
                            <time class=\"dtend\" \
                                datetime=\"2011-11-12T02:00:00\"></time> \
                                    <span class=\"location\">on $network</span>,\
                                        $seasonnum$epnum\
                        </div>\
                        <span title=\"Season $seasonnum, Episode $epnum\"\
                            class=\"summary\">$seriesname: \
                                &ldquo;$epname&rdquo;</span>\
                    </div>\
                </div>\
            </li>\
        ')

        lastseven_comingup_template = Template('\
            <li class=\"vevent episode-item\">\
                <div class=\"vevent-meta\">\
                    <time class=\"dtstart\" datetime=\"2011-11-11T03:00:00\">\
                        $deltatime </time>\
                    <time class=\"dtend\" datetime=\"2011-11-11T04:00:00\">\
                        </time> <span class=\"location\">on $network</span>,\
                            $seasonnum$epnum\
                </div>\
                <span title=\"Season $seasonnum, Episode $epnum\"\
                    class=\"summary\">$seriesname: &ldquo;$epname&rdquo;</span>\
            </li>\
        ')

        # sort data
        filtered_data = self.sort_data(filtered_data)

        # paste data in template
        lastsevendays = ""
        recently = ""
        comingup = ""

        # go through the episodes and build the html code by using the templates
        for i in range(len(filtered_data["last"]) - 1, -1, -1):
            lastsevendays += (lastseven_comingup_template.substitute(
                seasonnum=filtered_data["last"][i]["seasonnum"] + "x",
                epnum=filtered_data["last"][i]["epnum"],
                seriesname=filtered_data["last"][i]["name"],
                epname=filtered_data["last"][i]["title"],
                network=filtered_data["last"][i]["network"],
                deltatime=self.airdate_to_string(filtered_data["last"][i]["airdate"])))

        for i in range(len(filtered_data["coming"]) - 1, -1, -1):
            comingup += (lastseven_comingup_template.substitute(
                seasonnum=filtered_data["coming"][i]["seasonnum"] + "x",
                epnum=filtered_data["coming"][i]["epnum"],
                seriesname=filtered_data["coming"][i]["name"],
                epname=filtered_data["coming"][i]["title"],
                network=filtered_data["coming"][i]["network"],
                deltatime=self.airdate_to_string(
                filtered_data["coming"][i]["airdate"])))

        for i in range(len(filtered_data["recently"]) - 1, -1, -1):
            recently += (recently_template.substitute(
                seasonnum=filtered_data["recently"][i]["seasonnum"] + "x",
                epnum=filtered_data["recently"][i]["epnum"],
                seriesname=filtered_data["recently"][i]["name"],
                epname=filtered_data["recently"][i]["title"],
                network=filtered_data["recently"][i]["network"],
                deltatime=self.airdate_to_string(
                filtered_data["recently"][i]["airdate"])))

        # use template.html to create new html file
        fdwrite = open(self.currentdirpath + "/data/" + profile + ".html", "w")
        fdread = open(self.currentdirpath + "/media/template.html", "r")

        # go through every line in template.html
        # replace marker by episode data
        # TODO: this depends on the comments beeing at the right place
        # that should probably be changed
        for line in fdread:
            if (line.count("<!-- RECENTLY -->") == 1):
                # TODO: figure out this whole utf-8 thing...
                fdwrite.write(recently.encode('UTF-8'))
            elif (line.count("<!-- LAST_SEVEN_DAYS -->") == 1):
                fdwrite.write(lastsevendays.encode('UTF-8'))
            elif (line.count("<!-- COMING_UP -->") == 1):
                fdwrite.write(comingup.encode('UTF-8'))
            elif (line.count("<!-- TIME_GENERATED -->") == 1):
                now = datetime.now()
                time_str = "%d-%d-%d %d:%d:%d.%d" % (now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond)
                fdwrite.write(time_str)
            elif (line.count("<!-- TIME_FETCHED -->") == 1):
                tf_epoch = os.path.getmtime(self.currentdirpath + '/data/seriesdb.json')
                tf_datetime = datetime.fromtimestamp(tf_epoch)
                tf_str = "%d-%d-%d %d:%d:%d.%d" % (tf_datetime.year, tf_datetime.month, tf_datetime.day, tf_datetime.hour, tf_datetime.minute, tf_datetime.second, tf_datetime.microsecond)
                fdwrite.write(tf_str)
            elif (line.count("<!-- FETCH_BUTTON_FORM -->") == 1):
                fdwrite.write("<form action=\"fetch?%s\">" % (profile))
            else:
                fdwrite.write(line)

    # convert the airdate to a string
    @classmethod
    def airdate_to_string(cls, airdate):
        """convert airdate to a string"""
        # example data:
        # -2 days, 10:29:04.862377
        # 2 day(s), 10 hour(s) ago
        ret = ""

        days  = airdate.days
        hours = airdate.seconds // 3600
        mins  = (airdate.seconds // 60) % 60
        if airdate >= timedelta(days = 1):
            ret = str(days) + " day(s), " + str(hours) + " hour(s) ago "
        elif airdate >= timedelta(days = 0):
            ret = str(hours) + " hour(s), " + str(mins) + " min ago "
        elif airdate >= timedelta(days = -1):
            ret = "in " + str(23 - hours) + " hour(s), " + str(59 - mins) + " min(s)"
        else:
            ret = "in " + str(-days - 1) + " day(s), " + str(23 - hours) + " hour(s) "

        return ret

    # sort data according to airdate
    @classmethod
    def sort_data(cls, filtered_data):
        """sort data according to airdate"""
        sortedcoming = []
        while (len(filtered_data["coming"]) != 0):
            maxdate = timedelta(hours=0)
            maxindex = -1
            for i in range(len(filtered_data["coming"])):
                if (filtered_data["coming"][i]["airdate"] < maxdate):
                    maxdate = filtered_data["coming"][i]["airdate"]
                    maxindex = i
            if (maxindex != -1):
                sortedcoming.append(filtered_data["coming"].pop(maxindex))

        sortedrecently = []
        while (len(filtered_data["recently"]) != 0):
            maxdate = timedelta(hours=0)
            maxindex = -1
            for i in range(len(filtered_data["recently"])):
                if (filtered_data["recently"][i]["airdate"] > maxdate):
                    maxdate = filtered_data["recently"][i]["airdate"]
                    maxindex = i
            if (maxindex != -1):
                sortedrecently.append(filtered_data["recently"].pop(maxindex))

        sortedlast = []
        while (len(filtered_data["last"]) != 0):
            maxdate = timedelta(hours=0)
            maxindex = -1
            for i in range(len(filtered_data["last"])):
                if (filtered_data["last"][i]["airdate"] > maxdate):
                    maxdate = filtered_data["last"][i]["airdate"]
                    maxindex = i
            if (maxindex != -1):
                sortedlast.append(filtered_data["last"].pop(maxindex))

        return {"last": sortedlast, "coming": sortedcoming, "recently": sortedrecently}

    # filter data for the wanted show ids
    @classmethod
    def filter_profile(cls, data, ids):
        """filter data for wanted show ids"""
        tempdata = {}
        for i in range(len(data)):
            if (ids.count(data[i].keys()[0]) > 0):
                tempdata.update(data[i])
        return tempdata

    def generatehtml(self):
        """generate html files from fetched data"""
        # load show database
        try:
            data = json.load(open(self.currentdirpath + '/data/seriesdb.json', 'r'))
        except IOError:
            print "Couldn't find show data. Please fetch the data first!"
            return

        # load cfg and store in dict
        profiles = self.parsecfg_obj.get_config_data()

        # generate html file for every profile
        for profile in profiles:
            print "Generate HTML for: " + profile
            # copy data to a temp var. Deepcopy is used since we work on the data,
            # but we need the original data for the next profile
            # TODO: maybe there is a faster way, so we don't have to copy the data
            tempdata = copy.deepcopy(data)
            # filter for profile show ids
            profiledata = self.filter_profile(tempdata, profiles[profile])
            # filter data for airdate
            filtered_data = self.filter_data(profiledata)
            # output data to html
            self.output_data(filtered_data, profile)
            # output data to console
            #output_data_debug(filtered_data)
