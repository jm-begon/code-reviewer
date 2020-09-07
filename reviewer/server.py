# -*- coding: utf-8 -*-
from jinja2 import Environment, PackageLoader, select_autoescape, Template
from jinja2.exceptions import TemplateNotFound
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler
from pathlib import Path

from reviewer.annotations import ReviewedCode


DEBUG = True

BASE_DIR = Path(__file__).resolve().parent
HTML_DIR = BASE_DIR / 'html'


env = Environment(
    loader=PackageLoader('reviewer', 'html'),
    autoescape=select_autoescape(['html', 'xml'])
)


# Here, we specify the file types whose that should be accessible when
# requested. Thus, they will be returned as raw data instead of being routed.
authorized_files = {
    '.css': 'text/css',
    '.js': 'text/javascript',
    '.map': '',
}


# Global variable containing all the codes being annotated
codes = {}


def MakeRequestHandlerAt(cwd):
    """
    This function is a RequestHandler factory, allowing to pass a custom
    argument (cwd) to the class RequestHandler without overwriting the
    signature of the constructor of the parent class BaseHTTPRequestHandler.
    Indeed, this signature has to be kept to pass this handler to the
    HTTPServer class.
    """
    class CustomHandler(RequestHandler):
        def __init__(self, *args, **kwargs):
            self.cwd = cwd
            self.codes = codes
            super().__init__(*args, **kwargs)
    return CustomHandler


class RequestHandler(BaseHTTPRequestHandler):
    """
    This class is responsible for handling the HTTP requests. This is done by
    writing the bytes (header and content) in the object self.wfile provided
    by the BaseHTTPRequestHandler parent class.

    This class use a Router class to generate the page according to
     - the current working directory (cwd)
     - the path of the request
     - the data of the request
    """

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

        # Route the request according to the path and data
        self.route(path, data)

    def do_POST(self):
        """
        POST request stub
        """
        pass

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

    def route(self, path, data):
        """
        """
        if DEBUG:
            print(f'{path}\n{data}')

        # Bypass routing when authorized files
        filepath = Path(HTML_DIR / path[1:])
        if filepath.suffix in authorized_files:
            with filepath.open('r') as f:
                content = f.read()
            content_type = authorized_files[filepath.suffix]
            return self.respond(200, {'Content-type': content_type}, content)

        # Otherwise, redirect according to the path with the associated data
        try:
            if path == '/':
                home_page = self._home_page(data)
                self.respond(200, {'Content-type': 'text/html'}, home_page)
            elif path == '/review':
                review_page = self._review_page(data)
                self.respond(200, {'Content-type': 'text/html'}, review_page)
            elif path == '/add_comment':
                self.respond(self._add_comment(data), {}, '')
            elif path == '/remove_comment':
                self.respond(self._remove_comment(data), {}, '')
            elif path == '/add_mark':
                self.respond(self._add_mark(data), {}, '')
            elif path == '/remove_mark':
                self.respond(self._remove_mark(data), {}, '')
            elif path == '/save':
                self.respond(self._save(data), {}, '')
            else:
                notfound = env.get_template('notfound.html').render()
                self.respond(404, {'Content-type': 'text/html'}, notfound)
            
        except Exception as exception:
            # Another error occured
            if DEBUG:
                raise exception

            error_msg = '500 Internal Error'
            self.respond(500, {'Content-type': 'text/plain'}, error_msg)

    def _home_page(self, data):
        """
        Home page of the code reviewer program.
        """
        path = Path(data['path'][0].rstrip('/') if 'path' in data else '.')
        directory = self.cwd / path

        files, dirs = [], []
        if directory.is_dir():
            for el in sorted(directory.glob(r'*')):
                dirs.append(el.name) if el.is_dir() else files.append(el.name)

        infos = {'cwd': self.cwd, 'path': path, 'files': files,
                 'dirs': dirs}

        return env.get_template('home.html').render(**infos)

    def _review_page(self, data):
        """
        Review page of the code reviewer program.
        """
        filename = data['filename'][0]
        if not filename in self.codes:
            filepath = self.cwd / filename
            # TODO: verify that 'self.cwd / filename' is not a file outside of cwd
            with open(filepath, 'r') as f:
                raw_lines = f.readlines()

            self.codes[filename] = ReviewedCode(raw_lines)

            # If this code has already been annotated, the previous annotation are loaded
            if Path(str(filepath) + '.rvw').is_file():
                self.codes[filename].load(filepath)

        # TODO: here if 'lexer' in data (because "?lexer='Python2'" is in query for example),
        # pass the argument lexer
        lines, style = self.codes[filename].get_formatted_lines(filename, lexer=None)
        markups = self.codes[filename].get_markups()
        comments = self.codes[filename].get_comments()

        # TODO: use markups and comments to display them in the review_page
        infos = {'lines': lines, 'style': style, 'filename': filename}
        return env.get_template('review.html').render(**infos)

    def _add_comment(self, data):
        filename = data['filename'][0]
        if not filename in self.codes:
            return 403

        self.codes[filename].add_comment(data['line'][0], data['comment'][0])
        return 200

    def _remove_comment(self, data):
        filename = data['filename'][0]
        if not filename in self.codes:
            return 403

        self.codes[filename].remove_comment(data['line'][0])
        return 200

    def _save(self, data):
        """
        Responsible for serializing the annotations in a .rvw when a /save request
        is received.
        """
        filename = data['filename'][0]
        if not filename in self.codes:
            return 403

        self.codes[filename].save(self.cwd / filename)
        return 200
