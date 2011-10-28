#!/usr/bin/env python

##
## produce data for the rider types by gender graphs
##

import csv
import numpy
import sys
import types
from util import ZeroDict


reader = csv.reader(open('sanitized-data.csv','r'))
titles = reader.next()                  # headers

genders = {'male': ZeroDict(),
           'female': ZeroDict()}

for line in reader:
    gender = line[2].strip().lower()
    if gender not in ['male', 'female']:
        continue
    ridertype = line[1].strip().lower()
    rt = genders[gender]
    rt[ridertype] += 1
    
f = open("genderridertypes.gp", 'w')
print genders
keys = genders['male'].keys()
keys.sort()
f.write('# gender %s\n' % ' '.join(keys))

def nicekey(s):
    return s[:1].upper() + s[1:]

for gender in genders.keys():
    f.write(nicekey(gender) + ' ')
    for k in keys:
        f.write(' %d' % genders[gender][k])
    f.write('\n')
f.close()

f = open('ridergendertypes.gp', 'w')
f.write('# type male female\n')
for k in keys:
    f.write(nicekey(k) + ' ')
    for g in ['male', 'female']:
        num = genders[g][k]
        f.write(str(num) + ' ')
    f.write('\n')
f.close()
