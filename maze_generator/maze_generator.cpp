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

/**
 * This is actually ripped out of the boost library, but I didn't want to go
 * through the pain of installing boost just so I can make a single hash
 * function, and it means that people running this don't have to either.
 *
 * Note, however, that these recommend stdex::hash_value and I'm using
 * std::hash. From what I saw, stdex::hash is just the VS C++ version (?)
 *
 * See https://stackoverflow.com/questions/16471691/good-hash-function-for-pair-of-primitive-types
 * @return
 */
template<typename T>
void hash_combine(size_t &seed, T const &v) {
    seed ^= std::hash<T>(v) + 0x9e3779b9 + (seed << 6) + (seed >> 2);
}

template<class T>
struct pairHash {
    std::size_t operator()(const std::pair<T, T> p) const {
        size_t firstHash = std::hash<T>(p.first);
        hash_combine(firstHash, p.second);
        return firstHash;
    }
};


std::string currentDateTime() {
    time_t now = time(nullptr);
    const tm *timeStruct;
    char buffer[128];
    timeStruct = localtime(&now);

    strftime(buffer, sizeof(buffer), "%y_%m_%d_%X", timeStruct);

    return buffer;
}

struct cellInformation {
    cellInformation(std::pair<uint32_t, uint32_t> location,
                    std::vector<std::pair<uint32_t, uint32_t>> freeAdjacents) :
            location{std::move(location)},
            freeAdjacents{std::move(freeAdjacents)} {}

    std::pair<uint32_t, uint32_t> location;
    std::vector<std::pair<uint32_t, uint32_t>> freeAdjacents;
};

class RecursiveBacktrackingMaze {
public:
    RecursiveBacktrackingMaze(uint32_t &x, uint32_t &y, uint32_t seed) :
            x(x), y(y), rng(std::default_random_engine(seed)),
            random0to3(std::uniform_int_distribution<uint8_t>(0, 3)),
            random0touint32_t(std::uniform_int_distribution<uint32_t>(
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
                ((this->random0touint32_t(this->rng) % x) / 2) * 2,
                ((this->random0touint32_t(this->rng) % y) / 2) * 2
        };

        this->goalPos = std::pair<uint32_t, uint32_t>{
                ((this->random0touint32_t(this->rng) % x) / 2) * 2,
                ((this->random0touint32_t(this->rng) % y) / 2) * 2
        };

        while (startPos == goalPos) {
            // In case it made the exact same number, keep trying to make
            // more until they're different
            this->goalPos = std::pair<uint32_t, uint32_t>{
                    ((this->random0touint32_t(this->rng) % x) / 2) * 2,
                    ((this->random0touint32_t(this->rng) % y) / 2) * 2
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
            {0,  2},
            {0,  -2},
            {2,  0},
            {-2, 0}
    };

    std::default_random_engine rng;
    std::uniform_int_distribution<uint8_t> random0to3;
    std::uniform_int_distribution<uint32_t> random0touint32_t;

    void generateMaze() {
        /**
         * Sets the this->maze vector based on the current format
         */
        std::stack<cellInformation> pathTaken;
        std::unordered_set<std::pair<uint32_t, uint32_t>, pairHash<uint32_t>>
                visitedCells;
        pathTaken.emplace(startPos,
                          listSolidAdjacentCells(startPos));
        uint32_t pops = 0;
        while (!pathTaken.empty()) {
            auto &currentCell = pathTaken.top();
            // Roll back until currentCell has adjacent ones
            while (currentCell.freeAdjacents.empty()) {
                pathTaken.pop();
                currentCell = pathTaken.top();
            }
            // Pick a random free one
            uint8_t toMoveTo = random0to3(rng) %
                               currentCell.freeAdjacents.size();

            // Insert it into the stack as it is the next move
            pathTaken.emplace(
                    currentCell.freeAdjacents[toMoveTo],
                    listSolidAdjacentCells(currentCell.freeAdjacents[toMoveTo])
            );

            // Pop it out of the last one
            currentCell.freeAdjacents.erase(
                    currentCell.freeAdjacents.begin() + toMoveTo
            );

            // Update the maze
            markMazeClear(currentCell.location,
                          pathTaken.top().location);
        }
    }

    std::vector<std::pair<uint32_t, uint32_t>> listSolidAdjacentCells(
            std::pair<uint32_t, uint32_t> coord) {
        std::vector<std::pair<uint32_t, uint32_t>> clearCells;
        for (auto &m : moves) {
            // TODO: Validate that this can subtract
            auto adjacent = std::pair<uint32_t, uint32_t>{
                    m.first + coord.first,
                    m.second + coord.second
            };
            if (isSolid(adjacent)) {
                clearCells.push_back(adjacent);
            }
        }
        return clearCells;
    }

    void
    markMazeClear(std::pair<uint32_t, uint32_t> &coord1, std::pair<uint32_t,
            uint32_t> &coord2) {
        /// Marks all the cells between coord1 and coord2 as clear if they are
        /// walls

        // First find the direction that they are different in
        bool firstAxis = false;
        if (coord1.first != coord2.first) {
            firstAxis = true;
        }

        // TODO: Verify these coord1/second operations are correct
        if (firstAxis) {
            for (uint32_t i = coord1.first; i == coord2.first; i++) {
                if (this->maze[i][coord1.second] == 'H') {
                    this->maze[i][coord1.second] = 'O';
                }
            }
        } else {
            for (uint32_t i = coord1.second; i == coord2.second; i++) {
                if (this->maze[coord1.first][i] == 'H') {
                    this->maze[coord1.first][i] = 'O';
                }
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

    auto maze = RecursiveBacktrackingMaze(x, y, 42);
    maze.saveMaze();

    return EXIT_SUCCESS;
}