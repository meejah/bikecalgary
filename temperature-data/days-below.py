#!/usr/bin/env python

import sys

if len(sys.argv) < 2:
    print "usage: %s temperature" % sys.argv[0]
    sys.exit(-2)
    
temp = int(sys.argv[1])

days = 0
for line in file('temperature-data-2010.txt','r').readlines()[1:]:
    foo, min, avg, max = line.split()
    min = float(min)
    if min < temp:
        days += 1


print days,"days below",temp

