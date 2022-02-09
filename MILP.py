from gurobipy import *
from datetime import datetime
from cellNetwork import cellnetwork
from intersection import intersection
from cell import cell
import json
from random import randint

Wave = 1

# constraints to describe the CTM
def createConstraints(model, network):
	m = model
	# Set objective
	Totalflow = 0
	Totalqueue = 0
	for c in network.destinationCell:
		for t in range(1, TIME -1):
			Totalflow += c.y[t]
	for c in network.intersectionCell:
		for t in range(1, TIME -1):
			Totalqueue += c.n[t]
	m.setObjective(Totalflow, GRB.MAXIMIZE) 
	# m.setObjective(Totalqueue, GRB.MINIMIZE)
	# cell constraints
	for t in range(0, TIME - 1):
		for c in network.all:
			m.addConstr(c.n_free[t] == (c.jam - c.n[t]) * Wave)
			if c.type == "ordinary":
				m.addConstr(c.y[t] == min_(c.n[t], c.downstream[0].n_free[t], c.cap))
				m.addConstr(c.n[t + 1] == c.n[t] + c.getUpstreamY(t) - c.y[t])
				continue
			if c.type == "origin":
				m.addConstr(c.y[t] == min_(c.n[t], c.downstream[0].n_free[t], c.cap))
				m.addConstr(c.n[t + 1] == c.n[t] + c.D[t] - c.y[t])
				continue
			if c.type == "destination":
				m.addConstr(c.y[t] == c.n[t])
				m.addConstr(c.n[t + 1] == c.getUpstreamY(t))
			if c.type == "intersection":
				m.addConstr(c.n[t] == quicksum(vc.n[t] for vc in c.virtualCell))
				m.addConstr(c.y[t] == quicksum(vc.y[t] for vc in c.virtualCell))
				for vc, ra in zip(c.virtualCell, c.ratio):
					# m.addConstr(vc.y[t] == min_(vc.n[t], vc.downstream[0].n_free[t], vc.q[t]))
					m.addConstr(vc.y[t] == min_(vc.n[t], vc.q[t]))
					m.addConstr(vc.n[t + 1] == vc.n[t] - vc.y[t] + c.getUpstreamY(t) * ra)
	for x in network.intersection:
		for t in range(0, TIME):
			if t != TIME - 1:
				m.addConstr(x.X[t + 1] == x.X[t] + x.delta[t])
				# minimum duration == 2
				m.addConstr(x.delta[t] + x.delta[t + 1] <= 1)
			m.addConstr(2 * x.whs[t] + 3 * x.whr[t] + 4 * x.wvs[t] + 5 * x.wvr[t] - 2 == x.X[t] - 4 * x.k[t])
			m.addConstr(x.whs[t] + x.whr[t] + x.wvs[t] + x.wvr[t] == 1)
			for c1 in x.cellh:
				m.addConstr(c1.virtualCell[0].q[t] == x.whr[t] * c1.virtualCell[0].cap)
				m.addConstr(c1.virtualCell[1].q[t] == x.whs[t] * c1.virtualCell[1].cap)
				m.addConstr(c1.virtualCell[2].q[t] == c1.virtualCell[2].cap)
				m.addConstr(c1.virtualCell[3].q[t] == c1.virtualCell[3].cap)
			for c2 in x.cellv:
				m.addConstr(c2.virtualCell[0].q[t] == x.wvr[t] * c2.virtualCell[0].cap)
				m.addConstr(c2.virtualCell[1].q[t] == x.wvs[t] * c2.virtualCell[1].cap)
				m.addConstr(c2.virtualCell[2].q[t] == c2.virtualCell[2].cap)
				m.addConstr(c2.virtualCell[3].q[t] == c2.virtualCell[3].cap)
		cycleT = 10
		cycleN = TIME//cycleT
		for t in range(1, cycleN):
			# offset by time
			m.addConstr(x.whs[(t - 1) * cycleT + x.offset] == 1)
			m.addConstr(x.wvr[(t - 1) * cycleT + cycleT - 1 + x.offset] == 1)
			m.addConstr(quicksum(x.delta[tt] for tt in range(cycleT * t, (t + 1) * cycleT)) == 4)
		# m.addConstr(x.wvr[TIME - 1] == 1)
	return m

# read n from txt file
def readinitialN(file):
	f = open(file,"r")
	n = {}
	for line in f:
		# n101_39 8
		line = line[1:].split(" ")
		name = line[0].split("_")[0]
		value = int(line[1])
		n[name] = value
	return n

# set initial value
def initialN(model, network, fn):
	if fn == None:
		for c in network.all:
			model.addConstr(c.n[0] == 0)
	else:
		for c in fn:
			oc = network.findCell(c)
			model.addConstr(oc.n[0] == fn[c])
	return model

