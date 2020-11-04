import os

from collections import defaultdict
from enum import Enum


class Severity(Enum):
    GOOD = "good"
    NEUTRAL = "neutral"
    MILD = "mild"
    SEVERE = "severe"


class Comment(object):
    """
    end_line included
    """
    def __init__(self, file, start_line, end_line=None, severity=None,
                 text=""):
        # TODO might be nice to handle columns, author, type, timestamp(?)
        self.fpath = file
        self.start_line = start_line
        self.text = text
        self.end_line = start_line if end_line is None else end_line
        self.severity = Severity.NEUTRAL if severity is None else severity

    def __repr__(self):
        return "{}({}, {}, {}, {})" \
               "".format(self.__class__.__name__,
                         repr(self.fpath),
                         repr(self.start_line),
                         repr(self.end_line),
                         repr(self.severity),
                         repr(self.text),)

    def __str__(self):
        return "{}:{}-{};{}".format(self.fpath, self.start_line, self.end_line,
                                    self.text)



class CSVCommentParser(object):
    @classmethod
    def review_path(cls, fpath):
        dir, fullname = os.path.split(fpath)
        name, ext = os.path.splitext(fullname)
        return os.path.join(dir, "review_{}.csv".format(name))

    def __init__(self, mode="w"):
        self.mode = mode


    def save_from_same_file(self, comments):
        if len(comments) == 0:
            return
        fpath = self.__class__.review_path(comments[0].fpath)

        lines = []
        for comment in comments:
            line = ";".join([str(comment.fpath),
                             str(comment.start_line),
                             str(comment.end_line),
                             str(comment.severity.value),
                             comment.text.strip().replace(";", ",")])
            lines.append(line)

        with open(fpath, self.mode) as hdl:
            hdl.write(os.linesep.join(lines))
            hdl.write(os.linesep)

        return self

    def save(self, comments):
        dispath = defaultdict(list)
        for comment in comments:
            dispath[comment.fpath].append(comment)

        for comment_group in dispath.values():
            self.save_from_same_file(comment_group)

        return self

    def load(self, fpath):
        comments = []
        if not os.path.exists(fpath):
            return comments

        with open(fpath, "r") as hdl:
            content = hdl.readlines()

        for i, line in enumerate(content):
            line = line.strip()
            if len(line) == 0:
                continue
            try:
                file, start, end, severity, text = line.split(";")
                start = int(start)
                if len(end) == 0:
                    end = None
                else:
                    end = int(end)

                try:
                    severity = Severity(severity)
                except ValueError as e:
                    print(e)  # TODO log facility
                    severity = Severity.NEUTRAL

                comments.append(Comment(file, start, end, severity, text))
            except ValueError as e:
                # TODO log facility
                print("Error with line {} ('{}'): {}".format(i, line, e))

        return comments

    def load_for_source_file(self, fpath):
        return self.load(self.__class__.review_path(fpath))


