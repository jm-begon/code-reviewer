# -*- coding: utf-8 -*-
import json
from collections import OrderedDict

from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers.special import TextLexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

from .comment import CSVCommentParser, Severity, Comment


class ReviewedCode:
    """
    ReviewedCode is the class containing the annotations and the content of the
    code being reviewed. This is a view class. It knows about highlighted lines
    and texts but does not know the concept of comment.

    """


    @classmethod
    def from_file(cls, fpath):
        with open(fpath, 'r') as f:
            raw_lines = f.readlines()
        return cls(raw_lines, fpath).load()

    def __init__(self, raw_lines, fpath, comment_parser=None):
        self.raw_lines = raw_lines
        self.fpath = fpath
        self.comment_parser = CSVCommentParser() if comment_parser is None \
            else comment_parser

        self.texts = OrderedDict()
        self.markups = OrderedDict()
        self.saved = True

        self.severity2color = {
            Severity.GOOD: "green",
            Severity.NEUTRAL: "blue",
            Severity.MILD: "orange",
            Severity.SEVERE: "red",
        }

        self.color2severity = {v:k for k, v in self.severity2color.items()}
        self.color2severity[None] = Severity.NEUTRAL

    def add_mark(self, line, color_code):
        self.markups[line] = color_code
        self.saved = False

    def remove_mark(self, line):
        if line not in self.markups:
            return
        del self.markups[line]
        self.saved = False

    def add_text(self, line, text):
        self.texts[line] = text
        self.saved = False

    def remove_text(self, line):
        if line not in self.texts:
            return

        del self.texts[line]
        print("after remove:")
        print(self.texts)
        self.saved = False

    def get_formatted_lines(self, filename, lexer=None):
        """
        Given the raw_lines, markups and comments, generate the html code to
        display the code and comment.
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

    def get_texts(self):
        return self.texts

    def get_markups(self):
        return self.markups

    def get_saved(self):
        return self.saved

    def save(self):
        # Infer comment
        comments = []
        mark_lines = set()

        for line, text in self.texts.items():
            line = int(line)
            color_code = self.markups.get(line)
            severity = Severity(self.color2severity[color_code])
            color_code = self.severity2color[severity]  # if color_code was None
            prev_color_code = color_code
            end_line = line
            while color_code is not None and color_code == prev_color_code:
                mark_lines.add(end_line)
                prev_color_code = color_code
                end_line += 1
                color_code = self.markups.get(end_line)

            comments.append(Comment(self.fpath, line, end_line-1, severity, text))

        for line, color_code in self.markups.items():
            line = int(line)
            if line not in mark_lines:
                comments.append(Comment(self.fpath, line, line,
                                self.color2severity[color_code], ""))



        self.comment_parser.save_from_same_file(comments)
        self.saved = True


    def load(self):
        comments = self.comment_parser.load_for_source_file(self.fpath)
        for comment in comments:
            if len(comment.text) > 0:
                # Do not show empty comment
                self.add_text(comment.start_line, comment.text)

            color = self.severity2color[comment.severity]

            for line in range(comment.start_line, comment.end_line+1):
                self.add_mark(line, color)

        self.saved = True
        return self


