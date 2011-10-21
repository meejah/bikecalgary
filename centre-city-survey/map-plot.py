#!/usr/bin/env python

import os
import sys
import re
import csv
import numpy
import cairo
from util import ZeroDict
import osm

## some options to control the map
fearless_index = 1
fearless = 'fearless'
only_fearless = False
output = 'pdf'
DEBUG = False

## load the OSM data
osmmap = osm.OSM(open('centre-city.osm','r'))

def to_coords(nodes):
    "turn an osm.Node into x, y coords"
    rtn = []
    for n in nodes:
        n = osmmap.nodes[n]
        rtn.append( (n.lon, n.lat))
    return rtn

named_ways = []
for w in osmmap.ways.values():
    if w.tags.has_key('name'):
        named_ways.append(w)

## this controls the conversion of coords to "graph coords"
east_west_extent = (-114.04709 + 114.09567) + 0.001
north_south_extent = (51.05403 - 51.03727) + 0.001

reader = csv.reader(open('sanitized-data.csv','r'))
headers = reader.next()

ans = ZeroDict()
north = ZeroDict()
south = ZeroDict()

for line in reader:
    if only_fearless:
        if line[fearless_index].lower() == fearless:
            continue

    for road in (line[3].split(',') + line[5].split(',')):
        road = road.strip().lower()
        if len(road) == 0:
            continue
        if '8th avenue' in road:
            road = '8 avenue'

        ans[road] += 1

    for road in line[4].split(','):# + line[6].split(',')):
        road = road.strip().lower()
        if len(road) == 0:
            continue
        north[road] += 1
        
    for road in line[6].split(','):
        road = road.strip().lower()
        if len(road) == 0:
            continue
        south[road] += 1
        

name_re = re.compile('([0-9]*)[a-zA-Z]* (.*)')
##print ans

## make all the
## road names like OSM road tags seem to be ("8 Avenue" not "8th
## Avenue"). Although to get that, I had to hand-edit the .osm
## extract, because they're not consistent. This below remaps some
## of the survey answers to be OSM road names
##
## (FIXME: should go edit OSM itself with these fixes.)
##

def remap(k):
    m = name_re.match(k)
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
    #print "turned",k,"into",newk
    return newk

## normalize the road data to be from 0.0 to 1.0 

max = numpy.max(ans.values())
min = numpy.min(ans.values())
delta = max - min

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

if DEBUG:
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

## it's very odd that each of the Surface subclasses in Cairo (or at
## least pycairo) have different APIs for writing the output...
if output == 'svg':
    width, height = 800, 600
    surface = cairo.SVGSurface('map-plot.svg', width, height)
elif output == 'png':
    width, height = 800, 600
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
elif output == 'pdf':
    width, height = 800, 600
    surface = cairo.PDFSurface(open('map-plot.pdf','w'), width, height)
else:
    raise Exception("Don't understand output type:" + output)

context = cairo.Context(surface)
context.set_source_rgb(1,1,1)
context.rectangle(0,0,1,1)
context.fill()

context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
context.set_line_cap(cairo.LINE_CAP_ROUND)

## normalize the drawing context to (0,0) -> (1,1)
context.scale(width, height)


## utility function to draw a set of coordinates with a specific
## line-width
def draw_line(ctx, coords, lw):
    ctx.set_line_width(lw/500.0)
    ctx.move_to(coords[0][0], coords[0][1])
    for coord in coords[1:]:
        ctx.line_to(coord[0], coord[1])
    ctx.stroke()

## utility function to remap coordinates based on our extent. The
## magic numbers are google-projection geographic coordinates around
## Centre City (based on what I extracted from OSM).
def project(coord):
    x, y = coord
    return (((x + 114.09567) / east_west_extent),
            1.0 - ((y - 51.03727) / north_south_extent))

## first we do just the blue roads
## (i.e. "the data)
context.set_source_rgb(0,0,1)

for way in named_ways:
    coords = to_coords(way.nds)
    is_north = False
    care_about_north = False
    if 'Street' in way.tags['name'] or 'Trail' in way.tags['name']:
        care_about_north = True
        for (lng,lat) in coords:
            ## this is the longitude of a random CPR trainline node
            if lat > 51.0442720:
                is_north = True

    ## normalize these coordinates
    coords = map(project, coords)

    ## we take the first three words of the OSM street name and try to
    ## match against our survey names (which got transformed somewhat
    ## above).
    k = way.tags['name'].strip().lower()
    k = ' '.join(k.split()[:3])
    line = None

    ## this north/south stuff is CPR-tracks, which is only for
    ## Avenues, not streets and only because we split the survey based
    ## on the CPR tracks.
    if care_about_north:
        if is_north:
            if north_roads.has_key(k):
                linewidth = (north_roads[k]*16.0)+1.0
                draw_line(context, coords, linewidth)
        else:
            if south_roads.has_key(k):
                linewidth = (south_roads[k]*16.0)+1.0
                draw_line(context, coords, linewidth)
    else:
        ## for east/west roads we want them to extend past center
        ## street so we just mess with the name to make se become sw
        if 'avenue' in k and k[-1] == 'e':
            k = k[:-1] + 'w'
            
        if roads.has_key(k):
            linewidth = (roads[k] * 16.0) + 1.0
            draw_line(context, coords, linewidth)

##
## now we draw *all* the roads, with faint black lines
##
context.set_source_rgba(0,0,0,0.75)
for way in named_ways:
    coords = map(project, to_coords(way.nds))
    
    k = way.tags['name'].strip().lower()
    k = ' '.join(k.split()[:3])
    draw_line(context, coords, 1.0)

## write out the final product
if output == 'png':
    surface.write_to_png('map-plot.png')
context.show_page()
surface.finish()
