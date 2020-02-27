import re 

def latex_to_html(pat, sentence):
	pattern = re.compile(r'%s' %pat)
	matches = pattern.finditer(sentence)
	sd = ""
	size = 0
	if pat[2:8] == 'textbf':
		tag = 'b'
	elif pat[2:8] == 'textit':
		tag = 'i'
	else:
		tag = 'u'

	for match in matches:
		s, e = match.span()
		sd += sentence[size:s]
		size = e
		sd += r"<%s>%s</%s>" %(tag, match.group(1),tag)
	sd += sentence[size:]
	return r'%s'%sd
