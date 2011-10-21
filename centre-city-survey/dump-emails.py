#!/usr/bin/env python

## dump just the emails

import csv
import random

reader = csv.reader(open('downtown-calgary-cycling-engagement.csv','r'))
reader.next()                           # headers

email_idx = 22
for line in reader:
    if len(line) <= email_idx:
        continue
    email = line[email_idx].strip()
    if len(email) == 0:
        continue

    print email
