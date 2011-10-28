#!/usr/bin/env python

##
## create gnuplot data for the "roads" questions
##
## for each of the four questions, a data file is produced
##
## this data file has a row for each road and a column for each rider
## type with the totals for that ridertype; this is used to make a
## stacked bar chart so one can see how many of each rider-type
## selected that road.

import csv
import numpy
import sys
from util import ZeroDict

reader = csv.reader(open('sanitized-data.csv','r'))
titles = reader.next()

## this is the index into the data of which roads we're interested in

titles = {3: 'North of CPR, east/west routes',
          4: 'North of CPR, north/south routes',
          5: 'South of CPR, east/west routes',
          6: 'South of CPR, north/south routes'}
fnames = {3: 'roads_north_east.gp',
          4: 'roads_north_north.gp',
          5: 'roads_south_east.gp',
          6: 'roads_south_north.gp'}

## this minor magic works as so: ZeroDict (see util.py) takes an
## optional creator method to create the "zero" value, and uses that
## for any unknown key. So each of the dicts in here will create a
## sub-dict. The top-level key (3,4,5,6) is the row index. The next
## key is the road name, the final key is the rider type (with values
## of counts).

by_idx = {3: ZeroDict(lambda: ZeroDict()),
          4: ZeroDict(lambda: ZeroDict()),
          5: ZeroDict(lambda: ZeroDict()),
          6: ZeroDict(lambda: ZeroDict())}

def mapRoad(road):
    road = road.strip().lower()
    if '8th avenue' in road:
        road = '8th avenue'
    return road

for line in reader:
    ridertype = line[1].strip().lower()

    for index in [3,4,5,6]:
        for road in line[index].split(','):
            if road.strip() == '':
                continue
            road = mapRoad(road)
            by_idx[index][road][ridertype] += 1

## gnuplot uses space-separated names, so we just quote them which
## seems to work fine
def niceroad(road):
    return '"%s"'%road[:13]
    
def output(f, data):
    keys = []
    for h in data.keys():
        if not h in keys:
            keys.append(h)

    ## we sort the data by the count of confident cyclists for that
    ## road.
    def itemsorter(a, b):
        return cmp(a[1]['confident'], b[1]['confident'])
    items = data.items()
    items.sort(itemsorter)
    items.reverse()

    ## now we just write it out, with the columns in well-known order
    cols = ['confident', 'fearless', 'interested', 'reluctant']
    f.write("## roadname " + ' '.join(cols) + '\n')
    for (k, v) in items:
        f.write(niceroad(k) + ' ')
        for c in cols:
            f.write(str(v[c])+' ')
        f.write('\n')

for (k, v) in fnames.items():
    output(open(v, 'w'), by_idx[k])

