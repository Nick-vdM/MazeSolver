// Created by nicol on 7/06/2021.
// nick.vandermerwe@griffithuni.edu.au

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

class RecursiveBacktrackingMaze {
public:
    RecursiveBacktrackingMaze(int32_t &x, int32_t &y, int32_t seed) :
            x(x), y(y), rng(std::default_random_engine(seed)),
            randomInt(std::uniform_int_distribution<int32_t>(
                    0, std::numeric_limits<int32_t>::max())) {
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
        this->startPos = std::pair<int32_t, int32_t>{
                ((this->randomInt(this->rng) % x) / 2) * 2,
                ((this->randomInt(this->rng) % y) / 2) * 2
        };

        this->goalPos = std::pair<int32_t, int32_t>{
                ((this->randomInt(this->rng) % x) / 2) * 2,
                ((this->randomInt(this->rng) % y) / 2) * 2
        };

        while (startPos == goalPos) {
            // In case it made the exact same number, keep trying to make
            // more until they're different
            this->goalPos = std::pair<int32_t, int32_t>{
                    ((this->randomInt(this->rng) % x) / 2) * 2,
                    ((this->randomInt(this->rng) % y) / 2) * 2
            };
        }

        std::cout << "Start " << startPos.first << " " << startPos.second <<
                  std::endl <<
                  "Finish " << goalPos.first << " " << goalPos.second <<
                  std::endl;

        this->maze[startPos.first][startPos.second] = 'S';
        this->maze[goalPos.first][goalPos.second] = 'G';

        generateMaze();
    }

    /**
     * Fills the maze vector in storage with a random seed
     */
    RecursiveBacktrackingMaze(int32_t &xParameter, int32_t &yParameter) :
            RecursiveBacktrackingMaze(
                    xParameter, yParameter, time(nullptr)) {}


    std::vector<std::vector<char>> getMaze() {
        return maze;
    }

    void printMaze() {
        for (auto &line : this->maze) {
            for (auto &cell : line) {
                std::cout << cell;
            }
            std::cout << std::endl;
        }
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
    int32_t x;
    int32_t y;
    std::pair<int32_t, int32_t> startPos;
    std::pair<int32_t, int32_t> goalPos;

    /// The maze is represented as maze[y][x]
    std::vector<std::vector<char>> maze;
    /// We can look up a random direction with this
    std::vector<std::pair<int8_t, int8_t>> moves{
            {0,  1},
            {0,  -1},
            {1,  0},
            {-1, 0}
    };

    std::default_random_engine rng;
    std::uniform_int_distribution<int32_t> randomInt;

    void generateMaze() {
        /**
         * Sets the this->maze vector based on the current format
         */
        std::stack<std::pair<int32_t, int32_t>> pathTaken;
        pathTaken.emplace(startPos);
        // Start pos should already be marked so no need to worry
        // about marking it

        int32_t loops = 0;
        while (!pathTaken.empty()) {
            printMaze();
            std::cout << std::endl;
            auto &currentCell = pathTaken.top();
            auto adjacent = listSolidAdjacentCells(currentCell);
            while (adjacent.empty()) {
                pathTaken.pop();
                if (pathTaken.empty()) break;
                currentCell = pathTaken.top();
                adjacent = listSolidAdjacentCells(currentCell);
            }

            if (pathTaken.empty() && adjacent.empty()) break;

            uint8_t &&randomChoice = randomInt(rng) % adjacent.size();
            pathTaken.emplace(
                    (2 * adjacent[randomChoice].first) + currentCell.first,
                    (2 * adjacent[randomChoice].second) + currentCell.second
            );

            MoveTwoAndClear(currentCell, adjacent[randomChoice]);
        }
    }

    std::vector<std::pair<int8_t, int8_t>> listSolidAdjacentCells(
            std::pair<int32_t, int32_t> coord) {

        std::vector<std::pair<int8_t, int8_t>> solidCells;
        for (auto &m : moves) {
            auto adjacent = std::pair<int32_t, int32_t>{
                    (m.first * 2) + coord.first,
                    (m.second * 2) + coord.second
            };
            if (isInBounds(adjacent) && !isClear(adjacent)) {
                solidCells.emplace_back(m);
            }
        }
        return solidCells;
    }

    void MoveTwoAndClear(
            std::pair<int32_t, int32_t> coord,
            std::pair<int8_t, int8_t> &movement) {
        auto vectorCopy = this->maze;

        /// Marks two cells in front/behind of coord
        for (int i = 0; i < 3; i++) {
            if (isInBounds(coord) &&
                (this->maze[coord.first][coord.second] == 'H')) {
                this->maze[coord.first][coord.second] = 'O';
            }
            coord.first += movement.first;
            coord.second += movement.second;
        }

        if (vectorCopy == this->maze) {
            std::cout << "something is wrong" << std::endl;
        }
    }

    bool isInBounds(std::pair<int32_t, int32_t> &coord) const {
        if (coord.first >= x || coord.first < 0 ||
            coord.second >= y || coord.second < 0) {
            return false;
        }
        return true;
    }

    bool isClear(std::pair<int32_t, int32_t> &coord) const {
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
    int32_t x = strtol(argv[1], nullptr, 10);
    int32_t y = strtol(argv[2], nullptr, 10);

    std::cout << "Starting..." << std::endl;
    auto maze = RecursiveBacktrackingMaze(x, y, 42);
    maze.saveMaze();
    maze.printMaze();
    std::cout << std::endl << "Done" << std::endl;

    return EXIT_SUCCESS;
}