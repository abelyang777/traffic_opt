from collections import defaultdict
import json

def passthrough(file):
	f = open(file,"r")
	d = defaultdict(lambda: 0)
	for line in f:
		# line = [y0_n_1_des_0,11.94]
		line = line.strip("\n").split(",")
		# varname = [y0,n,1,des,0]
		varname = line[0].split("_")
		time = int(varname[-1])
		ctype = varname[-2]
		if ctype == "des" and varname[0][0] == "y":
			d[time] += float(line[1])
	return d

def pthroughintsec(file):
	f = open(file,"r")
	d = defaultdict(lambda: 0)
	for line in f:
		# y0_e_0_0l_4,5
		line = line.strip("\n").split(",")
		varname = line[0].split("_")
		time = int(varname[-1])
		if varname[0][0] == "y":
			if varname[2] =="0" and varname[3] == "0":
				d[time] += float(line[1])
	return d

def queue(file):
	f = open(file,"r")
	d = defaultdict(lambda: 0)
	for line in f:
		# y0_e_0_0l_4,5
		line = line.strip("\n").split(",")
		varname = line[0].split("_")
		time = int(varname[-1])
		if varname[0][0] == "n":
			if varname[2] =="0" and varname[3] == "0":
				d[time] += float(line[1])
		if varname[0][0] == "y":
			if varname[2] =="0" and varname[3] == "0":
				d[time] -= float(line[1])
	return d

def allN(file):
	f = open(file, "r")
	d = defaultdict(lambda: 0)
	for line in f:
		# y0_e_0_0l_4,5
		line = line.strip("\n").split(",")
		varname = line[0].split("_")
		time = int(varname[-1])
		if varname[0][0] == "n":
			d[time] += float(line[1])
	return d

def findcell(cid, cells):
	for c in cells:
		if c["id"] == cid:
			return c
	return None

def findintsec(iid, intsecs):
	for i in intsecs:
		if i["id"] == iid:
			return i
	return None

def greencells(output, intsecs):
	fout = open(output, "r")
	dout = json.load(fout)
	res = defaultdict(list)
	for i in sorted(dout.keys()):
		intsec = findintsec(i, intsecs)
		for time, sig in enumerate(dout[i]):
			if sig == "whs":
				res[time] += [cid + "s" for cid in intsec["cellh"]]
				res[time] += [cid + "l" for cid in intsec["cellh"]]
			if sig == "whr":
				res[time] += [cid + "r" for cid in intsec["cellv"]]
			if sig == "wvs":
				res[time] += [cid + "s" for cid in intsec["cellv"]]
				res[time] += [cid + "l" for cid in intsec["cellv"]]
			if sig == "wvr":
				res[time] += [cid + "r" for cid in intsec["cellv"]]
	return res

def greenusage(log, gcell, cells):
	f = open(log, "r")
	d = defaultdict(lambda: [0,0])
	for line in f:
		# y0_e_0_0l_19,0
		line = line.strip("\n").split(",")
		varname = line[0].split("_")
		if len(varname) == 5 and varname[0][0] == "y":
			time = int(varname[-1])
			cid = "_".join([varname[0], varname[1], varname[2], varname[3]])
			cid = cid[1:]
			if cid in gcell[time]:
				d[time][0] += float(line[1])
				cap = findcell(cid, cells)["lane"] * 5
				d[time][1] += cap
	return d

def wastedgreen(log, gcell):
	f = open(log, "r")
	d = defaultdict(lambda: 0)
	for line in f:
		# y0_e_0_0l_19,0
		line = line.strip("\n").split(",")
		varname = line[0].split("_")
		if len(varname) == 5 and varname[0][0] == "y":
			time = int(varname[-1])
			cid = "_".join([varname[0], varname[1], varname[2], varname[3]])
			cid = cid[1:]
			if cid in gcell[time]:
				if float(line[1]) < 1:
					d[time] += 1
	return d

def celllist():
	f = open("cells.json", "r")
	cells = json.load(f)
	return cells

def intseclist():
	f = open("intsec.json", "r")
	intsecs = json.load(f)
	return intsecs

'''cells = celllist()
intsecs = intseclist()
gcell = greencells(output, intsecs)'''



def createmetrics(file):
	log = file + ".txt"
	output = file + ".json"

	cells = celllist()
	intsecs = intseclist()
	gcell = greencells(output, intsecs)
	
	dpass = passthrough(log)
	dqueue = queue(log)
	dalln = allN(log)
	gusage = greenusage(log, gcell, cells)
	wastedg = wastedgreen(log, gcell)
	pti = pthroughintsec(log)

	metrics = [dpass, dqueue, dalln, gusage, wastedg, pti]
	return metrics


def createcsv(i):
	f = open(i + ".csv", "a")
	sumpass = 0
	title = "pass through, queue/16, all vehicle, all left, green usage, wasted green, intersection volume/16,"
	title += "pass through(opt), queue/16(opt), all vehicle(opt), all left(opt), green usage(opt), wasted green(opt), intersection volume/16(opt)\n"
	f.write(title)
	mc8 = createmetrics("c8_" + i)
	mc10 = createmetrics("c10_" + i)
	sumpass1, sumpass2 = 0, 0
	for i in range(40):
		sumpass1 += mc8[0][i]
		sumpass2 += mc10[0][i]
		line = str(mc8[0][i]) + "," + str(mc8[1][i]/16) + "," + str(mc8[2][i]) + "," + str(sumpass1) + "," + str(mc8[3][i][0] * 100 / mc8[3][i][1]) + "," + str(mc8[4][i]) + "," + str(mc8[5][i]/16) + ","
		line += str(mc10[0][i]) + "," + str(mc10[1][i]/16) + "," + str(mc10[2][i]) + "," + str(sumpass2) + "," + str(mc10[3][i][0] * 100 / mc10[3][i][1]) + "," + str(mc10[4][i]) + "," + str(mc10[5][i]/16) + "\n"
		f.write(line)




for i in ["1","2","3"]:
	createcsv(i)