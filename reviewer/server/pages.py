# -*- coding: utf-8 -*-
from jinja2 import Environment, PackageLoader, select_autoescape
from pathlib import Path

from reviewer.languages.matches import languages


env = Environment(
    loader=PackageLoader('reviewer.server', 'html'),
    autoescape=select_autoescape(['html', 'xml'])
)


class Page():
    """
    """

    def __init__(self, cwd, data):
        self.cwd = cwd
        self.data = data
        self.template = 'notfound.html'

    def format_data(self):
        """
        """
        return self.data

    def get_html(self):
        """
        """
        template = env.get_template(self.template)
        infos = self.format_data()
        return template.render(**infos)


class HomePage(Page):
    """
    """

    def __init__(self, cwd, data):
        self.cwd = cwd
        self.data = data
        self.template = 'home.html'

    def format_data(self):
        """
        """
        path = Path(self.data['path'][0].rstrip('/') if 'path' in self.data else '.')
        directory = self.cwd / path
        
        files, dirs = [], []
        if directory.is_dir():
            for el in sorted(directory.glob(r'*')):
                dirs.append(el.name) if el.is_dir() else files.append(el.name)

        return {'cwd': self.cwd, 'path': path, 'files': files, 'dirs': dirs}


class ReviewPage(Page):
    """
    """

    def __init__(self, cwd, data):
        self.cwd = cwd
        self.data = data
        self.template = 'review.html'

    def format_data(self):
        """
        """
        file = self.data['file'][0]
        with open(self.cwd / file, 'r') as f:
            lines = f.readlines()

        return {'cwd': self.cwd, 'file': file, 'lines': lines}
