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

def nicekey(k):
    if k == 'under 18':
        return '<18'
    return k

f = open('agegender.gp', 'w')
f.write('# type male female\n')

## "under 18" ends up last; make it first
keys.insert(0, keys[-1])
keys = keys[:-1]

## write data
for k in keys:
    f.write(nicekey(k) + ' ')
    for g in ['male', 'female']:
        num = genders[g][k]
        f.write(str(num) + ' ')
    f.write('\n')
f.close()
