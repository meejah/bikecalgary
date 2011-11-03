#!/usr/bin/env python

import os
import sys
import re
import csv
import numpy
import cairo
from util import ZeroDict
import osm
import math

## some options to control the map
percent_labels = False
fearless_index = 1
fearless = 'fearless'
only_fearless = False
output = 'png'
DEBUG = False

if True:
    ## mostly-colour used to indicate popularity
    MAX_LINE_THICKNESS = 0.0
    MIN_LINE_THICKNESS = 4.0
    COLOR_MIN = (0.6,0.6,1)
    COLOR_MAX = (1,0,0)
    LABEL_COLOR = (0,0.1,0,1.0)
    
else:
    ## just line-thickness used to indicate popularity
    ## (this is the published map)
    MAX_LINE_THICKNESS = 16.0
    MIN_LINE_THICKNESS = 1.0
    COLOR_MIN = (0,0,1)
    COLOR_MAX = (0,0,1)
    LABEL_COLOR = (1,0,0,0.75)

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

realdata = {}
roads = {}
for k in ans.keys():
    roads[remap(k)] = (ans[k] - min) / float(delta)
    realdata[remap(k)] = ans[k]
maxreal = 327.0#numpy.max(realdata.values())
    
north_roads = {}
min = numpy.min(north.values())
delta = numpy.max(north.values()) - min
for k in north.keys():
    north_roads[remap(k)] = (north[k] - min) / float(delta)
    realdata[remap(k)] = north[k]

realsouth = {}
south_roads = {}
min = numpy.min(south.values())
delta = numpy.max(south.values()) - min
for k in south.keys():
    south_roads[remap(k)] = (south[k] - min) / float(delta)
    realsouth[remap(k)] = south[k]

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

## set up our context and make it white
context = cairo.Context(surface)
context.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
context.set_line_cap(cairo.LINE_CAP_ROUND)
context.set_source_rgb(1,1,1)
context.rectangle(0,0,1,1)
context.fill()


## normalize the drawing context to (0,0) -> (1,1) no matter how big
## we made it
context.scale(width, height)


## utility function to draw a set of coordinates with a specific
## line-width
def draw_line(ctx, coords, lw, color):
    if len(color) == 3:
        context.set_source_rgb(*color)
    else:
        context.set_source_rgba(*color)
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

## (linear) interpolate between two colours
def interpolate(a, b, amt):
    return map(lambda x,y: y + ((float(x)-float(y))*amt), a, b)

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
    ## streets, not avenues and only because we split the survey based
    ## on the CPR tracks.
    col = COLOR_MIN
    if care_about_north:
        if is_north:
            if north_roads.has_key(k):
                col = interpolate(COLOR_MAX, COLOR_MIN, north_roads[k])
                linewidth = (north_roads[k]*MAX_LINE_THICKNESS)+MIN_LINE_THICKNESS
                draw_line(context, coords, linewidth, col)
        else:
            if south_roads.has_key(k):
                col = interpolate(COLOR_MAX, COLOR_MIN, south_roads[k])
                linewidth = (south_roads[k]*MAX_LINE_THICKNESS)+MIN_LINE_THICKNESS
                draw_line(context, coords, linewidth, col)
    else:
        ## for east/west roads we want them to extend past center
        ## street so we just mess with the name to make se become sw
        if 'avenue' in k and k[-1] == 'e':
            k = k[:-1] + 'w'
            
        if roads.has_key(k):
            col = interpolate(COLOR_MAX, COLOR_MIN, roads[k])
            linewidth = (roads[k] * MAX_LINE_THICKNESS) + MIN_LINE_THICKNESS
            ## we scaled the context to be 0,0 -> 1,1 so need to
            ## compensate for aspect ratio
            linewidth = linewidth * (width/float(height))
            draw_line(context, coords, linewidth, col)

##
## now we draw *all* the roads, with faint black lines
##
for way in named_ways:
    coords = map(project, to_coords(way.nds))
    
    k = way.tags['name'].strip().lower()
    k = ' '.join(k.split()[:3])
    draw_line(context, coords, 1.0, (0,0,0,0.75))

##
## now label some roads. This is mostly "by hand" -- I selected nodes
## from the .osm data for each street which ends up with "decent
## looking" label placement.
##
## the list below is a list of Way IDs to use (the name is gotten from
## the tags). If you want to change the placement of a label, look in
## centre-city.osm, find a better node and exchange its ID here in the
## list. Ditto to add labels to other roads
##

if True:
    ## roads to label
    labels = ['32000799-7', '32517441-0', '32000716-6', '46695262-4', '32000977-6', '31973594-5']

    ## this is here, with the first "if" to help determine some IDs to
    ## use for streets you want to label
    to_name = ['1 Street SW']
    
    context.set_source_rgba(1,0,0,0.75)
    for way in named_ways:
       if way.tags['name'] in to_name:
           print way.id,way.tags['name']

       if way.id in labels:
           print "drawing",way.id,way.tags['name']
           context.set_source_rgba(*LABEL_COLOR)
           context.select_font_face('serif', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
           context.set_font_size(0.02)
           matrix = context.get_font_matrix()
           if 'Avenue' in way.tags['name']:
               ## approximate angle for all avenues
               angle = 0.0752901961851
               matrix.rotate(angle)
           else:
               ## just use 90 degrees for streets
               matrix.rotate(math.pi/2)
           context.set_font_matrix(matrix)
           coords = map(project, to_coords(way.nds))
           
           ## FIXME 0.01 should really be half the font-height instead
           if 'Avenue' in way.tags['name']:
               context.move_to(coords[0][0], coords[0][1]+0.01)
           else:
               context.move_to(coords[0][0]-0.01, coords[0][1])

           ## figure out some label text, optionally with the percent
           ## of respondents who clicked this response. Could use
           ## "realmax" or "southmax" to get the normalized percent
           ## instead...but that's not really a percent so much as a rank
           txt = way.tags['name']

           if percent_labels:
               if realdata.has_key(way.tags['name'].lower()):
                   percent = ((realdata[way.tags['name'].lower()]/maxreal)*100.0)

                   ## for a street, we take the biggest value from the
                   ## north and south of CPR tracks response. Could put
                   ## both labels on, but usually they're very close and
                   ## that will clutter the map a lot more.
                   if realsouth.has_key(way.tags['name'].lower()):
                       p = ((realsouth[way.tags['name'].lower()]/maxreal)*100.0)
                       print way.tags['name'],p
                       if p > percent:
                           percent = p
                   txt = txt + ' (%02.1f%%)' % percent
           context.show_text(txt)
    

## write out the final product
if output == 'png':
    surface.write_to_png('map-plot.png')
context.show_page()
surface.finish()
