#!/usr/bin/python2.7
# -*- coding: utf-8 -*-


import cherrypy
from cherrypy import wsgiserver

import signal
from threading import Lock

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from local_seriesly import LocalSeriesly

PORT = 8070
IP = '0.0.0.0'
URI_PATH = '/show'
FETCH_PATH = '/fetch'
LS_PATH = '/home/erebos/projects/programming/local_seriesly/'
DEFAULT_PROFILE = "myprofile"

# lock for the ls object, so it can be replaced when config is updated
ls_lock = Lock()

# connection to local seriesly to generate html pages
ls = LocalSeriesly()

# wsgi method
def show_data(environ, start_response):
    # Generate HTML files.
    # TODO: Do this on a profile basis
    with ls_lock:
        ls.generate()

    # get profile name from URL
    profile = environ["QUERY_STRING"]
    if not profile:
        profile = DEFAULT_PROFILE

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
    with ls_lock:
        ls.fetch()

    # get profile name from URL
    profile = environ["QUERY_STRING"]
    if not profile:
        profile = DEFAULT_PROFILE

    htmlfilepath = LS_PATH + "/media/data_fetched_template.html"

    # open html file and put lines to output
    fd = open(htmlfilepath, 'r')
    ret = ""
    for line in fd:
        line = line.replace("<!-- PROFILE_NAME -->", profile)
        ret += line

    # build response
    status = '200 OK'
    response_headers = [('Content-type','text/html')]
    start_response(status, response_headers)
    return [ret]

class UpdateConfigHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # !!!!!!!!!!!!!!!!!!!
        # BAD BAD BAAAAD HACK!!!! But, who cares, right?!
        if 'show_id.cfg' in event.src_path:
            with ls_lock:
                global ls
                print("Reloading config...")
                ls = LocalSeriesly()

event_handler = UpdateConfigHandler()
observer = Observer()
observer.start()
observer.schedule(event_handler, '.')

# start wsgi server
d = wsgiserver.WSGIPathInfoDispatcher({URI_PATH: show_data, FETCH_PATH: fetch_data})
server = wsgiserver.CherryPyWSGIServer((IP, PORT), d)

# signal callback
def stop_server(*args, **kwargs):
  server.stop()
  observer.stop()

# add signal callback
signal.signal(signal.SIGINT,  stop_server)

# start cherrypy server
server.start()
