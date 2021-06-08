//
// Created by nicol on 7/06/2021.
// https://www.linkedin.com/in/nick-vd-merwe/
// nick.jvdmerwe@gmail.com

// Implements a recursive backtracking algorithm to write
// a maze into the mazes directory
// https://stackoverflow.com/questions/60532245/implementing-a-recursive-backtracker-to-generate-a-maze
// https://www.gormanalysis.com/blog/random-numbers-in-cpp/

#include <iostream>
#include <ctime>
#include <utility>
#include <vector>
#include <stack>
#include <unordered_map>
#include <unordered_set>
#include <fstream>
#include <cstdio>
#include <random>

std::string currentDateTime() {
    time_t now = time(nullptr);
    const tm *timeStruct;
    char buffer[128];
    timeStruct = localtime(&now);

    strftime(buffer, sizeof(buffer), "%y_%m_%d_%X", timeStruct);

    return buffer;
}

struct cellInformation {
    cellInformation(std::pair<size_t, size_t> location,
                    std::vector<std::pair<size_t, size_t>> freeAdjacents) :
            location{std::move(location)},
            freeAdjacents{std::move(freeAdjacents)} {}

    std::pair<size_t, size_t> location;
    std::vector<std::pair<size_t, size_t>> freeAdjacents;
};

class RecursiveBacktrackingMaze {
public:
    RecursiveBacktrackingMaze(size_t &x, size_t &y, size_t seed) :
            x(x), y(y), rng(std::default_random_engine(seed)),
            random0to3(std::uniform_int_distribution<uint8_t>(0, 3)),
            random0toSize_t(std::uniform_int_distribution<size_t>(
                    0, std::numeric_limits<size_t>::max())) {
        /**
         * Fills the maze vector in storage with a set seed
         */
        // Start everything with walls - we'll be digging
        std::vector<char> filler(this->x, 'H');
        this->maze = std::vector<std::vector<char>>(this->y, filler);

        if (x < 2 && y < 2) {
            std::cerr << "WARNING: It is recommended that x and y are above 2"
                      << std::endl
                      << "however, it will continue." << std::endl;
        }

        // Pick a random start and end that's an odd number
        // In a backtracking algorithm like this, an odd number is always
        // an open wall.
        this->startPos = std::pair<size_t, size_t>{
                ((this->random0toSize_t(this->rng) % x) / 2) * 2 + 1,
                ((this->random0toSize_t(this->rng) % y) / 2) * 2 + 1
        };

        this->goalPos = std::pair<size_t, size_t>{
                ((this->random0toSize_t(this->rng) % x) / 2) * 2 + 1,
                ((this->random0toSize_t(this->rng) % y) / 2) * 2 + 1
        };

        while (startPos == goalPos) {
            // In case it made the exact same number, keep trying to make
            // more until they're different
            this->goalPos = std::pair<size_t, size_t>{
                    ((this->random0toSize_t(this->rng) % x) / 2 + 1) * 2,
                    ((this->random0toSize_t(this->rng) % y) / 2 + 1) * 2
            };
        }

        std::cout << "Start " << startPos.first << " " << startPos.second <<
                  std::endl <<
                  "Finish " << goalPos.first << " " << goalPos.second <<
                  std::endl;

        this->maze[startPos.second][startPos.first] = 'S';
        this->maze[goalPos.second][goalPos.first] = 'G';

        generateMaze();
    }

    /**
     * Fills the maze vector in storage with a random seed
     */
    RecursiveBacktrackingMaze(size_t &xParameter, size_t &yParameter) :
            RecursiveBacktrackingMaze(
                    xParameter, yParameter, time(nullptr)) {}


    std::vector<std::vector<char>> getMaze() {
        return maze;
    }

    bool saveMaze(const std::string &path) {
        // TODO: May need revision on file format
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
        std::string pathName = "mazes/" + std::to_string(this->x) + 'x' +
                               std::to_string(this->y) +
                               currentDateTime() + ".txt";
        return this->saveMaze(pathName);
    }

private:
    size_t x;
    size_t y;
    std::pair<size_t, size_t> startPos;
    std::pair<size_t, size_t> goalPos;

    /// The maze is represented as maze[y][x]
    std::vector<std::vector<char>> maze;
    std::stack<cellInformation> pathTaken;
    /// We can look up a random direction with this
    std::vector<std::pair<int8_t, int8_t>> moves{
            {0,  2},
            {0,  -2},
            {2,  0},
            {-2, 0}
    };

    std::default_random_engine rng;
    std::uniform_int_distribution<uint8_t> random0to3;
    std::uniform_int_distribution<size_t> random0toSize_t;

    void generateMaze() {
        /**
         * Sets the this->maze vector based on the current format
         */
        this->pathTaken.emplace(startPos,
                                listSolidAdjacentCells(startPos));
        while (!this->pathTaken.empty()) {
            auto &currentCell = this->pathTaken.top();
            // Roll back until currentCell has adjacent ones
            while (currentCell.freeAdjacents.empty()) {
                this->pathTaken.pop();
                currentCell = this->pathTaken.top();
            }
            // Pick a random free one
            uint8_t toMoveTo = random0to3(rng) %
                               currentCell.freeAdjacents.size();

            // Insert it into the stack as it is the next move
            this->pathTaken.emplace(
                    currentCell.freeAdjacents[toMoveTo],
                    listSolidAdjacentCells(currentCell.freeAdjacents[toMoveTo])
            );

            // Pop it out of the last one
            currentCell.freeAdjacents.erase(
                    currentCell.freeAdjacents.begin() + toMoveTo
            );

            // Update the maze
            markMazeClear(currentCell.location,
                          this->pathTaken.top().location);
        }
    }

    std::vector<std::pair<size_t, size_t>> listSolidAdjacentCells(
            std::pair<size_t, size_t> coord) {
        std::vector<std::pair<size_t, size_t>> clearCells;
        for (auto &m : moves) {
            // TODO: Validate that this can subtract
            auto adjacent = std::pair<size_t, size_t>{
                    m.first + coord.first,
                    m.second + coord.second
            };
            if (!isClear(adjacent)) {
                clearCells.push_back(adjacent);
            }
        }
        return clearCells;
    }

    void markMazeClear(std::pair<size_t, size_t> &start, std::pair<size_t,
            size_t> &finish) {
        /// Marks all the cells between start and finish as clear if they are
        /// walls

        // First find the direction that they are different in
        bool firstAxis = false;
        if (start.first != finish.first) {
            firstAxis = true;
        }

        // TODO: Verify these first/second operations are correct
        if (firstAxis) {
            for (size_t i = start.first; i > finish.first; i++) {
                if (this->maze[i][start.second] == 'H') {
                    this->maze[i][start.second] = 'O';
                }
            }
        } else {
            for (size_t i = start.second; i > finish.second; i++) {
                if (this->maze[start.first][i] == 'H') {
                    this->maze[start.first][i] = 'O';
                }
            }
        }
    }

    bool isClear(std::pair<size_t, size_t> coord) const {
        /// Evaluates true when the cell is not a wall and the coord is
        // inside bounds
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
    if (argc != 3) {
        std::cerr << "ERROR: This function requires an x and y dimension for "
                     "maze size" << std::endl;
    }
    size_t x = strtol(argv[1], nullptr, 10);
    size_t y = strtol(argv[2], nullptr, 10);

    auto maze = RecursiveBacktrackingMaze(x, y);
    maze.saveMaze();

    return EXIT_SUCCESS;
}