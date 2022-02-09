import json

def mycount(a):
	ans = []
	last = a[0]
	count = 0
	if last == "wvr":
		ans = [0,0,0]
	for i,v in enumerate(a):
		if v != last:
			ans.append(count)
			last = v
			count = 1
		else:
			count += 1
	ans.append(count)
	return ans

def byphase(filename, ids):
	f = open(filename,"r")
	out = open("stackinput.json","w")
	ans = []
	doutput = json.load(f)
	# 1, whs, whs, ...
	for i in doutput:
		if i in ids:
			ans.append(mycount(doutput[i][:20]))
	# trim shape	
	# duration 1, duration 2, ..., duration 8
	for i in ans:
		if len(i) > 8:
			i = i[:8]
		while len(i) < 8:
			i.append(0)
	# transpose
	ansT = []
	ansJson = {}
	for i in range(8):
		temp = []
		for j in ans:
			temp.append(j[i])
		ansT.append(temp)
		ansJson[i] = temp
	json.dump(ansJson,out)
	return ansT


def getplt(ans, ids):
	import pandas as pd
	import matplotlib.pyplot as plt
	df = pd.DataFrame({'p1':ans[0],'p2':ans[1],'p3':ans[2],'p4':ans[3],'p1+':ans[4],'p2+':ans[5],'p3+':ans[6],'p4+':ans[7]},index = ids)
	ax = df.plot.barh(stacked=True, color = {'p1':"blue","p2":"orange","p3":"green","p4":"red",'p1+':"blue","p2+":"orange","p3+":"green","p4+":"red"});

	# ax.figure.set_size_inches(6,6)
	# ax.set_title("My ax title")

	# ax.legend(loc='upper right')
	plt.show()

ids = ["0","3","6","13"]
ans = byphase("01191619CTMoutput.json", ids)
getplt(ans, ids)