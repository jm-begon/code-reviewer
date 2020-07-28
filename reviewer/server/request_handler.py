# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler

from reviewer.server.router import Router
from urllib.parse import urlparse, parse_qs
from pathlib import Path


def MakeRequestHandlerAt(cwd):
    """
    """
    class CustomHandler(RequestHandler):
        def __init__(self, *args, **kwargs):
            self.cwd = cwd
            super().__init__(*args, **kwargs)
    return CustomHandler


class RequestHandler(BaseHTTPRequestHandler):
    """
    """
    
    def respond(self, status, headers, content):
        """
        Send the response using BaseHTTPRequestHandler methods
    
        Arguments
        ---------
        - status: int
            The HTTP status code
        - headers: dictionary
            The dictionary of headers ({field: value})
        - content: string
            The content to send as response data
        """
        self.send_response(status)
        for field, value in headers.items():
            self.send_header(field, value)
        self.end_headers()
        self.wfile.write(bytes(content, 'utf-8'))

    def do_HEAD(self):
        """
        HEAD request stub
        """
        pass

    def do_GET(self):
        """
        GET request stub
        """
        # Parse url into path and data
        url = urlparse(self.path)
        path = url.path
        data = parse_qs(url.query)

        # Create the Router responsible for retrieving the response
        router = Router(self.cwd, path, data)
        status, headers, content = router.get_response()

        self.respond(status, headers, content)

    def do_POST(self):
        """
        POST request stub
        """
        pass
        # if 'content-length' in self.headers:
        #     data_length = int(self.headers['content-length'])
        #     data = self.rfile.read(data_length)
        # else:
        #     data = {}

        # # Create the Router responsible for retrieving the response
        # router = Router(self.path, data)
        # status, headers, content = router.get_response()

        # self.respond(status, headers, content)
