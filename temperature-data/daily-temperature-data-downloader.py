#!/usr/bin/env python

## download each days min, average and max temperature from
## almanac.com

## http://www.almanac.com/weather/history/AB/Calgary/2010-01-01

import urllib2
import re
import datetime

matcher = re.compile('.*\\<h3>Temperature\\</h3>\\<div class="weatherhistory_results_datavalue temp_mn">\\<h4>Minimum Temperature\\</h4>\\<p>\\<span class="value">([0-9.-]*)\\</span> \\<span class="units">&#176;C\\</span>\\</p>\\<p class="explanation">\\</p>\\</div>\\<div class="weatherhistory_results_datavalue temp">\\<h4>Mean Temperature\\</h4>\\<p>\\<span class="value">([0-9.-]*)\\</span> \\<span class="units">&#176;C\\</span>\\</p>\\<p class="explanation">\\</p>\\</div>\\<div class="weatherhistory_results_datavalue temp_mx">\\<h4>Maximum Temperature\\</h4>\\<p>\\<span class="value">([0-9.-]*)\\</span> \\<span class="units">&#176;C\\</span>\\</p>\\<p class="explanation">\\</p>\\</div>\\</div>.*')

date = datetime.date(2010,1,1)           # january 1, 2010
delta = datetime.timedelta(1)           # 1 day

data = file('temperature-data-%04d.txt'%date.year, 'w')
data.write('#year/month/day min avg max\n')


for i in range(365):
    year, month, day = date.year, date.month, date.day
    date += delta
    for line in urllib2.urlopen('http://www.almanac.com/weather/history/AB/Calgary/%04d-%02d-%02d' % (year, month, day)).readlines():
        m = matcher.match(line)
        if m:
            min, avg, max = float(m.group(1)), float(m.group(2)), float(m.group(3))
            data.write('%04d/%02d/%02d %f %f %f\n' % (year, month, day, min, avg, max))

        
