from cell import cell
from intersection import intersection
from gurobipy import GRB

class cellnetwork(object):
	def __init__(self, TIME):
		self.ordinaryCell = []
		self.originCell = []
		self.destinationCell = []
		self.intersectionCell = []
		self.virtualCell = []
		self.all = []
		self.intersection = []
		self.TIME = TIME
	def newOrdinaryCell(self, cid, lane, model):
		c = cell(cid, lane, model, self.TIME)
		c.type = "ordinary"
		self.ordinaryCell.append(c)
		self.all.append(c)
		return c
	def newOriginCell(self, cid, lane, model, D):
		c = cell(cid, lane, model, self.TIME)
		c.type = "origin"
		# to avoid too full
		c.jam = lane * 1000
		c.D = D # new vehicles generated here
		c.upstream = None
		self.originCell.append(c)
		self.all.append(c)
		return c
	def newDestinationCell(self, cid, lane, model):
		c = cell(cid, lane, model, self.TIME)
		c.type = "destination"
		c.downstream = None
		self.destinationCell.append(c)
		self.all.append(c)
		return c
	def newVirtualCell(self, cid, lane, model):
		c = cell(cid, lane, model, self.TIME)
		c.type = "virtual"
		# debug
		c.jam = lane * 1000
		c.q = {} # actual capacity
		for t in range(self.TIME):
			c.q[t] = model.addVar(lb=0, vtype=GRB.CONTINUOUS, name="q" + str(c.id) + "_" + str(t))
		self.virtualCell.append(c)
		self.all.append(c)
		return c
	def newIntersectionCell(self, cid, lanewidth, model):
		# lanewidth = [1,2,1,3] left, straight, right, special
		c = cell(cid, 10, model, self.TIME)
		c.type = "intersection"
		c.virtualCell = []
		for index, dirction in enumerate(["l","s","r","u"]):
			vc = self.newVirtualCell(c.id + dirction, lanewidth[index], model)
			c.virtualCell.append(vc)
		self.intersectionCell.append(c)
		self.all.append(c)
		return c
	def newIntersection(self, iid, model, cellh, cellv):
		itsc = intersection(iid, model, self.TIME)
		itsc.cellh = cellh
		itsc.cellv = cellv
		self.intersection.append(itsc)
		return itsc
	def sampleIntersection(self, iid, itype, lanewidths, model):
		# lanewidth:{"n": [1,2,1,3],"s": [1,2,1,3],"w": [1,2,1,3],"e": [1,2,1,3]}
		config_dict = {"I":"sample_I.csv", "N": "sample_N.csv",	"S": "sample_S.csv", \
						"E": "sample_E.csv", "W": "sample_W.csv"}
		f = open(config_dict[itype], "r")
		lines = []
		# create cells
		for line in f:
			line = line.strip("\n").split(",")
			lines.append(line)
			direction = line[0][0]
			if line[1] == "ordinary":
				self.newOrdinaryCell(iid + "_" + line[0], lanewidths[direction][-1], model)
			if line[1] == "intersectionCell":
				self.newIntersectionCell(iid + "_" + line[0], lanewidths[direction], model)
		# create links
		for line in lines:
			c = self.findCell(iid + "_" + line[0])
			if line[2] == "external":
				c.upstream = None
			else:
				for i in line[2].split(" "):
					c.upstream.append(self.findCell(iid + "_" + i))
			if line[3] == "external":
				c.downstream = None
			else:
				for i in line[3].split(" "):
					c.downstream.append(self.findCell(iid + "_" + i))
		cellv, cellh = [], []
		if itype != "N":
			cellv.append(self.findCell(iid + "_n_0_0"))
		if itype != "S":
			cellv.append(self.findCell(iid + "_s_0_0"))
		if itype != "E":
			cellh.append(self.findCell(iid + "_e_0_0"))
		if itype != "W":
			cellh.append(self.findCell(iid + "_w_0_0"))
		itsc = self.newIntersection(iid, model, cellh, cellv)
		return itsc
	def findCell(self, cid):
		# print("find:"+str(cid))
		if cid == None:
			return None
		for c in self.all:
			if str(c.id) == str(cid):
				return c
		print("can't find cell:" + cid)
	def findIntersection(self, iid):
		if iid == None:
			return None
		for i in self.intersection:
			if str(iid) == str(i.id):
				return i
		print("can't find intersection:" + iid)
	def showNetwork(self):
		for c in self.all:
			if c.type == "origin":
				print(str(c.id)+" to "+c.getDownstream())
			elif c.type == "destination":
				print(str(c.id)+" from "+c.getUpstream())
			elif c.type == "ordinary":
				print(str(c.id)+" from "+c.getUpstream()+" to "+c.getDownstream())
		for i in self.intersection:
			ch = ""
			for c in (i.cellh + i.cellv):
				ch += c.id + " "
			print(i.id + ":" + ch)
	def showcell(self):
		for c in self.all:
			print(c.id)
	# read links.csv to create cells
	def creatNetwork(self, links, model):
		m = model
		# ID[0], type[1], upstream[2], downstream[3], lane[4], ratio[5]
		for line in links:
			ctype = line[1]
			c = None
			if ctype == "ordinary":
				c = self.newOrdinaryCell(line[0], m)
			if ctype == "origin":
				D = [0 for i in range(self.TIME)]
				c = self.newOriginCell(line[0], m, D)
			if ctype == "destination":
				c = self.newDestinationCell(line[0], m)
			if ctype == "intersectionCell":
				c = self.newIntersectionCell(line[0], m)
	def setRatio(self, ratio):
		for c in ratio:
			self.findCell(c[0]).ratio = c[1].split(" ")
	# read D.csv file to set up incoming traffic flow
	def setInflow(self, demand):
		for line in demand:
			cell = self.findCell(line[0])
			cell.jam = 2000
			cell.D = list(map(float, line[1:]))
	def setOffset(self, offset):
		f = open(offset, "r")
		for line in f:
			line = line.strip("\n").split(",")
			intersection = self.findIntersection(line[0])
			intersection.offset = float(line[1])