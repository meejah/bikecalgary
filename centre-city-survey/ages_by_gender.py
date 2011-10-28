#!/usr/bin/env python

##
## produce data for the ages graph with gender
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
    age = line[0].strip().lower()
    rt = genders[gender]
    rt[age] += 1
    
f = open("genderages.gp", 'w')
print genders
keys = genders['male'].keys()
keys.sort()
f.write('# gender %s\n' % ' '.join(keys))

for gender in genders.keys():
    f.write(gender + ' ')
    for k in keys:
        f.write(' %d' % genders[gender][k])
    f.write('\n')
f.close()


f = open('agegender.gp', 'w')
f.write('# type male female\n')
for k in keys:
    f.write(k + ' ')
    for g in ['male', 'female']:
        num = genders[g][k]
        f.write(str(num) + ' ')
    f.write('\n')
f.close()
