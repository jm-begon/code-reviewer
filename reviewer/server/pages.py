# -*- coding: utf-8 -*-
from jinja2 import Environment, PackageLoader, select_autoescape, Template
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers.special import TextLexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from pathlib import Path


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
            raw_code = f.read()

        # TODO: propose to manually select another lexer if guess was bad
        try:
            lexer = guess_lexer_for_filename(file, raw_code, stripnl=False,
                                             ensurenl=False)
        except ClassNotFound as e:
            lexer = TextLexer(stripnl=False, ensurenl=False)

        formatter = HtmlFormatter(style='xcode')
        style = formatter.get_style_defs()
        code = highlight(raw_code, lexer, formatter)
        lines = code.split('\n')[:-1]

        return {'cwd': self.cwd, 'file': file, 'lines': lines, 'style': style,
                'raw_code': raw_code}


class Save:
    """
    """

    def __init__(self, cwd, data):
        """
        """
        self.cwd = cwd
        self.data = data

    def get_html(self):
        """
        """
        file = self.data['file'][0]
        with open(self.cwd / file, 'r') as f:
            lines = f.readlines()

        comments = {}
        for line, comment in zip(self.data['lines'], self.data['comments']):
            comments[int(line)] = comment

        with open(self.cwd / (file + '.rvw'), 'w') as f:
            for i, line in enumerate(lines):
                if i + 1 in comments:
                    f.write('# [RVW] ' + comments[i + 1] + '\n')
                f.write(line)

        return '';
