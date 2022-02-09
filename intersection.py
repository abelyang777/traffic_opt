from gurobipy import GRB

class intersection(object):
	def __init__(self, iid, model, TIME):
		m = model
		self.id = str(iid)
		self.whs = {} # 4 phases
		self.whr = {}
		self.wvs = {}
		self.wvr = {}
		self.X = {}
		self.k = {}
		self.delta = {}
		self.TIME = TIME
		self.offset = 0 # TO DO
		for t in range(self.TIME):
			self.whs[t] = m.addVar(vtype= GRB.BINARY, name="whs" + str(iid) + "_" + str(t)) # straight and left signal variable horizontal direction 
			self.whr[t] = m.addVar(vtype=GRB.BINARY, name="whr" + str(iid) + "_" + str(t)) # right signal
			self.wvs[t] = m.addVar(vtype=GRB.BINARY, name="wvs" + str(iid) + "_" + str(t))
			self.wvr[t] = m.addVar(vtype=GRB.BINARY, name="wvr" + str(iid) + "_" + str(t))
			self.X[t] = m.addVar(lb=0, vtype=GRB.INTEGER, name="X" + str(iid) + "_" + str(t))
			self.k[t] = m.addVar(lb=0, vtype=GRB.INTEGER, name="k" + str(iid) + "_" + str(t))
			# if signal change at time t
			self.delta[t] = m.addVar(vtype=GRB.BINARY, name="delta" + str(iid) + "_" + str(t))
		self.cellh = []
		self.cellv = []
		self.north = []
		self.south = []
		self.east = []
		self.west =[]