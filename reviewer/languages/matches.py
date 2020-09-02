# -*- coding: utf-8 -*-


# In all languages, we use \$?\w+ as a variable name match
matches = {
    'trailing_new_lines': (r'\n[\s]+\Z', r'\n'),
    'trailing_whitespaces': (r'[ \t]+$', '\n'),
    'bad_incr': (r'(\$?\w+)\s*=\s*$1\s*(\+|-)\s*1', '$1$2$2'),
    'bad_inplace_op': (r'(\$?\w+)\s*=\s*$1\s*(\+|-|\/|\*)\s*([\d\.]+)', '$1 $2= $3'),
}
