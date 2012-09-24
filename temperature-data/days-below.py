#!/usr/bin/env python

import sys

if len(sys.argv) < 2:
    print "usage: %s temperature" % sys.argv[0]
    sys.exit(-2)
    
temp = int(sys.argv[1])

maxdays = 0
mindays = 0
for line in file('temperature-data-2011.txt','r').readlines()[1:]:
    foo, min, avg, max = line.split()
    min = float(min)
    max = float(max)
    if max < temp:
        maxdays += 1
    if min < temp:
        mindays += 1


print maxdays,"days with High below",temp
print mindays,"days with Low below",temp

