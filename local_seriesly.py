#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""local seriesly fetches data from tvrage and generates html files"""

import os
import json
import sys
import src.fetchdata as fetchdata
import src.generatehtml as generatehtml
import src.parse_cfg as parse_cfg
from optparse import OptionParser


class LocalSeriesly(object):
    """main class for local_seriesly"""

    parsecfg_obj = None
    fetchdata_obj = None
    generate_obj = None

    def __init__(self):
        self.parsecfg_obj = parse_cfg.ParseCFG()
        self.fetchdata_obj = fetchdata.Fetchdata()
        self.generate_obj = generatehtml.GenerateHTML()

    # remove html files and fetched data
    def remove(self):
        """remove working data"""
        # remove the json database with fetched data
        print "Removing show data..."
        currentdirpath = os.path.dirname(os.path.realpath(sys.argv[0]))
        try:
            os.remove(currentdirpath + "/data/seriesdb.json")
        except OSError:
            pass

        # remove the html for every profile
        print "Removing profile data..."
        profiles = self.parsecfg_obj.get_profile_names()
        for profile in profiles:
            try:
                os.remove(currentdirpath + "/data/" + profile + ".html")
            except OSError:
                pass

        # remove the compiled python scripts
        # TODO: why are these scripts even compiled?
        print "Removing compiled python scripts..."
        try:
            os.remove(currentdirpath + "/src/fetchdata.pyc")
        except OSError:
            pass
        try:
            os.remove(currentdirpath + "/src/generatehtml.pyc")
        except OSError:
            pass
        try:
            os.remove(currentdirpath + "/src/parse_cfg.pyc")
        except OSError:
            pass
        try:
            os.remove(currentdirpath + "/src/__init__.pyc")
        except OSError:
            pass

    @classmethod
    def list_all_shows(cls):
        """list all shows currently in one or more profiles"""
        currentdirpath = os.path.dirname(os.path.realpath(sys.argv[0]))

        try:
            data = json.load(open(currentdirpath + '/data/seriesdb.json', 'r'))
        except IOError:
            print "Couldn't find show data. Please fetch the data first!"
            return

        temp = []

        for show in data:
            show_id = show.keys().pop()
            show_name = show[show_id].pop()["name"]
            temp.append(show_name + " (id: " + show_id + ")")
        temp.sort()
        for line in temp:
            print line

    def profiles(self):
        """list all profiles including their ids"""
        profiles = self.parsecfg_obj.get_config_data()
        for profile in profiles:
            print "Profile: " + profile
            show_ids = profiles[profile]
            for show_id in show_ids:
                # TODO: add show name to output
                print "\t" + show_id

    # fetch data
    def fetch(self):
        """fetch data from tvrage.com"""
        self.fetchdata_obj.fetchdata()
        raw_input("Press key to exit...")

    # generate html files
    def generate(self):
        """generate html files for profiles"""
        self.generate_obj.generatehtml()

    def main(self):
        """main method that parses command line arguments"""

        # use OptionParser to provide decent argument parsing
        parser = OptionParser()
        parser.add_option("-f", "--fetch", action="store_true", dest="fetch", help="fetch data")
        parser.add_option("-g", "--generate", action="store_true", dest="generate", help="generate the html documents")
        # TODO: be able to choose the config file
        #parser.add_option("-c", "--configfile", dest="config_file",
        #    help="path to config file with the profiles and show ids",
        #    metavar="FILE")
        parser.add_option("-r", "--remove", action="store_true", dest="clean", help="remove html files and fetched data")
        parser.add_option("-l", "--list", action="store_true", dest="listshows", help="list all shows by name that are currently in a profile")
        parser.add_option("-p", "--profiles", action="store_true", dest="profiles", help="list all profiles and their shows")

        (options, args) = parser.parse_args()

        # go through the options
        if options.clean:
            self.remove()
        if options.fetch:
            self.fetch()
        if options.listshows:
            self.list_all_shows()
        if options.profiles:
            self.profiles()
        if options.generate:
            self.generate()


if __name__ == '__main__':
    OBJ = LocalSeriesly()
    OBJ.main()
