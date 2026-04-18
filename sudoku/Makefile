# 
# Example Makefile to compile and run
#

# compile
# should be modified according to the tools of the paralellization
all: solution.cpp
	g++ -o solution solution.cpp -Xpreprocessor -fopenmp

# run locally
.PHONY: run-local
run-local: all
	./solution

# run on the cluster
# should be also modified
.PHONY: run
run: solution
	srun -o solution.out ./solution
	cat solution.out

# run on the cluster
# should be also modified
.PHONY: batch
batch: solution
	sbatch solution.sh

.PHONY: clean
clean:
	rm -rf solution mandelbrot.tga *.out

