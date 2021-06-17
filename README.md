# Maze Solver
## Main Script
Essentially, we want a script that does this
* Splits into n threads, and each has a unique name. On each thread:
  * Run the maze generator with X * Y dimensions
  * Solve with CSP, record time and path taken
  * Solve with RL, record time and path taken
* Average all the times together

These results should be graphed, trended to different big-O notations and 
compared in the report section.

## Maze Generator - Recursive backtracking
This is a backtracking algorithm in C++ which is compiled on Cygwin using -O3. 
Backtracking was chosen because it results [with fewer but longer dead ends, 
and usually a very long and twisty solution](http://www.astrolog.org/labyrnth/algrithm.htm), 
isn't uniform, and most importantly is bias free. We can generate a 
100,000\*100,000 maze in five minutes using ten gigabytes of RAM, and 10,000\*
10,000 in five seconds using 100MB of RAM. If we want to test even bigger, we 
should move to using recursive division, but that can end up with a maze that 
looks less 'human' as the passages are all either 2\*1 or 1\*2 in shape.

## PAT Solver
Essentially just the shunting game in the example scripts. Requires testing to 
check for memory overflow, must be able to survive until at least 1000\*1000.

## RL Model
To check and optimise
