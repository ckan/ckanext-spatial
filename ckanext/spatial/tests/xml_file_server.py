from __future__ import print_function

import os

try:
    from http.server import SimpleHTTPRequestHandler
    from socketserver import TCPServer
except ImportError:
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from SocketServer import TCPServer

from threading import Thread


PORT = 8999


class MyHttpRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/xml")
        self.end_headers()

        # ignore the path from the ? to pick up the file correctly
        path = self.path[1:(self.path.index('?'))] if '?' in self.path else self.path[1:]

        with open(path, 'rb') as f:
            content = f.read().decode('utf-8')

        self.wfile.write(bytes(content, "utf-8"))

        return


def serve(port=PORT):
    """Serves test XML files over HTTP"""

    # Make sure we serve from the tests' XML directory
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "xml"))

    Handler = MyHttpRequestHandler

    class TestServer(TCPServer):
        allow_reuse_address = True

    httpd = TestServer(("", PORT), Handler)

    print("Serving test HTTP server at port", PORT)

    httpd_thread = Thread(target=httpd.serve_forever)
    httpd_thread.setDaemon(True)
    httpd_thread.start()
