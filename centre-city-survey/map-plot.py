#!/usr/bin/env python

import os
import sys
import re
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import csv
import numpy

if False:
    ax = plt.axes()
    line = mlines.Line2D([0,1], [0,1], lw=5.0, alpha=0.4)
    ax.add_line(line)
    plt.show()
    sys.exit(0)

sys.path.insert(0, '/home/mike/src/osmgeocode')
import osm

osmmap = osm.OSM(open('centre-city.osm','r'))

def to_coords(nodes):
    rtn = []
    for n in nodes:
        n = osmmap.nodes[n]
        rtn.append( (n.lon, n.lat))
    return rtn

named_nodes = {}
named_ways = []
for w in osmmap.ways.values():
    if w.tags.has_key('name'):
        named_ways.append(w)
        continue
    
        k = w.tags['name']
        print k,w,w.nds
        if named_nodes.has_key(k):
            named_nodes[k] = named_nodes[k] + to_coords(w.nds)
        else:
            named_nodes[k] = to_coords(w.nds)


east_west_extent = (-114.04709 + 114.09567) + 0.001
north_south_extent = (51.05403 - 51.03727) + 0.001

reader = csv.reader(open('sanitized-data.csv','r'))
titles = reader.next()

ans = {}
north = {}
south = {}
index = 3
fearless_index = 1
fearless = 'fearless'

for line in reader:
    #    if line[fearless_index].lower() == fearless:
    #        continue

    for road in (line[3].split(',') + line[5].split(',')):
        road = road.strip().lower()
        if len(road) == 0:
            continue
        if '8th avenue' in road:
            road = '8 avenue'

        if ans.has_key(road):
            ans[road] += 1
        else:
            ans[road] = 1

    for road in line[4].split(','):# + line[6].split(',')):
        road = road.strip().lower()
        if len(road) == 0:
            continue
        if north.has_key(road):
            north[road] += 1
        else:
            north[road] = 1
        
    for road in line[6].split(','):
        road = road.strip().lower()
        if len(road) == 0:
            continue
        if south.has_key(road):
            south[road] += 1
        else:
            south[road] = 1
        

## normalize the road data to be from 0.0 to 1.0
## also make all the road names like OSM road tags seem to be ("8
## Avenue" not "8th Avenue")

name_re = re.compile('([0-9]*)[a-zA-Z]* (.*)')
max = numpy.max(ans.values())
min = numpy.min(ans.values())
delta = max - min
##print ans

def remap(k):
    m = name_re.match(k)
    if m is None:
        print 'BOOM',k
    newk = m.group(1) + ' ' + m.group(2).lower()
    if k in ['olympic way se']:
        newk = k
    elif k == 'centre street sw':
        newk = 'centre street s'
    elif k == 'riverfront avenue':
        newk = k + ' se'
    elif k == 'macleod trail se (has underpass)':
        newk = 'macleod trail se'
    else:
        words = newk.split()
        if len(words) < 3 or words[2] not in['nw','ne','sw','se']:
            words = words[:2]
            words.append('sw')
        else:
            words = words[:3]
        newk = ' '.join(words)
    print "turned",k,"into",newk
    return newk

roads = {}
for k in ans.keys():
    roads[remap(k)] = (ans[k] - min) / float(delta)
    
north_roads = {}
min = numpy.min(north.values())
delta = numpy.max(north.values()) - min
for k in north.keys():
    north_roads[remap(k)] = (north[k] - min) / float(delta)

south_roads = {}
min = numpy.min(south.values())
delta = numpy.max(south.values()) - min
for k in south.keys():
    south_roads[remap(k)] = (south[k] - min) / float(delta)

## a random CPR node is:
## <node id="613170606" lat="51.0442720" lon="-114.0737556" user="sbrown" uid="361745" visible="true" version="2" changeset="8429892" timestamp="2011-06-13T19:39:41Z"/>

for (k,v) in roads.items():
    print k,v
print "NORTH:"
for (k,v) in north_roads.items():
    print k,v
print "SOUTH:"
for (k,v) in south_roads.items():
    print k,v

print "East/West:"
for (k,v) in roads.items():
    print k,v

ax = plt.axes()

## first we do just the blue roads
## (i.e. "the data)
for way in named_ways:
    v = to_coords(way.nds)
    is_north = False
    care_about_north = False
    if 'Street' in way.tags['name'] or 'Trail' in way.tags['name']:
        care_about_north = True
        for (lng,lat) in v:
            if lat > 51.0442720:
                is_north = True
            else:
                pass#print "not north enough",lat,way.tags['name']
            
    x = map(lambda a: ((a[0] + 114.09567)/east_west_extent)+0.05, v)
    y = map(lambda a: ((a[1] - 51.03727)/north_south_extent)+0.05, v)

    k = way.tags['name'].strip().lower()
    k = ' '.join(k.split()[:3])
    line = None
    if care_about_north:
        if is_north:
            if north_roads.has_key(k):
                linewidth = (north_roads[k]*16.0)+1.0
                ax.add_line(mlines.Line2D(x, y, lw=linewidth, alpha=1.0, color='blue'))
        else:
            if south_roads.has_key(k):
                linewidth = (south_roads[k]*16.0)+1.0
                ax.add_line(mlines.Line2D(x, y, lw=linewidth, alpha=1.0, color='blue'))
    else:
        ## for east/west roads we want them to extend past center stret
        if 'avenue' in k and k[-1] == 'e':
            k = k[:-1] + 'w'
            
        if roads.has_key(k):
            linewidth = (roads[k] * 16.0) + 1.0
            ax.add_line(mlines.Line2D(x, y, lw=linewidth, alpha=1.0, color='blue'))

## now we do *all* the roads, with faint black lines            
for way in named_ways:
    v = to_coords(way.nds)
    is_north = False
    care_about_north = False
    x = map(lambda a: ((a[0] + 114.09567)/east_west_extent)+0.05, v)
    y = map(lambda a: ((a[1] - 51.03727)/north_south_extent)+0.05, v)

    k = way.tags['name'].strip().lower()
    k = ' '.join(k.split()[:3])
    line = None
    ax.add_line(mlines.Line2D(x, y, lw=0.5, alpha=0.4, color='black'))

plt.savefig('map-plot.svg', transparent=True)
#plt.show()
