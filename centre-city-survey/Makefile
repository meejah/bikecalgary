
all: map-plot.png ridertypes.png genderages.png roads.png


map-plot.png: map-plot.py Makefile
	python map-plot.py
	convert -size 3000x15 -fill green -background white -font Helvetica -pointsize 12 "caption:Map data CC BY-SA 2.0 OpenStreetMap.org"  caption.png
	composite -geometry "+545+5" caption.png map-plot.png map-plot.png

## warning, these are a bit o' a hackjob since "gnuplot gnuplot-roads"
## really builds all four and I don't know if you can have multiple
## targets. and I don't really care, 'cause it works.

roads.png: roads_data.py roads_north_east.gp gnuplot-roads Makefile
	python roads_data.py
	gnuplot gnuplot-roads

	convert -crop "150x70+375+20" dummy_key.png key.png
	convert -rotate 90 roads_north_east.png foo.png
	composite -geometry "+620+20" key.png foo.png bar.png
	convert -crop "800x350+0+0" bar.png roads_north_east.png
#	convert -size 350x25 -background white -font Helvetica -pointsize 23 "caption:North of CPR, east/west routes" caption.png
#	composite -geometry "+250+325" caption.png roads_north_east.png roads_north_east.png

	convert -crop "150x70+375+20" dummy_key.png key.png
	convert -rotate 90 roads_north_north.png foo.png
	composite -geometry "+620+440" key.png foo.png bar.png
	convert -crop "800x600+0+0" bar.png roads_north_north.png
#	convert -size 350x25 -background white -font Helvetica -pointsize 23 "caption:North of CPR, north/south routes" caption.png
#	composite -geometry "+250+565" caption.png roads_north_north.png roads_north_north.png

	convert -crop "150x70+375+20" dummy_key.png key.png
	convert -rotate 90 roads_south_east.png foo.png
	composite -geometry "+620+140" key.png foo.png bar.png
	convert -crop "800x300+0+0" bar.png roads_south_east.png
#	convert -size 350x25 -background white -font Helvetica -pointsize 23 "caption:South of CPR, east/west routes" caption.png
#	composite -geometry "+250+270" caption.png roads_south_east.png roads_south_east.png

	convert -crop "150x70+375+20" dummy_key.png key.png
	convert -rotate 90 roads_south_north.png foo.png
	composite -geometry "+620+440" key.png foo.png bar.png
	convert -crop "800x600+0+0" bar.png roads_south_north.png
#	convert -size 350x25 -background white -font Helvetica -pointsize 23 "caption:South of CPR, north/south routes" caption.png
#	composite -geometry "+250+565" caption.png roads_south_north.png roads_south_north.png


	convert -size 800x1850 canvas:white roads.png
	convert -size 350x24 -background white -font Helvetica -pointsize 23 "caption:East/West Routes" caption.png
	composite -geometry "+140+5" caption.png roads.png roads.png
	composite -geometry "+0+35" roads_north_east.png roads.png roads.png
	composite -geometry "+0+350" roads_south_east.png roads.png roads.png

	convert -size 350x24 -background white -font Helvetica -pointsize 23 "caption:North/South Routes" caption.png
	composite -geometry "+140+620" caption.png roads.png roads.png
	convert -size 350x24 -background white -font Helvetica -pointsize 16 "caption:North of CPR" caption.png
	composite -geometry "+140+645" caption.png roads.png roads.png
	composite -geometry "+0+660" roads_north_north.png roads.png roads.png

	convert -size 350x24 -background white -font Helvetica -pointsize 16 "caption:South of CPR" caption.png
	composite -geometry "+140+1240" caption.png roads.png roads.png
	composite -geometry "+0+1260" roads_south_north.png roads.png roads.png
	rm caption.png
	rm foo.png
	rm bar.png
	rm dummy_key.png
	rm key.png


agegender.gp: ages_by_gender.py
	python ages_by_gender.py

genderridertypes.gp: ridertypes_by_gender.py
	python ridertypes_by_gender.py

ridertypes.png: gnuplot-ridertypes genderridertypes.gp
	gnuplot gnuplot-ridertypes

genderages.png: gnuplot-genderages agegender.gp
	gnuplot gnuplot-genderages
