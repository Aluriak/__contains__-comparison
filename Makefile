all: bench plot

bench:
	python benchmark.py

plot:
	python plot.py

show:
	feh benchmark.png


p: plot
b: bench
a: all
s: show
