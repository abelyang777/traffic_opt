from cellNetwork import cellnetwork
from intersection import intersection
from cell import cell
import json

def createNetwork(model, file, network):
	f = open(file,"r")
	network_json = json.load(f)
	# create cells in the intersections
	# need to modify the cap and jam based on lane number
	for i in network_json:
		itsc = cellNetwork.sampleIntersection(i["ID"], i["type"], model)
		for direction in ["n","s","e","w"]:
	# create cells outside interstions
	for i in network_json:
		# other intersection, external area, non-applicable
		for direction in ["n","s","e","w"]:
			current = network.findCell(i["ID"] + "_" + direction + "_0_0")
			if i["outreach"][direction] != []:
				# to external area
				if i["outreach"][direction][0] == "e":
					# origin cell
					D = [0 for i in range(network.TIME)] # dummy D
					origin = network.newOriginCell(i["ID"] + "_"+ direction + "_1_ori", model, D)
					current.upstream = [origin]
					origin.downstream = [current]
					# destination cell
					destination = network.newDestinationCell(i["ID"] + "_" + direction + "_1_des",model)
					ordcell = network.findCell(i["ID"] + "_" + direction + "_0_1")
					ordcell.downstream = [destination]
					destination.upstream = [ordcell]
				# to other intersection
				else:
					for disance in range(1, i["outreach"][direction][1] + 1):
						c = network.newOrdinaryCell(i["ID"] + "_" + direction + "_" + str(disance) + "_0")
						current.upstream = [c]
						c.downstream = [current]
						current = c
					target = network.findCell(i["outreach"][direction][0])
					current.upstream = [target]
					target.downstream = [current]
	return network