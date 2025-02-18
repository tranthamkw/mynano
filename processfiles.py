import os
import sys
import re


pathname=sys.argv[1]


myfiles = os.listdir(pathname)

pattern = "Raw"
newfilename=""
print(len(myfiles))

for i in range(len(myfiles)):
	if re.match(pattern,myfiles[i]):
		newfilename=os.path.join(pathname,myfiles[i])
		print(newfilename)



#print(myfiles)
os._exit(0)
