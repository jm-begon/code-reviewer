from pygments import lexers
from pygments.formatters import HtmlFormatter
from pygments import highlight

class Code():
	def __init__(self, header, footer):
		self.header = header
		self.footer = footer
		self.content = []

	def add_line(self, line_number, raw_data):
		self.content.append(LineOfCode(line_number, raw_data))

	def __str__(self):
		ret = self.header
		for line in self.content:
			ret += str(line) + '\n'
		return ret + self.footer

class LineOfCode():
	def __init__(self, line_number, raw_data):
		self.line_number = line_number
		self.raw_data = raw_data

	def __str__(self):
		ret = "<tr class=\"table_entry\">\n"
		ret += "\t<td class=\"line_number\">\n\t\t" +\
				'<div><button class="comment_button" type="submit""><i class="far fa-comment bubble"></i></button></div>\n\t\t'  +\
				'<div><button class="comment_button markup" type="submit" onclick="mark(this)"><i class="fas fa-map-marker-alt marker"></i></button></div>\n\t\t'  +\
				'<div>' + str(self.line_number) + "</div>\n" +\
				"\t</td>\n";

		ret += "\t<td class=\"line_of_code\">\n\t\t" + self.raw_data + "\n\t</td>\n"
		ret += "</tr>"
		return ret


lex = lexers.get_lexer_by_name("python")
formatter = HtmlFormatter(style='xcode')

with open('code_to_display.py', 'r') as code_to_display:
	raw_code = code_to_display.read()
	raw_html = highlight(raw_code, lex, formatter)
	raw_lines = raw_html.split('\n')

	with open("header.html", "r") as header:
		with open("footer.html", "r") as footer:
			code = Code(header.read(), footer.read())

	line_number = 1
	for raw_data in raw_lines[0:len(raw_lines) - 2]:
		if line_number == 1:
			raw_data = raw_data[raw_data.find("<span ") : len(raw_data)]
		code.add_line(line_number, raw_data)
		line_number += 1

	with open("colored_code.html", "w") as colored_code:
		colored_code.write(str(code))
	
with open("style.css", "w") as f:
	with open("base_style.css", "r") as base:
		f.write(base.read())
		f.write(formatter.get_style_defs())


















