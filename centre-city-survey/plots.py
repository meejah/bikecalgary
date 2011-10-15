#!/usr/bin/env python

##
## draw some pretty pictures of the data
##

## this is a total hackjob as I don't really know how to use
## matplotlib but thought I'd give it a go. I don't see how to reset
## its state, so instead of just running a loop to generate the 4
## plots I want, we take a command-line parameter.
##
## matplotlib produces reasonble looking plots, but I find it somewhat
## counter-intuitive to use -- although it somewhat follows gnuplot's
## paradigm of issuing commands which affect the "current" plot. that
## was what I was trying to get away from with a python solution,
## however ;)

import csv
import numpy
import sys
reader = csv.reader(open('sanitized-data.csv','r'))

titles = reader.next()

## this is the index into the data of which roads we're interested in

titles = {3: 'North of CPR, east/west routes',
          4: 'North of CPR, north/south routes',
          5: 'South of CPR, east/west routes',
          6: 'South of CPR, north/south routes'}

def generate_plot(index, fname):
    answers = {}
    answers['both 9th and 8th'] = 0
    fearless_answers = {}
    fearless_answers['both 9th and 8th'] = 0
    for line in reader:
        print line[2]
        if line[2].lower() == 'female':
            ans = answers
        else:
            ans = fearless_answers
            

        test = 0
        for road in line[index].split(','):
            road = road.strip()
            if '8th Avenue' in road:
                test += 1
                road = '8th Avenue (except S.A.)'
            if len(road) == 0:
                continue
            if '9th' in road:
                test += 1

            if ans.has_key(road):
                ans[road] += 1
            else:
                ans[road] = 1
        if test == 2:
            ans['both 9th and 8th'] += 1
            print "both!"


    print answers
    print fearless_answers

    import matplotlib.pyplot as plt

    def sorter(a, b):
        return cmp(a[1], b[1])
    items = answers.items()
    items.sort(sorter)
    fearless_items = []
    for (k,v) in items:
        fearless_items.append((k, fearless_answers[k]))

    

    N = len(items)
    ind = numpy.arange(N)
    fig = plt.figure(figsize=(9,7))
    ax1 = fig.add_subplot(111)
    ax2 = fig.add_subplot(111)
    plt.subplots_adjust(left=0.3)
    print map(lambda x: x[1], items)
    rects = ax1.barh(ind, map(lambda x: x[1], items), 0.45, color='blue')
#    for rect in rects:
#        ax1.text(2, rect.get_y()+(rect.get_height()/2.0), int(rect.get_width()), color='white', verticalalignment='center', weight='bold')
                 
    rects = ax2.barh(ind+0.5, map(lambda x: x[1], fearless_items), 0.45, color='red')
#    for rect in rects:
#        ax2.text(2, rect.get_y()+(rect.get_height()/2.0), int(rect.get_width()), color='white', verticalalignment='center', weight='bold')
        
    plt.ylabel("Road")
    def format(s):
        if '(' in s:
            return s[:s.find('(')]
        return s
    plt.yticks(numpy.arange(N)+0.5, map(lambda x: format(x[0]), items))
    plt.title(titles[index])
    plt.margins(0, 0, tight=False)
    plt.savefig(fname)

idx = int(sys.argv[1])
generate_plot(idx, "plot_%d.png"%idx)

