#!/usr/bin/env python

## this takes the "real" raw .csv data from google and sanitizes it
## for public consumption. This involves: removing the first two
## columns (timestamp, and an unused question); removing column 9 (an
## unused question); removing the last entry (email address) and
## randomizing the entries before re-writing them.

import csv
import random


reader = csv.reader(open('downtown-calgary-cycling-engagement.csv','r'))
writer = csv.writer(open('sanitized-data.csv', 'w'))

new_data = []
headers = reader.next()
new_headers = headers[2:-1]
new_headers = new_headers[:6] + new_headers[7:]
reader.next()                           # mike's debug response

for line in reader:
    if len(line) < 8:
        continue                        # there is one bogus response with no answers

    # remove first two columns and last column
    newline = line[2:-1]
    oldentry = newline[6]
    if oldentry.strip() != '':
        print "Danger! Column 8 wasn't empty!"
    # remove column 8 (which is now 6)
    newline = newline[:6] + newline[7:]
    new_data.append(newline)

wrote = 0
writer.writerow(new_headers)
while len(new_data):
    ln = random.randrange(0, len(new_data))
    writer.writerow(new_data[ln])
    wrote += 1
    new_data = new_data[:ln] + new_data[ln+1:]

if wrote != 327:
    print "Didn't write the correct number of lines!"
