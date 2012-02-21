#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""fetch data from tvrage"""

# ToDo:
# - add support for html datetime tags
# - optimize data structure
#
#
#


import urllib2
import xml.dom.minidom as dom
import json
import os
import sys
import threading
import httplib
import parse_cfg

# data structure (more or less):
# - data {id, series}
# -- series {name, episodes}
# --- episodes {episode}
# ---- episode {epnum, title}


# This method fetches the data for a specific show (url)
def get_series_info(ids, data):
    """fetch data for specific show"""
    SEMA_POOL.acquire()

    series = []
    done = 0
    url_template = "http://services.tvrage.com/feeds/full_show_info.php?sid="

    while(done == 0):
        try:
            parsed_dict = dom.parse(urllib2.urlopen(url_template + ids))
            done = 1
        except httplib.BadStatusLine:
            print "[" + ids.rjust(5) + "] Connection error - retry"
        except httplib.IncompleteRead:
            print "[" + ids.rjust(5) + "] Connection error - retry"
        except IOError:
            print "[" + ids.rjust(5) + "] Connection timed out - retry"

    seriesname = (parsed_dict.getElementsByTagName('name')[0].toxml()
        .replace("<name>", "").replace("</name>", ""))
    network = (parsed_dict.getElementsByTagName('network')[0].toxml()
        .replace("<network country=US>", "").replace("</network>", ""))
    airtime = (parsed_dict.getElementsByTagName('airtime')[0].toxml()
        .replace("<airtime>", "").replace("</airtime>", ""))
    series.append({
        "name": seriesname,
        "network": network,
        "airtime": airtime,
        "episodes": get_episodes_info(parsed_dict)
    })

    print "[" + ids.rjust(5) + "] Stopping thread to fetch data"
    data.append({ids: series})

    SEMA_POOL.release()


# parse dom dict for episodes
def get_episodes_info(parsed_dict):
    """parse dom dict for episodes"""
    episodes = []
    for node in parsed_dict.getElementsByTagName("episode"):
        episodes.append(get_episode_info(node))
    return episodes


# parse dom node for episode info
def get_episode_info(node):
    """parse dom node for episode info"""
    children = node.childNodes
    episode = []
    epnum = 0
    title = ""
    airdate = ""

    for child in children:
        if (child.toxml().count("seasonnum") == 2):
            epnum = child.toxml()
        if (child.toxml().count("title") == 2):
            title = child.toxml()
        if (child.toxml().count("airdate") == 2):
            airdate = child.toxml()

    seasonnum = ""
    try:
        seasonnum = node.parentNode.attributes["no"].value
    except KeyError:
        pass

    episode.append({
        "epnum": (str(epnum).replace("<seasonnum>", "")
            .replace("</seasonnum>", "")),
        "title": (str(title.encode("utf-8"))
            .replace("<title>", "").replace("</title>", "")),
        "seasonnum": seasonnum,
        "airdate": (str(airdate).replace("<airdate>", "")
            .replace("</airdate>", ""))
    })
    return episode


def fetchdata():
    """main method to fetch data"""
    print "[     ] Starting fetching data"

    # http://services.tvrage.com/feeds/full_show_info.php?sid=8322

    show_ids = parse_cfg.get_show_ids()

    data = []

    # fetch data for every show and store in data dict
    threads = []
    for ids in show_ids:
        print "[" + ids.rjust(5) + "] Starting thread to fetch data"
        temp_thread = (threading.Thread(target=get_series_info,
            args=(ids, data)))
        threads.append(temp_thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # TODO: catch keyboard interrupt

    # dump the data to the json database,
    # so it can be used by the other script later
    json_path = CURRENTDIRPATH + '/data/seriesdb.json'
    print "[     ] Writing data to " + json_path
    json.dump(data, open(json_path, 'w'))

    print "[     ] Finished fetching data"


# get the script path, so the config- and json-file can be found
CURRENTDIRPATH = os.path.dirname(os.path.realpath(sys.argv[0]))

# limit the number of threads/connections that can be made simultaneous
MAXCONNECTIONS = 10
SEMA_POOL = threading.BoundedSemaphore(value=MAXCONNECTIONS)

if __name__ == '__main__':
    fetchdata()
