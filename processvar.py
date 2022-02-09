from collections import defaultdict


# csv variables
def step1(file, target_cell):
	d = defaultdict(dict)
	f=open(file,"r")
	fo=open("out.csv","a")
	# m102_9 50
	fo.write("var,number,time,value\n")
	for line in f:
		line = line.strip("\n")
		var = line[0]
		# [m102_9, 50]
		line = line.split(" ")
		value = line[1]
		# [m102, 9]
		line = line[0].split("_")
		number = line[0][1:]
		if number in target_cell and var in ["n","y"]:
			time = line[1]
			out = var+","+number+","+time+","+value+"\n"
			fo.write(out)

# csv variables
def output(file):
	d = defaultdict(dict)
	f=open(file,"r")
	fo=open("output.csv","a")
	# m102_9 50
	fo.write("var,number,time,value\n")
	# X1,0,0
	for line in f:
		line = line.strip("\n")
		var = line[0]
		line = line.split(",")
		# [X1, 0, 0]
		time = line[1]
		value = line[2]
		number = line[0][1:]
		if var == "X":
			time = line[1]
			out = var+","+number+","+time+","+str(int(value) % 4)+"\n"
			fo.write(out)

# number visualization
def step2(file):
	f=open(file,"r")
	fo=open("out2.csv","a")
	# m102_9 50
	dic = {}
	sig = ["e" for i in range(40)]
	for line in f:
		line = line.strip("\n")
		var = line[0]
		if var == "n": 
			# [m102_9, 50]
			line = line.split(" ")
			value = line[1].strip("-")
			# [m102, 9]
			line = line[0].split("_")
			number = line[0][1:]
			time = int(line[1])
			if number not in dic:
				dic[number] = [-1 for i in range(40)]
			dic[number][time] = value
		if var == "w":
			# [whs0_38,0]
			line = line.split(" ")
			value = str(line[1].strip("-"))
			# [whs0,38]
			line = line[0].split("_")
			number = line[0][1:3]
			time = int(line[1])
			if value == "1":
				sig[time] = number
	for i in range(40):
		out = dic["101"][i]+","+dic["102"][i]+","+dic["103"][i]+","+sig[i]+","+dic["104"][i]+","+dic["105"][i]+"||"
		out += dic["301"][i]+","+dic["302"][i]+","+dic["303"][i]+","+sig[i]+","+dic["304"][i]+","+dic["305"][i] + "\n"
		out += dic["205"][i]+","+dic["204"][i]+","+sig[i]+","+dic["203"][i]+","+dic["202"][i]+","+dic["201"][i]+"||"
		out += dic["405"][i]+","+dic["404"][i]+","+sig[i]+","+dic["403"][i]+","+dic["402"][i]+","+dic["401"][i]+"\n"
		fo.write(out)
		fo.write("========\n")

# KPI visualization 
def step3(file, inter_cell, des_cell, alltime):
	f=open(file,"r")
	fo=open("out3.csv","a")
	# m102_9 50
	des_y = [0 for i in range(alltime)]
	int_y = [0 for i in range(alltime)]
	int_n = [0 for i in range(alltime)]
	fo.write("des_y,int_y,int_n\n")
	for line in f:
		line = line.strip("\n")
		var = line[0]
		# [m102_9, 50]
		line = line.split(" ")
		value = int(float(line[1]))
		# [m102, 9]
		line = line[0].split("_")
		number = line[0][1:]
		time = int(line[1])
		if var == "y" and number in inter_cell:
			int_y[time] += value
		if var == "n" and number in inter_cell:
			int_n[time] += value
		if var == "y" and number in des_cell:
			des_y[time] += value
	for i in range(alltime):
		out = str(des_y[i])+","+str(int_y[i])+","+str(int_n[i])+"\n"
		fo.write(out)


def step4(file):
	f=open(file,"r")
	fo=open("out4.csv","a")
	# m102_9 50
	int_n = [[0,0,0,0] for i in range(40)]
	sig = [0 for i in range(40)]
	for line in f:
		line = line.strip("\n")
		var = line[0]
		if var == "w":
			# [whs0_38,0]
			line = line.split(" ")
			value = str(line[1].strip("-"))
			# [whs0,38]
			line = line[0].split("_")
			number = line[0][1:3]
			time = int(line[1])
			if value == "1":
				sig[time] = number
			continue
		# [m102_9, 50]
		line = line.split(" ")
		value = int(float(line[1]))
		# [m102, 9]
		line = line[0].split("_")
		number = line[0][1:]
		time = int(line[1])
		if var == "n" and number == "103":
			int_n[time][0] += value
		if var == "n" and number == "203":
			int_n[time][1] += value
		if var == "n" and number == "303":
			int_n[time][2] += value
		if var == "n" and number == "403":
			int_n[time][3] += value
	for t in range(40):
		out = str(int_n[t][0])+","+str(int_n[t][1])+","+str(int_n[t][2])+","+str(int_n[t][3])+","+str(sig[t])+"\n"
		fo.write(out)



inter_cell = [103,203,303,403,113,213,313,413,123,223,323,423,133,233,333,433,143,243,343,443]
inter_cell = [str(x) for x in inter_cell]
des_cell = [205,305,405,315,415,325,425,335,435,345,445,145]
des_cell = [str(x) for x in des_cell]
# step1("10060215CTMlog.txt", inter_cell)
output("10121704CTMlog.txt")