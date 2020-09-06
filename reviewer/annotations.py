# -*- coding: utf-8 -*-
import json

from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers.special import TextLexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound


class ReviewedCode:
    """
    ReviewedCode is the class containing the annotations and the content of the
    code being reviewed. This class can be serialized into a .rvw file, and we
    can load it from a .rwv file.
    """

    def __init__(self, raw_lines):
        self.raw_lines = raw_lines
        self.comments = {}
        self.markups = {}
        self.saved = True

    def add_markup(self, line, color_code):
        """
        TODO: Charles, tu peux modifier autant que tu veux.
        """
        self.markups[line] = color_code
        self.saved = False

    def remove_markup(self, line):
        """
        TODO: Charles, tu peux modifier autant que tu veux.
        """
        if line not in self.markups:
            return
        del self.markups[line]
        self.saved = False

    def add_comment(self, line, comment):
        """
        TODO: Charles, tu peux modifier autant que tu veux.
        """
        self.comments[line] = comment
        self.saved = False

    def remove_comment(self, line):
        """
        TODO: Charles, tu peux modifier autant que tu veux.
        """
        if line not in self.comments:
            return

        del self.comments[line]
        self.saved = False

    def get_formatted_lines(self, filename, lexer=None):
        """
        Given the raw_lines, markups and comments, generate the html code to
        display the code and comment.

        TODO: Charles, tu peux modifier autant que tu veux.
        """
        raw_code = ''.join(self.raw_lines)
        try:
            if lexer is not None:
                # TODO: add possibility in review_page to select a lexer
                lexer = get_lexer_by_name(lexer)
            else:
                lexer = guess_lexer_for_filename(filename, raw_code,
                                                 stripnl=False, ensurenl=False)
        except ClassNotFound as e:
            lexer = TextLexer(stripnl=False, ensurenl=False)

        formatter = HtmlFormatter(style='xcode', nowrap=True)
        style = formatter.get_style_defs()
        code = highlight(raw_code, lexer, formatter)
        lines = code.split('\n')

        return lines, style

    def get_comments(self):
        """
        TODO: Charles, tu peux modifier autant que tu veux.
        """
        return self.comments

    def get_markups(self):
        """
        TODO: Charles, tu peux modifier autant que tu veux.
        """
        return self.markups

    def save(self, filepath):
        review = {
            'markups': self.markups,
            'comments': self.comments,
            'raw_lines': self.raw_lines,
        }
        with open(str(filepath) + '.rvw', 'w') as f:
            f.write(json.dumps(review))

        self.saved = True

    def load(self, filepath):
        with open(str(filepath) + '.rvw', 'r') as f:
            review = json.loads(f.read())

        self.markups = review['markups']
        self.comments = review['comments']
        self.raw_lines = review['raw_lines']
