# -*- coding: utf-8 -*-
from pathlib import Path

from server.pages import HomePage, ReviewPage

from jinja2.exceptions import TemplateNotFound


DEBUG = True

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / 'server' / 'templates'

routes = {
    '/': HomePage,
    '/review': ReviewPage
}
content_type = {
    '.css': 'text/css',
    '.js': 'text/javascript',
}


class Router():
    """
    """
    def __init__(self, path, data=None):
        """
        """
        self.path = path
        if data is None:
            self.data = {}
        else:
            self.data = data

        if DEBUG:
            print(f'Path: {self.path}')
            print(f'Data: {self.data}')

    def get_response(self):
        """
        """
        # Routes the files of type .css or .js
        path = Path(TEMPLATES_DIR / self.path[1:])  # [???] not the best way ?
        if path.suffix in content_type:
            with path.open('r') as f:
                content = f.read()
            return 200, {'Content-type': content_type[path.suffix]}, content

        try:
            page = routes[self.path](self.data)
            return 200, {'Content-type': 'text/html'}, page.get_html()

        except (KeyError, TemplateNotFound) as e:
            # Route does not exist
            if DEBUG:
                print(e)
            return 404, {'Content-type': 'text/plain'}, '404 Not Found'

        except Exception as e:
            # Another error occured
            if DEBUG:
                raise e
            return 500, {'Content-type': 'text/plain'}, '500 Internal Error'
