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
    RecursiveBacktrackingMaze(uint32_t &x, uint32_t &y, uint32_t seed) :
            x(x), y(y), rng(std::default_random_engine(seed)),
            randomInt(std::uniform_int_distribution<uint32_t>(
                    0, std::numeric_limits<uint32_t>::max())) {
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
        this->startPos = std::pair<uint32_t, uint32_t>{
                ((this->randomInt(this->rng) % x) / 2) * 2,
                ((this->randomInt(this->rng) % y) / 2) * 2
        };

        this->goalPos = std::pair<uint32_t, uint32_t>{
                ((this->randomInt(this->rng) % x) / 2) * 2,
                ((this->randomInt(this->rng) % y) / 2) * 2
        };

        while (startPos == goalPos) {
            // In case it made the exact same number, keep trying to make
            // more until they're different
            this->goalPos = std::pair<uint32_t, uint32_t>{
                    ((this->randomInt(this->rng) % x) / 2) * 2,
                    ((this->randomInt(this->rng) % y) / 2) * 2
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
    RecursiveBacktrackingMaze(uint32_t &xParameter, uint32_t &yParameter) :
            RecursiveBacktrackingMaze(
                    xParameter, yParameter, time(nullptr)) {}


    std::vector<std::vector<char>> getMaze() {
        return maze;
    }

    void printMaze(){
        for(auto & line : this->maze){
            for(auto & cell : line){
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
    uint32_t x;
    uint32_t y;
    std::pair<uint32_t, uint32_t> startPos;
    std::pair<uint32_t, uint32_t> goalPos;

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
    std::uniform_int_distribution<uint32_t> randomInt;

    void generateMaze() {
        /**
         * Sets the this->maze vector based on the current format
         */
        std::stack<std::pair<uint32_t, uint32_t>> pathTaken;
        pathTaken.emplace(startPos);
        // Start pos should already be marked so no need to worry
        // about marking it

        while (!pathTaken.empty()) {
            auto &currentCell = pathTaken.top();
            auto adjacent = listSolidAdjacentCells(currentCell);
            while (adjacent.empty()) {
                pathTaken.pop();
                if(pathTaken.empty()) break;
                currentCell = pathTaken.top();
                adjacent = listSolidAdjacentCells(currentCell);
            }

            if(pathTaken.empty() && adjacent.empty()) break;

            uint8_t &&randomChoice = randomInt(rng) % adjacent.size();
            pathTaken.emplace(
                    (2 * adjacent[randomChoice].first) + currentCell.first,
                    (2 * adjacent[randomChoice].second) + currentCell.second
            );

            MoveTwoAndClear(currentCell, adjacent[randomChoice]);
        }
    }

    std::vector<std::pair<int8_t, int8_t>> listSolidAdjacentCells(
            std::pair<uint32_t, uint32_t> coord) {

        std::vector<std::pair<int8_t, int8_t>> solidCells;
        for (auto &m : moves) {
            auto adjacent = std::pair<uint32_t, uint32_t>{
                    m.first + coord.first,
                    m.second + coord.second
            };
            if (isSolid(adjacent)) {
                solidCells.emplace_back(m);
            }
        }
        return solidCells;
    }

    void MoveTwoAndClear(
            std::pair<uint32_t, uint32_t> coord,
            std::pair<int8_t, int8_t> &movement) {
        /// Marks two cells in front/behind of coord
        for (int i = 0; i < 2; i++) {
            coord.first += movement.first;
            coord.second += movement.second;
            if (isSolid(coord)) {
                this->maze[coord.first][coord.second] = 'O';
            }
        }
    }

    bool isSolid(std::pair<uint32_t, uint32_t> coord) const {
        /**
         * Evaluates true when the cell is a wall and the coord is
         * inside bounds
         */
        if (coord.first >= x || coord.first < 0 ||
            coord.second >= y || coord.second < 0) {
            return false;
        }

        if (maze[coord.first][coord.second] == 'O') {
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
    uint32_t x = strtol(argv[1], nullptr, 10);
    uint32_t y = strtol(argv[2], nullptr, 10);

    std::cout << "Starting..." << std::endl;
    auto maze = RecursiveBacktrackingMaze(x, y, 42);
    maze.saveMaze();
    maze.printMaze();
    std::cout << std::endl << "Done" << std::endl;

    return EXIT_SUCCESS;
}