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
    def __init__(self, data):
        if not instanceof(data, dict):
            raise ValueError('Request data should be passed as a dictionary')
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
    def __init__(self, data):
        self.data = data
        self.template = 'home.html'

    def format_data(self):
        """
        """
        cwd = self.data['cwd'][0].rstrip('/') if 'cwd' in self.data else '~'
        directory = Path(cwd).expanduser().resolve()
        cwd = str(directory)
        
        files, dirs = [], []
        if directory.is_dir():
            for el in directory.glob(r'*'):
                dirs.append(el.name) if el.is_dir() else files.append(el.name)

        return {'cwd': cwd, 'files': files, 'dirs': dirs}


class ReviewPage(Page):
    def __init__(self, data):
        self.data = data
        self.template = 'review.html'

    def format_data(self):
        """
        """
        cwd = self.data['cwd'][0] if 'cwd' in self.data else '~'
        directory = Path(cwd).expanduser().resolve()
        cwd = str(directory)
        
        files = []
        if directory.is_dir():
            for el in directory.glob(r'*'):
                if el.is_file() and not el.name.startswith('.'):
                    files.append(el.name)
        elif directory.is_file():
            files.append(directory.name)
        
        return {'files': files}
