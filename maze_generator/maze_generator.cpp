//
// Created by nicol on 7/06/2021.
// https://www.linkedin.com/in/nick-vd-merwe/
// nick.jvdmerwe@gmail.com

// Implements a recursive backtracking algorithm to write
// a maze into the mazes directory
// https://stackoverflow.com/questions/60532245/implementing-a-recursive-backtracker-to-generate-a-maze

#include <iostream>
#include <time.h>
#include <vector>
#include <stack>
#include <unordered_map>
#include <unordered_set>
#include <fstream>
#include <stdio.h>
#include <random>

class randomGen{
public:
    randomGen(){
        std::generate_n()
    }

private:
    static std::random_device r;
    static std::uniform_int_distribution<size_t> dist;
};

const std::string currentDateTime() {
    time_t now = time(0);
    const tm *timeStruct;
    char buffer[128];
    timeStruct = localtime(&now);

    strftime(buffer, sizeof(buffer), "%y_%m_%d_%X", timeStruct);

    return buffer;
}

class RecursiveBacktrackingMaze {
public:

    bool generateMaze(size_t x, size_t y) {
        // Pick a random start

    }

    std::vector<std::vector<char>> getMaze() {
        return maze;
    }

    bool saveMaze(std::string path) {
        std::ofstream ofs;
        ofs.open(path);
        if (!ofs) {
            std::cerr << "Failed to open " << path << std::endl;
            return false;
        }

        for (auto &row : maze) {
            for (auto &c : row) {
                ofs << c;
            }
            ofs << std::endl;
        }
        ofs.close();
        return true;
    }

    bool saveMaze() {
        /// Automatically picks a path under mazes/
        std::string pathName = "mazes/" + currentDateTime() + '.txt';
        return this->saveMaze();
    }

private:
    size_t x;
    size_t y;

    std::vector<std::vector<char>> maze;
    std::stack<std::pair<size_t, size_t>> path;
    /// We can look up a random direction with this
    std::vector<std::vector<int8_t>> moves{
            {0,  1},
            {0,  -1},
            {1,  0},
            {-1, 0}
    };

    bool isClear(std::pair<size_t, size_t> coord) const {
        if (coord.first > x || coord.first < 0 ||
            coord.second > y || coord.second < 0) {
            return false;
        }

        if (maze[coord.first][coord.second] == 'H') {
            return false;
        }

        return true;
    }
};

int main(int argc, char **argv) {
    if (argc != 2) {
        std::cerr << "ERROR: This function requires an x and y dimension for "
                     "maze size" << std::endl;
    }
    size_t x = atoi(argv[0]);
    size_t y = atoi(argv[1]);


}