def initialX(model, network, fx):
	if fx == None:
		for i in network.intersection:
			model.addConstr(i.X[0] == 0)
	else:
		for i in fx:
			oi = network.findIntersection(i)
			model.addConstr(oi.X[0] == fx[i] + 1)
	return model

def saveLastN(model, network, TIME):
	fn = {}
	for c in network.all:
		fn[c.id] = c.n[TIME - 2].x
	return fn

def saveLastX(model, network, TIME):
	fx = {}
	for i in network.intersection:
		fx[i.id] = i.X[TIME - 1].x % 4
	return fx

def saveLog(model):
	now = datetime.now()
	current_time = now.strftime("%m%d%H%M")
	f = open(current_time + "CTMlog.txt", "a")
	for v in model.getVars():
		# y0_n_0_0_0 0
		f.write('%s,%g\n' % (v.varName, v.x))

def saveoutput(model, network, TIME):
	now = datetime.now()
	current_time = now.strftime("%m%d%H%M")
	out = {}
	f = open(current_time + "CTMoutput.json", "w")
	for i in network.intersection:
		temp = ["Na" for signal in range(TIME)]
		for index in range(TIME):
			if i.whs[index].x > 0.9:
				temp[index] = "whs"
			elif i.whr[index].x > 0.9:
				temp[index] = "whr"
			elif i.wvs[index].x > 0.9:
				temp[index] = "wvs"
			elif i.wvr[index].x > 0.9:
				temp[index] = "wvr"
		out[i.id] = temp
	json.dump(out, f)
	return saveoutput

def createNetwork(model, file, network):
	f = open(file,"r")
	network_json = json.load(f)
	# create cells in the intersections
	for i in network_json:
		itsc = network.sampleIntersection(i["ID"], i["type"], i["lanewidth"], model)
	# create cells outside interstions
	for i in network_json:
		# other intersection, external area, non-applicable
		for direction in ["n","s","e","w"]:
			if i["outreach"][direction] != []:
				current = network.findCell(i["ID"] + "_" + direction + "_0_0")
				# to external area
				lanewidth = i["outreach"][direction][-1]
				if i["outreach"][direction][0] == "e":
					# origin cell
					D = [0 for i in range(network.TIME)] # dummy D
					origin = network.newOriginCell(i["ID"] + "_"+ direction + "_1_ori", lanewidth, model, D)
					current.upstream = [origin]
					origin.downstream = [current]
					# destination cell
					destination = network.newDestinationCell(i["ID"] + "_" + direction + "_1_des", lanewidth, model)
					ordcell = network.findCell(i["ID"] + "_" + direction + "_0_1")
					ordcell.downstream = [destination]
					destination.upstream = [ordcell]
				# to other intersection
				else:
					for disance in range(1, i["outreach"][direction][1] + 1):
						c = network.newOrdinaryCell(i["ID"] + "_" + direction + "_" + str(disance) + "_0", lanewidth, model)
						current.upstream = [c]
						c.downstream = [current]
						current = c
					target = network.findCell(i["outreach"][direction][0])
					current.upstream = [target]
					target.downstream = [current]
	return network

def createData(model, network_file, ratio, D, start, end):
	TIME = end - start
	network = cellnetwork(TIME) # create network
	# cells
	network = createNetwork(model, network_file, network)
	# ratio
	f = open(ratio, "r")
	ratio = []
	for line in f:
		line = line.strip("\n").split(",")
		if line[0] <= str(start) and line[1] >= str(end):
			ratio.append([line[2], line[3]])
	network.setRatio(ratio)
	# D
	f = open(D, "r")
	demand = []
	temp = []
	count = 0
	for line in f:
		if start < count < end or count == 0:
			line = line.strip("\n").split(",")
			temp.append(line)
		count += 1
	for col in range(len(temp[0])):
		demand.append([temp[row][col] for row in range(len(temp))])
	network.setInflow(demand)
	return network

start = 0
end = 40
TIME = end - start

m = Model("MILP") # create model
network = createData(m, "network.json", "turn_ratio.csv", "D.csv", start, end)

lastnfile = open("lastn.json","r")
lastn = json.load(lastnfile)

lastxfile = open("lastx.json","r")
lastx = json.load(lastxfile)

m = initialX(m, network, lastx)
m = initialN(m, network, lastn)

network.setOffset("offset.csv")

m = createConstraints(m, network) # set up constraints
m.Params.timeLimit = 180 # 30 seconds
m.Params.MIPfocus = 1 # focus on finding the solution, 3 focus on bound
m.Params.MIPGap = 0.1 # gap at 10%

try:
	m.optimize()
except GurobiError as e:
	print('Error code ' + str(e.errno) + ": " + str(e))

saveLog(m)
saveoutput(m, network, TIME)


'''
lastjson = open("lastx.json","w")
lastx = saveLastX(m, network, TIME)
json.dump(lastx, lastjson)


lastjson = open("lastn.json","w")
lastn = saveLastN(m, network, TIME)
json.dump(lastn, lastjson)
'''