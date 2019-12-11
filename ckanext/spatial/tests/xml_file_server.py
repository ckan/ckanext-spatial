from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
import os

import http.server
import socketserver
from threading import Thread


PORT = 8999

def serve(port=PORT):
    '''Serves test XML files over HTTP'''
    
    # Make sure we serve from the tests' XML directory
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'xml'))

    Handler = http.server.SimpleHTTPRequestHandler
    
    class TestServer(socketserver.TCPServer):
        allow_reuse_address = True
    
    httpd = TestServer(("", PORT), Handler)
    
    print('Serving test HTTP server at port', PORT)

    httpd_thread = Thread(target=httpd.serve_forever)
    httpd_thread.setDaemon(True)
    httpd_thread.start()
