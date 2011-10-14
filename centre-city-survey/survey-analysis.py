#!/usr/bin/env python


## analyzes the survey results for Centre City engagement stuff

import csv
import numpy
reader = csv.reader(open('sanitized-data.csv','r'))


titles = reader.next()

## for the routes questions, they are columns
## (so subtract 2 because we nuke 0, 1)
## 3: north of tracks, east/west
## 4: north of tracks, north/south
## 5: south of tracks, east/west
## 6: south of tracks, north/south

north_east = []
north_north = []
south_east = []
south_north = []

for line in reader:
    north_east.append(len(line[3].split(',')))
    north_north.append(len(line[4].split(',')))
    south_east.append(len(line[5].split(',')))
    south_north.append(len(line[6].split(',')))


print len(north_east),"total resposes"
print "statistics:                       median\taverage\t\tmax"
print "north of cpr, east-west routes:  ",numpy.median(north_east),"\t\t",numpy.average(north_east),"\t",numpy.amax(north_east)
print "north of cpr, north-south routes:",numpy.median(north_north),"\t\t",numpy.average(north_north),"\t",numpy.amax(north_north)
print "south of cpr, east-west routes:  ",numpy.median(south_east),"\t\t",numpy.average(south_east),"\t",numpy.amax(south_east)
print "south of cpr, north-south routes:",numpy.median(south_north),"\t\t",numpy.average(south_north),"\t",numpy.amax(south_north)
