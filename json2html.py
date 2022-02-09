# -*- coding: UTF-8 -*-
def createhtml(filename, ids):
	import json
	f = open(filename, "r")
	jsondata = json.load(f)
	filename = filename.split(".")[0]
	fout = open(filename + ".html", "a", encoding='utf-8')
	colorset = {"whs":"Cyan", "whr":"LightBlue", "wvs":"#1589FF", "wvr":"#357EC7"}
	dirset = {"whs":"⇄","whr":"","wvs":"⇅","wvr":""}
	# fout.write("<html><body><table cellspacing=\"0\">\n")
	fout.write("<html><body><table>\n")
	fout.write("<tr><td></td>")
	for i in range(40):
		fout.write("<td style=\"width:20px;\" align=\"center\">" + str(i) + "</td>")
		# fout.write("<td align=\"center\">" + str(i) + "</td>")
	for i in ids:
		fout.write("<tr><td>" + i + "</td>")
		for phase in jsondata[i]:
			fout.write("<td bgcolor=" + colorset[phase] + " align=\"center\">"+ dirset[phase] +"</td>")
		fout.write("</tr>\n")
	fout.write("</table></body></html>")



# ids = [str(i) for i in range(17)]
ids = ["1","4","8","14"]
#ids = ["6","7","8","9","10"]
ans = createhtml("01191619CTMoutput.json", ids)
	