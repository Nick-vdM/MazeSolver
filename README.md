# Maze Solver
## Overview
This consists of five tools. The PAT Solver folder, RLSolver folder, 
maze_generator folder, and the Profiler and ProfileParser.

## PAT Solver
There are two files in here, a 'normal' maze solver that functions exactly
like the shunting game, and a solver that marks where it has gone. It was noticed
that if we mark the previous move, it lowers the maximum number of transitions
and usually makes it faster with less memory usage.

## Reinforcement Learning
This is essentially just the lab split into individual scripts. The grid\_world 
handles all of the operations with regards to the actual world, the rl\_agent 
manages the RLAgent class, and the script ties them together.

## Maze Generator - Recursive backtracking
This is a backtracking algorithm in C++ which is compiled on Cygwin using -O3. 
Backtracking was chosen because it results [with fewer but longer dead ends, 
and usually a very long and twisty solution](http://www.astrolog.org/labyrnth/algrithm.htm), 
isn't uniform, and most importantly is bias free. We can generate a 
100,000\*100,000 maze in five minutes using ten gigabytes of RAM, and 10,000\*
10,000 in five seconds using 100MB of RAM. So the time spent on maze
generation in comparison to other tasks is next to none.

Another thing that is done in the maze generator is making the maze files.
It fully prints the CSP file with the correct syntax, and prints the text
file used by the RL scripts.

## Profiler.py
This runs the maze generator, then runs the CSP and the RL on the same maze that 
was made for a given number of loops with increments.

One important thing is that this only functions on Linux because it uses the
time command from there to measure memory. Additionally, this means that it runs
noticeably slower than it would directly through windows (about a factor of 3).

## ProfileParser.py
This consists of two classes, the ProfileParser and the GraphMaker. Due to how
the profiler produces just the outputs of the commands instead of parsing out the
useful information, it extracts the actual useful parts.

As for the graph maker, it makes graphs.
