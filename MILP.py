from gurobipy import *

CAP = 5
JAM = 20
TIME = 40
GMIN = 1
GMAX = 3
Wave = 0.5
# Create a new model
m = Model("MILP")

# cell structure
#       11        12
# 1 2 3(10) 4 5 6(13) 7
#        9        14
#        8        15

# create network
allCell = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
ordinaryCell = [2, 4, 5, 9, 14]
originCell = [1, 8, 12]
destinationCell = [7, 11, 15]
intersectionCell = [3, 10, 6, 13]
intersection = [(3, 10), (6, 13)]

# Create variables
y = {} # number of vehicles leaving cell i at time t
n = {} # number of vehicles in cell i at time t
n_free = {}  # number of space in cell i at time t
for i in allCell:
    for t in range(1, TIME + 1):
        y[i, t] = m.addVar(lb=0, ub=CAP, vtype=GRB.INTEGER, name="y" + str(i) + "_" + str(t))
        n[i, t] = m.addVar(lb=0, ub=JAM, vtype=GRB.INTEGER, name="n" + str(i) + "_" + str(t))
        n_free[i, t] = m.addVar(lb=0, ub=JAM, vtype=GRB.INTEGER, name="m" + str(i) + "_" + str(t))
# number of vehicles entering the origin cell
D = {}
for i in originCell:
    for t in range(1, TIME):
        if t > 30:
            D[i, t] = 0
            continue
        if i == 1 or i == 12:
            D[i, t] = 4
        else:
            D[i, t] = 1
# actual capacity for intersection cell i in time interval t
q = {}
for i in intersectionCell:
    for t in range(1, TIME + 1):
        q[i, t] = m.addVar(lb=0, vtype=GRB.INTEGER, name="q" + str(i) + "_" + str(t))
# 0–1 variables for switching traffic light at intersection (i,j)
w = {}
for x in intersection:
    for t in range(1, TIME + 1):
        w[x, t] = m.addVar(vtype=GRB.BINARY, name="w" + str(x) + "_" + str(t))

# Set objective
TotalDelay = 0
for i in allCell:
    for t in range(1, TIME + 1):
        TotalDelay += t * n[i, t]
m.setObjective(TotalDelay, GRB.MINIMIZE)

# cell constraints
for t in range(1, TIME):
    for i in allCell:
        m.addConstr(n_free[i, t] <= (JAM - n[i, t]) * 0.5 + 0.9)
        m.addConstr(n_free[i, t] >= (JAM - n[i, t]) * 0.5)
        if t == 1:
            m.addConstr(n[i, t] == 0)
            m.addConstr(y[i, t] == 0)
        if i in ordinaryCell:
            m.addConstr(y[i, t] == min_(n[i, t], n_free[i + 1, t], CAP))
            m.addConstr(n[i, t + 1] == n[i, t] + y[i - 1, t] - y[i, t])
            continue
        if i in originCell:
            m.addConstr(y[i, t] == min_(n[i, t], n_free[i + 1, t], CAP))
            m.addConstr(n[i, t + 1] == n[i, t] + D[i, t] - y[i, t])
            continue
        if i in destinationCell:
            m.addConstr(y[i, t] == n[i, t])
            m.addConstr(n[i, t + 1] == y[i - 1, t])

for x in intersection:
    i = x[0]
    j = x[1]
    for t in range(1, TIME):
        m.addConstr(y[i, t] == min_(n[i, t], n_free[i + 1, t], CAP, q[i, t]))
        m.addConstr(y[j, t] == min_(n[j, t], n_free[j + 1, t], CAP, q[j, t]))
        m.addConstr(n[i, t + 1] == n[i, t] + y[i - 1, t] - y[i, t])
        m.addConstr(n[j, t + 1] == n[j, t] + y[j - 1, t] - y[j, t])
        m.addConstr(q[i, t] == w[x, t] * CAP)
        m.addConstr(q[j, t] == (1 - w[x, t]) * CAP)

'''
# Minimum green
dummy = {}
dummy_sum = {}
for x in intersection:
    for t in range(2, TIME - GMIN):
        dummy_sum[x, t] = 0
        dummy[x, t] = m.addVar(vtype=GRB.INTEGER, name="v" + str(x) + "_" + str(t))
        m.addConstr(q[i, t] - q[i, t-1] <= dummy[x, t])
        m.addConstr(-q[i, t] + q[i, t - 1] <= dummy[x, t])
        for t2 in range(t, t + GMIN):
            dummy_sum[x, t] += dummy[x, t2]
        m.addConstr(dummy_sum[x, t] <= CAP)
'''
MaxGreen = True
# Maximum green
if MaxGreen:
    i_GMAX = {}
    j_GMAX = {}
    for x in intersection:
        for t in range(1, TIME - GMAX + 1):
            i = x[0]
            j = x[1]
            i_GMAX[x, t] = quicksum(q[i, t2] for t2 in range(t, t + GMAX + 1))
            j_GMAX[x, t] = quicksum(q[j, t2] for t2 in range(t, t + GMAX + 1))
            m.addConstr(i_GMAX[x, t] <= CAP * GMAX)
            m.addConstr(j_GMAX[x, t] <= CAP * GMAX)

FixedCyele = False
# fixed cycle length
CYCLE = 4
if FixedCyele:
    for x in intersection:
        for t in range(1, t - CYCLE):
            m.addConstr(q[i, t] - q[i, t + CYCLE] == 0)
            m.addConstr(q[j, t] - q[j, t + CYCLE] == 0)
# ensure flow conservation
try:
    m.Params.timeLimit = 60
    m.optimize()
except GurobiError as e:
    print('Error code ' + str(e.errno) + ": " + str(e))
f = open("var.txt", "a")
for v in m.getVars():
    f.write('%s %g\n' % (v.varName, v.x))
m.write("MILP.lp")
m.write("MILP.mps")
print('Obj: %g' % m.objVal)
