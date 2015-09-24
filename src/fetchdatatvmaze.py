#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""fetch data from tvrage"""

# ToDo:
# - add support for html datetime tags
# - optimize data structure
# - optimize xml parsing (that is just not my thing)
#
#


import urllib2
import xml.dom.minidom as dom
import xml.parsers.expat
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

#[
#  {
#    "18164": [
#      {
#        "network": "<network country=\"US\">amc",
#        "airtime": "22:00",
#        "name": "Breaking Bad",
#        "episodes": [
#          [
#            {
#              "epnum": "01",
#              "airdate": "2008-01-20",
#              "seasonnum": "1",
#              "title": "Pilot"
#            }
#          ]
#        ]
#      }
#    ]
#  }
#]


class FetchdataTVMaze(object):
    """fetch data for local_seriesly"""
    currentdirpath = ""
    maxconnections = 0
    maxerrorcount = 10
    sema_pool = None
    parsecfg_obj = None

    def __init__(self):
        # get the script path, so the config- and json-file can be found
        self.currentdirpath = os.path.dirname(os.path.realpath(sys.argv[0]))

        self.parsecfg_obj = parse_cfg.ParseCFG()

        # limit the number of threads/connections that can be made simultaneous
        self.maxconnections = 10
        self.sema_pool = threading.BoundedSemaphore(value=self.maxconnections)

    def id_tvrage_to_tvmaze(self, rage_id):
        # http://api.tvmaze.com/lookup/shows?tvrage=24493
        url_template = r"http://api.tvmaze.com/lookup/shows?tvrage="
        try:
            resp = urllib2.urlopen(url_template + str(rage_id)).read()
            resp = json.loads(resp)
            return resp["id"]
        except:
            return None

    def fetch_episode_info(self, show_id):
        url_template = r'http://api.tvmaze.com/shows/{show_id}/episodes'
        
        try:
            resp = urllib2.urlopen(url_template.format(show_id=show_id)).read()
            resp = json.loads(resp)
        except:
            print("Could not fetch episode info!")
            return []        

        episodes = []
        for e in resp:
            temp = {}
            temp["epnum"]     = e["number"]
            temp["airdate"]   = e["airdate"]
            temp["seasonnum"] = str(e["season"])
            temp["title"]     = e["name"]
            episodes.append([temp])
        return episodes


    def fetch_series_info(self, show_id):
        print('fetching {show_id}'.format(show_id=show_id))
        url_template = r'http://api.tvmaze.com/shows/{show_id}'
        
        try:
            resp = urllib2.urlopen(url_template.format(show_id=show_id)).read()
            resp = json.loads(resp)
        except:
            return None
            
        airtime = resp["schedule"]["time"]
        
        # Stupid Hack: Make sure all data is valid
        name = ""
        try:
            name = resp["name"]
        except:
            pass
          
        # try either network or webChannel (e.g. Netflix) name  
        network = ""
        try:
            network = resp["network"]["name"]
        except:
            try:
                network = resp["webChannel"]["name"]
            except:
                pass
                
        if airtime == "":
          airtime = "20:00"
          
        episodes = self.fetch_episode_info(show_id)

        ret = {"name": name,
               "airtime": airtime,
               "network": network,
               "episodes": episodes}
        return ret
        

    def fetchdata(self):
        """main method to fetch data"""
        print "[     ] Starting fetching data"
        
        # http://api.tvmaze.com/shows/1
        # {
        #   "id": 1,
        #   "name": "Under the Dome",
        #   "schedule": {
        #     "time": "22:00"
        #   }
        #   "network": {
        #     "name": "CBS"
        #   }
        # }
        
        # http://api.tvmaze.com/shows/1/episodes?specials=1
        # [
        #   {
        #     "season": 1,
        #     "airstamp": "2013-07-01T22:00:00-04:00",
        #     "number": 3,
        #     "name": "Outbreak"
        #   }, ...
        # ]
        
        # get the show ids from the config file
        show_ids = self.parsecfg_obj.get_show_ids()
        
        data = []
        for i in show_ids:
            r = self.fetch_series_info(i)
            if r is not None:
                data.append({i: [r]})
        
        # dump the data to the json database,
        # so it can be used by the other script later
        json_path = self.currentdirpath + '/data/seriesdb.json'
        print "[     ] Writing data to " + json_path
        json.dump(data, open(json_path, 'w'))

        print "[     ] Finished fetching data"
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        