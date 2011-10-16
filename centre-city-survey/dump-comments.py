#!/usr/bin/env python

## dump just the comments

import csv
import random

reader = csv.reader(open('sanitized-data.csv','r'))
reader.next()                           # headers

for line in reader:
    comment = line[9].strip()
    if len(comment) == 0:
        continue

    comment.replace('\n', ' ')
    print comment
    print
