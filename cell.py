from gurobipy import GRB, quicksum

class cell(object):
	def __init__(self, cid, lane, model, TIME):
		m = model
		self.id = str(cid)
		self.type = None
		self.cap = 5 * lane
		self.jam = 20 * lane
		self.lane = lane # dummy value
		self.n = {} # number of vehicles in cell i at time t
		self.n_free = {} # number of space in cell i at time t
		self.y = {} # number of vehicles leaving cell i at time t
		self.TIME = TIME
		for t in range(0, self.TIME):
			self.y[t] = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name="y" + str(cid) + "_" + str(t))
			self.n[t] = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name="n" + str(cid) + "_" + str(t))
			self.n_free[t] = m.addVar(lb=0, vtype=GRB.CONTINUOUS, name="m" + str(cid) + "_" + str(t))
		# m.addConstr(self.y[0] == 0)
		# m.addConstr(self.n[0] == 0)
		self.upstream = []
		self.downstream = []
	def getUpstream(self):
		out = ""
		for c in self.upstream:
			out += str(c.id) + " "
		return out.strip()
	def getDownstream(self):
		out = ""
		for c in self.downstream:
			out += str(c.id) + " "
		return out.strip()
	def getUpstreamY(self, t):
		return quicksum(i.y[t] for i in self.upstream)
