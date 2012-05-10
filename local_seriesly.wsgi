import os
from cgi import parse_qs

def application(environ, start_response):
    status = '200 OK'
    output = ""

    # TODO: check if valid filename
    # TODO: make path dynamic or something
    profile = environ['QUERY_STRING']
    filename = "/var/www/local_seriesly/data/" + profile + ".html"

    try:
        fd = open(filename, "r")
        for line in fd:
            output = output + line
        fd.close()
    except IOError:
        output = "Invalid profile name"

    response_headers = [('Content-type', 'text/html'), ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]
