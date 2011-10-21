#!/usr/bin/env python

## dump just the comments

import csv
import random

with_emails = False

reader = csv.reader(open('downtown-calgary-cycling-engagement.csv','r'))
reader.next()                           # headers

for line in reader:
    comment = line[12].strip()
    if len(comment) == 0:
        continue

    email = None
    if len(line) > 22:
        email = line[22]
    comment = comment.replace('\n', ' ')
    comment = comment.replace('\r', ' ')
    if with_emails and email:
        print "(" + email.strip() + ")",comment
    else:
        print comment
    print
