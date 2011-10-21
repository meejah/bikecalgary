#!/usr/bin/env python

##
## this takes the raw data and produces other data tables out of it,
## including tables for the gnuplot-based graphs and for use in Excel
##


import csv
import numpy
import sys
import types
from util import ZeroDict


reader = csv.reader(open('sanitized-data.csv','r'))
titles = reader.next()                  # headers

rider_types = ZeroDict()
gender = ZeroDict()
ages = ZeroDict()
underpasses = ZeroDict()
underpasses_sep = ZeroDict()
cyclethrough = ZeroDict()
cycle_sunny = ZeroDict()
cycle_winter = ZeroDict()
walk = ZeroDict()
transit = ZeroDict()
drive = ZeroDict()
trip_end = ZeroDict()
trip_begin = ZeroDict()

def normalizeStreetName(s):
    return s.split('(')[0].strip()

for line in reader:
    ages[line[0]] += 1
    rider_types[line[1]] += 1
    gender[line[2]] += 1

    assert(len(line[7].strip()) == 0 or len(line[8].strip()) == 0)
    for street in line[7].split(','):
        if street.strip() == '':
            continue
        underpasses[normalizeStreetName(street)] += 1
    for street in line[8].split(','):
        if street.strip() == '':
            continue
        underpasses[normalizeStreetName(street)] += 1
    for street in line[10].split(','):
        if street.strip() == '':
            continue
        underpasses_sep[normalizeStreetName(street)] += 1

    ## basically if someone didn't answer all the last questions, the
    ## line is just short it seems.
    if len(line) > 11:
        cyclethrough[line[11]] += 1
    if len(line) > 12:
        cycle_sunny[line[12]] += 1
    if len(line) > 13:
        cycle_winter[line[13]] += 1
    if len(line) > 14:
        walk[line[14]] += 1
    if len(line) > 15:
        transit[line[15]] += 1
    if len(line) > 16:                  # why are we missing the drive question from some?
        drive[line[16]] += 1
    if len(line) > 17:
        trip_end[line[17]] += 1
    if len(line) > 18:
        trip_begin[line[18]] += 1
    
    
## output some gnuplot-able data files

def gp_output(f, table):
    """outputs data suitable for gnuplot"""
    keys = table.keys()
    keys.sort()
    f.write('# ' + ', '.join(keys) + '\n\n')
    for k in keys:
        if k == '':
            f.write('n/a')
        else:
            f.write(k)
        f.write(' '+str(table[k])+'\n')

def csv_output(f, table):
    """outputs CSV data, hopfully good for Excel"""

    keys = table.keys()
    keys.sort()
    writer = csv.writer(f)
    writer.writerow([f.name.split('.')[0], 'total'])

    for k in keys:
        nicekey = k
        if k == '':
            nicekey = 'n/a'
        writer.writerow([nicekey, table[k]])

for (name, data) in [('ages', ages),
                     ('ridertypes', rider_types),
                     ('gender', gender),
                     ('underpasses', underpasses),
                     ('underpasses-sep', underpasses_sep),
                     ('cycle-sunny',cycle_sunny),
                     ('cycle-winter',cycle_winter),
                     ('walk',walk),
                     ('drive',drive),
                     ('transit',transit),
                     ('trip_starts',trip_begin),
                     ('trip_dests',trip_end)                     
                     ]:
    gp_output(open('trans_'+name+'-gp', 'w'), data)
    csv_output(open('trans_'+name+'.csv', 'w'), data)
