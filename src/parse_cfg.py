#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""parses local_seriesly config file"""

import os
import sys

class ParseCFG:

    # {name: [ids...]}
    CONFIG_DATA_PROFILES = None

#    def parse_config(self):
    def __init__(self):
        """parse config file"""

        # get the current dir
        currentdirpath = os.path.dirname(os.path.realpath(sys.argv[0]))

        self.CONFIG_DATA_PROFILES = {}

        # open the config file
        # TODO: what if the config file is not there -> panic!
        fdcfg = open(currentdirpath + '/show_id.cfg', 'r')

        # parse the config file
        # TODO: make this a little more robust (maybe use XML...)
        for line in fdcfg:
            line = line.replace(" ", "")
            if (line.find("#") == -1 and line.find("=") != -1):
                temp = line.split("=")
                name = temp[0]
                ids = temp[1].strip("\n").split(",")
                self.CONFIG_DATA_PROFILES.update({name: ids})


    def get_config_data(self):
        """get complete config data with profiles and ids"""
        return self.CONFIG_DATA_PROFILES


    def get_profile_names(self):
        """get a list of all profile names"""
        return self.CONFIG_DATA_PROFILES.keys()


    def get_show_ids(self):
        """get all unique show ids"""
        # filter the profile id to a list of all ids
        show_ids = []
        for batch in self.CONFIG_DATA_PROFILES.values():
            for show_id in batch:
                show_ids.append(show_id)

        # cast to set and back to eliminate redundant ids
        show_ids = list(set(show_ids))

        # sort list
        show_ids.sort()

        return show_ids
