
all: map-plot.png plot_3.png plot_4.png plot_5.png plot_6.png ridertypes.png

map-plot.png: map-plot.py
	python map-plot.py

plot_3.png: plots.py
	python plots.py 3
plot_4.png: plots.py
	python plots.py 4
plot_5.png: plots.py
	python plots.py 5
plot_6.png: plots.py
	python plots.py 6

ridertypes.png: gnuplot-ridertypes genderridertypes.gp
	gnuplot gnuplot-ridertypes
