#!/usr/bin/python2.7
# -*- coding: utf-8 -*-


import cherrypy
from cherrypy import wsgiserver

import signal

from local_seriesly import LocalSeriesly

PORT = 8070
IP = '0.0.0.0'
URI_PATH = '/show'
FETCH_PATH = '/fetch'
LS_PATH = '/opt/local_seriesly'

# connection to local seriesly to generate html pages
ls = LocalSeriesly()

# wsgi method
def show_data(environ, start_response):
    # Generate HTML files.
    # TODO: Do this on a profile basis
    ls.generate()

    # get profile name from URL
    profile = environ["QUERY_STRING"]

    # build html file path
    # TODO: fix os dependent parts
    htmlfilepath = LS_PATH + "/data/" + str(profile) + ".html"

    # open html file and put lines to output
    fd = open(htmlfilepath, 'r')
    ret = ""
    for line in fd:
        ret += line

    # build response
    status = '200 OK'
    response_headers = [('Content-type','text/html')]
    start_response(status, response_headers)
    return [ret]

def fetch_data(environ, start_response):
    ls.fetch()

    # build response
    status = '200 OK'
    response_headers = [('Content-type','text/html')]
    start_response(status, response_headers)
    return ['data fetched...']

# start wsgi server
d = wsgiserver.WSGIPathInfoDispatcher({URI_PATH: show_data, FETCH_PATH: fetch_data})
server = wsgiserver.CherryPyWSGIServer((IP, PORT), d)

# signal callback
def stop_server(*args, **kwargs):
  server.stop()

# add signal callback
signal.signal(signal.SIGINT,  stop_server)

# start cherrypy server
server.start()
