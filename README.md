# Maze Solver
## Main Script
Essentially, we want a script that does this
* Splits into n threads, and each has a unique name. On each thread:
  * Run the maze generator with X * Y dimensions
  * Solve with CSP, record time and path taken
  * Solve with RL, record time and path taken
* Average all the times together

These results should be graphed, trended to different big-O notations and compared in the report section.

## Maze Generator - Recursive backtracking
This is a backtracking algorithm in C++ which is compiled on Cygwin using -O3. Backtracking was chosen because it results [with fewer but longer dead ends, and usually a very long and twisty solution]{http://www.astrolog.org/labyrnth/algrithm.htm}

## PAT Solver
Essentially just the shunting game in the example scripts.

## RL Model
To be made
