"""
Example program for the courses of INFO02050 and INFO0902 (ULiege).

This program highlight part of the c99 code which may be problematic
(with respect to optimal use of language and style). It will produce many
false positive which must be dismissed manually.

TODO: use pygment and work at the lexer level
"""

import re
import sys
import os
from collections import namedtuple, OrderedDict

# Some regex explanation. See http://www.dii.uchile.cl/~daespino/files/Iso_C_1999_definition.pdf annex A for details
# r'[_a-zA-Z]\w*'   identifier
# r'for\s*\(\s*(([_a-zA-Z]\w*\s*=.*)|);.*;.*\)'   for(;;) or for without identifier
# r'.*\s*[!|=]=\s*(true|false|1|NULL).*'   explicit test for boolean
# r'.*\s*(\+=)\s*1\s*'   explicit incrementation
from reviewer import CSVCommentParser
from reviewer import Comment

Positive = namedtuple("Positive", ["file", "line", "content"])

C99_ID = r'[_a-zA-Z]\w*'  # https://www2.cs.arizona.edu/~debray/Teaching/CSc453/DOCS/cminusminusspec.html



L1 = "[L1] Import issue."  # Useless or missing
L2 = "[L2] Misuse of global variables or macro."  # No macro. typedef/const instead
L3 = "[L3] Missing static on auxiliary function."
L4 = "[L4] Suboptimal code structure."  # Too complex, not modular enough, useless funcitons, etc.
L5 = "[L5] Lack of flexibility."
L6 = "[L6] Initialization/declaration mishap."
L7 = "[L7] Inadequate type."
L8 = "[L8] Inadequate control structure."  # Lots of if when switch can do, etc.
L9 = "[L9] Shortcut misused."  # == 1, ternary, etc.
L10 = "[L10] Proper check of returned value."  # .alloc, fopen, etc. Also conditional memory leaks

S1 = "[S1] Unclear variable names."
S2 = "[S2] Inconsistent names."
S3 = "[S3] indentation or spacing inconsistencies."
S4 = "[S4] Lack of readability."
S5 = "[S5] Lack (or abundance) of comments and specifications."


def specialize(error_type, info):
    return "{}: {}.".format(error_type[:-1], info)




class Checker(object):
    def __init__(self, *checks):
        self.checks = checks

    def check_file(self, fpath):
        with open(fpath) as handle:
            # Code is expected quite small
            text = handle.read().split(os.linesep)

        comments = []

        for i, line in enumerate(text):
            for check in self.checks:
                if check.check_line(line):
                    comments.append(Comment(fpath, i + 1,
                                            text=check.describe()))

        return comments




class RegularCheck(object):
    def __init__(self, description, regexp):
        self.description = description
        self.regex = regexp

    def describe(self):
        return self.description

    def check_line(self, line):
        return re.search(self.regex, line)



class StdioCheck(RegularCheck):
    def __init__(self):
        super().__init__(specialize(L1, "stdio + (f)printf (library code "
                                        "should not produce output which "
                                        "cannot be turned down)"),
                         r'(stdio)|(printf)')




class DefineCheck(RegularCheck):
    def __init__(self):
        super().__init__(specialize(L2, "forbidden use of 'define'. Use "
                                        "typedef or const instead (define "
                                        "makes it hard to find bugs and p"
                                        "rovide no advantage for what we do "
                                        "in this course)"),
                         r'(#define)')


class ExternCheck(RegularCheck):
    def __init__(self):
        super().__init__(specialize(L6, "forbidden use of 'extern'"),
                         r'(extern)')


class ForC99StyleCheck(RegularCheck):
    def __init__(self):
        super().__init__(specialize(L6, "non-C99 for loop style (declare your "
                                        "variables in the for statement to "
                                        "keep everything local)"),
                         r'for\s*\(\s*(([_a-zA-Z]\w*\s*=.*)|);.*;.*\)')


class ReturnDigitCheck(RegularCheck):
    def __init__(self):
        super().__init__(specialize(L7, "non-use of true|false (use boolean "
                                        "type for better readability)"),
                         r'(return)\s*\(?\s*\d+\s*\)?\s*;')


class GotoCheck(RegularCheck):
    def __init__(self):
        super().__init__(specialize(L8, 'forbidden use of goto (rely on more '
                                        'predictable control structure for '
                                        'better readability)'),
                         r'(goto)')


class DirectExitCheck(RegularCheck):
    def __init__(self):
        super().__init__(specialize(L8, "forbidden use of direct exit (library "
                                        "code should not decide to close the "
                                        "program; this must be done by the "
                                        "business part of the code)"),
                         r'(exit)')

class AssertCheck(RegularCheck):
    def __init__(self):
        super().__init__(specialize(L8, 'over-reliance on assert (assert are '
                                        'deactivated in production mode and '
                                        'should not be the only way to avoid '
                                        'common user input mistakes)'),
                         r'(assert)')


class DirectBoolCheck(RegularCheck):
    def __init__(self):
        # Verbose (boolean) testing--such as '==true' or '== NULL'
        super().__init__(specialize(L9, "non-use of appropriate shortcuts"),
                         r'.*\s*[!|=]=\s*(true|false|1|NULL).*')
        # looking for '== 0' would raise quite a lot of false positive as it
        # is a frequent test


