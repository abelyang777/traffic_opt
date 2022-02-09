'''
from random import randint

a = {"a":1,"b":2,"c":3}
#j = json.dumps(a)
f = open("test.json","w")
json.dump(a,f)

d = []
for i in range(5):
	c = {str(i):i}
	d.append(c)
f = open("test.json","w")
json.dump(d,f)

f = open("network.json","r")
j = json.load(f)
for i in j:
	print(i["ID"])
'''
import json
f = open("01191337CTMoutput.json","r")
d = json.load(f)
print(d["4"])