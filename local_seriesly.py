#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

"""local seriesly fetches data from tvrage and generates html files"""

import os
import sys
import fetchdata
import generatehtml
import parse_cfg
from optparse import OptionParser


# remove html files and fetched data
def remove():
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
    profiles = parse_cfg.get_profile_names()
    for profile in profiles:
        try:
            os.remove(currentdirpath + "/data/" + profile + ".html")
        except OSError:
            pass

    # remove the compiled python scripts
    # TODO: why these scripts even compiled?
    print "Removing compiled python scripts..."
    try:
        os.remove(currentdirpath + "/fetchdata.pyc")
    except OSError:
        pass
    try:
        os.remove(currentdirpath + "/generatehtml.pyc")
    except OSError:
        pass
    try:
        os.remove(currentdirpath + "/parse_cfg.pyc")
    except OSError:
        pass


# fetch data
def fetch():
    """fetch data from tvrage.com"""
    fetchdata.fetchdata()


# generate html files
def generate():
    """generate html files for profiles"""
    generatehtml.generatehtml()


def main():
    """main method that parses command line arguments"""

    # use OptionParser to provide decent argument parsing
    parser = OptionParser()
    parser.add_option("-f", "--fetch", action="store_true",
        dest="fetch", help="fetch data")
    parser.add_option("-g", "--generate", action="store_true",
        dest="generate", help="generate the html documents")
    # TODO: be able to choose the config file
    #parser.add_option("-c", "--configfile", dest="config_file",
    #    help="path to config file with the profiles and show ids",
    #    metavar="FILE")
    parser.add_option("-r", "--remove", action="store_true",
        dest="clean", help="remove html files and fetched data")
    (options, args) = parser.parse_args()

    # go through the options
    if options.clean:
        remove()
    if options.fetch:
        fetch()
    if options.generate:
        generate()


if __name__ == '__main__':
    main()