class IncremetShortcutCheck(RegularCheck):
    def __init__(self):
        super().__init__(
            specialize(L9, "Non-use of incrementation shortcut"),
            r'.*\s*(\+=)\s*1\s*'
        )

    def check_line(self, line):
        match = super().check_line(line)  # detect pattern id1 = id2 + 1
        if match:
            return match
        regexp = r'('+C99_ID+r')' + r'\s*=\s*' + r'('+C99_ID+r')' + \
                 r'\s*\+\s*1\s*'
        match = re.match(regexp, line)
        if match:
            return match.group(1) == match.group(2)
        return None


class FOpenCheck(RegularCheck):
    def __init__(self):
        # Will highlight every fopen. Must be discarded manually
        super().__init__(specialize(L10, "forgotten check for 'fopen'"),
                         r'(fopen)')

class AllocCheck(RegularCheck):
    def __init__(self):
        # Will highlight every .alloc. Must be discarded manually
        super().__init__(specialize(L10, "forgotten check for .alloc"),
                         r'([mc]alloc)|(realloc)')


class SwapCheck(RegularCheck):
    def __init__(self):
        # Will make many false positive but the time gain is still worth it
        super().__init__(specialize(L4, "should be an inline function"),
                         r'(void swap)')


def get_grade(folders="./*/", order=None):
    import glob
    from collections import defaultdict
    from reviewer.comment import Severity

    regex = re.compile(r'^(\[[LS]\d\d?\])')

    loader = CSVCommentParser().load

    # Collecting info
    infos = {}
    for file in glob.glob(os.path.join(folders, "review_*.csv")):
        group = os.path.basename(os.path.dirname(file))
        group_info = infos.get(group)
        if group_info is None:
            group_info = defaultdict(int)
            infos[group] = group_info

        print("Loading file '{}'...".format(file))
        comments = loader(file)
        for comment in comments:
            # take into account only mild/sevre comments
            if comment.severity not in {Severity.MILD, Severity.SEVERE}:
                continue

            # Get type from text
            match = regex.search(comment.text)
            if not match:
                continue

            type = match.group(0)

            group_info[type] += (1 if comment.severity == Severity.MILD else 5)

    # Parsing stuff
    if order is None:
        order = infos.keys()

    no_info = []

    errors = ["[L{}]".format(i) for i in range(1, 11)]
    errors.extend(["[S{}]".format(i) for i in range(1, 5)])
    print("Group", end='\t')
    for e in errors:
        print(e, end='\t')
    print()

    for group in order:
        print(group, end="\t")

        group_info = infos.get(group)
        if group_info is not None:
            for error in errors:
                grade = group_info.get(error, 0)
                if grade == 0:
                    print("", end="\t")
                elif grade <= 3:
                    print(2, end="\t")
                else:
                    print(5, end="\t")
        else:
            no_info.append(group)
        print()


    print();print("No info for", os.linesep.join(no_info))



def prepare_pdfs(folders="./*/", order=None, salt=""):
    # Suppose all pdfs of a given group are in the group folder
    import glob, os
    from collections import defaultdict
    import tarfile
    from datetime import datetime
    from hashlib import md5 as hashf

    # gather files
    group2files = defaultdict(list)
    for file in glob.glob(os.path.join(folders, "*.pdf")):
        group = os.path.basename(os.path.dirname(file))
        group2files[group].append(file)

    if order is None:
        order = group2files.keys()

    empty = set()

    date = datetime.now()

    for group in order:
        files = group2files.get(group)
        if files is None or len(files) == 0:
            empty.add(group)
            print()
            continue

        h = hashf()
        h.update(salt.encode("utf-8"))
        h.update(str(date).encode("utf-8"))

        for f in files:
            with open(f, "rb") as hdl:
                h.update(hdl.read())


        prefix = h.hexdigest()

        axv_name = "{}_{}_feedback.tar.gz".format(prefix, group)
        print(group, "\t", axv_name)
        with tarfile.open(axv_name, "w:gz") as axv:
            for fpath in files:
                axv.add(fpath, os.path.basename(fpath))


    print(); print("No feedback for", os.linesep, os.linesep.join(empty))














if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser("Perform checks on .c student files to "
                                     "highlight (potential) problems")
    parser.add_argument("--library", action='store_true', default=False,
                        help="Consider the code as library in production-ready "
                             "mode")

    parser.add_argument("files", nargs="*")
    args = parser.parse_args()

    checks = [
        DefineCheck(), ExternCheck(), ForC99StyleCheck(),
        ReturnDigitCheck(), GotoCheck(),
        DirectBoolCheck(), IncremetShortcutCheck(),
        FOpenCheck(), AllocCheck(), SwapCheck(),
    ]

    if args.library:
        checks.extend([StdioCheck(), AssertCheck(), DirectExitCheck()])


    checker = Checker(*checks)
    saver = CSVCommentParser()

    for file in args.files:
        print("Processing file", file, " ...")
        try:
            comments = checker.check_file(file)
            if len(comments) > 0:
                print(" {} comment(s)".format(len(comments)))
                saver.save(comments)

        except Exception as e:
            print("File", file, "was skipped ({})".format(e))



    print("Check for the following mistakes:")
    print("---------------------------------")
    print(L1)
    print(L2)
    print(L3)
    print(L4)
    print(L5)
    print(L6)
    print(L7)
    print(L8)
    print(L9)
    print(L10)
    print(S1)
    print(S2)
    print(S3)
    print(S4)
    print(S5)
