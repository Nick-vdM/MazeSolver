// Created by nicol on 7/06/2021.
// nick.vandermerwe@griffithuni.edu.au

// Implements a recursive backtracking algorithm to write
// a maze into the mazes directory
// https://stackoverflow.com/questions/60532245/implementing-a-recursive-backtracker-to-generate-a-maze
// https://www.gormanalysis.com/blog/random-numbers-in-cpp/

#include <iostream>
#include <cerrno>
#include <ctime>
#include <utility>
#include <vector>
#include <stack>
#include <fstream>
#include <cstdio>
#include <random>
#include <chrono>
#include <cstring>

#pragma comment(linker, "/STACK:10000000")
#pragma comment(linker, "/HEAP:10000000")


std::string currentDateTime() {
    time_t now = time(nullptr);
    const tm *timeStruct;
    char buffer[128];
    timeStruct = localtime(&now);

    strftime(buffer, sizeof(buffer), "_%y_%m_%d_%H%M%S", timeStruct);

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
        std::vector<char> filler(this->y, 'H');
        this->maze = std::vector<std::vector<char>>(this->x, filler);

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

//        this->startPos = std::pair<int32_t, int32_t>{0, 0};
//        this->goalPos = std::pair<int32_t, int32_t>{248, 8};

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

        generateMaze();

        // Add the start and goal afterwards. This makes comparisons during
        // that search easier/faster
        this->maze[startPos.first][startPos.second] = 'S';
        std::cout << "Goal " << goalPos.first << " " << goalPos.second <<
                  std::endl;
        this->maze[goalPos.first][goalPos.second] = 'G';
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
                std::cout << cell << "  ";
            }
            std::cout << std::endl;
        }
    }

    bool saveStartPosToTxt(const std::string &path) {
        /**
         * You probably only care about this if you specified the filename
         */
        std::ofstream ofs;
        ofs.open(path);
        if (!ofs) {
            std::cerr << "Failed to open " << path << std::endl;
            std::cerr << strerror(errno) << std::endl;
            return false;
        }

        ofs << this->startPos.first << " " << this->startPos.first;
        ofs.close();
        return true;
    }

    bool saveMazeToTxt(const std::string &path) {
        // TODO: May need revision on file format
        std::ofstream ofs;
        ofs.open(path);
        if (!ofs) {
            std::cerr << "Failed to open " << path << std::endl;
            std::cerr << strerror(errno) << std::endl;
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

    bool saveMazeToTxt() {
        /// Automatically picks a path under mazes/
        std::string pathName = "mazes/" + std::to_string(this->x) + 'x' +
                               std::to_string(this->y) +
                               currentDateTime() + ".txt";
        return this->saveMazeToTxt(pathName);
    }

    bool saveMazeToCsp(const std::string &path) {
        // TODO: May need revision on file format
        std::ofstream ofs;
        ofs.open(path);
        if (!ofs) {
            std::cerr << "Failed to open " << path << std::endl;
            std::cerr << strerror(errno) << std::endl;
            return false;
        }

        ofs << "#define NoOfRows " << this->x << ";" << std::endl;
        ofs << "#define NoOfCols " << this->y << ";" << std::endl;
        ofs << "var maze[NoOfRows][NoOfCols]:{0..4} = [";
        size_t index = 0; // its impossible for 2^31^2 to overflow this
        size_t maxIndex = (this->x * this->y);
        for (auto &row : maze) {
            for (auto &c : row) {
                switch (c) {
                    case 'O':
                        ofs << '0';
                        break;
                    case 'H':
                        ofs << '1';
                        break;
                    case 'S':
                        ofs << '2';
                        break;
                    case 'G':
                        ofs << '3';
                        break;
                    default:
                        std::cerr << "Something strange is in the maze"
                                  << std::endl;
                        break;
                }
                if (++index >= maxIndex) break;
                ofs << ",";
            }
            ofs << std::endl << '\t';
        }
        // We could have done that last loop with an if condition in the middle,
        // but frankly its going to be a hell of a lot easier to just delete
        // that last comma

        ofs << "];" << std::endl;

        // When the file gets opened it should have a newline at the end for
        // safety
        ofs << "var pos[2]:{0.." << std::max(this->x, this->y)
            << "} = [" << this->startPos.first << "," << this->startPos.second
            << "];" << std::endl;

        ofs.close();
        return true;
    }

    bool saveMazeToCsp() {
        /// Automatically picks a path under mazes/
        std::string pathName = "mazes/" + std::to_string(this->x) + 'x' +
                               std::to_string(this->y) +
                               currentDateTime() + ".csp";
        return this->saveMazeToCsp(pathName);
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
        std::stack<std::pair<int32_t, int32_t>,
                std::vector<std::pair<uint32_t, uint32_t>>> pathTaken;
        pathTaken.emplace(startPos);
        // Start pos should already be marked so no need to worry
        // about marking it

        int32_t loops = 0;
        while (!pathTaken.empty()) {
//            std::cout << pathTaken.size() << std::endl;
//            printMaze();
//            std::cout << std::endl;
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
            MoveTwoAndClear(currentCell, adjacent[randomChoice]);
            pathTaken.emplace(
                    (2 * adjacent[randomChoice].first) + currentCell.first,
                    (2 * adjacent[randomChoice].second) + currentCell.second
            );
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
            if (isInBounds(adjacent) &&
                this->maze[adjacent.first][adjacent.second] == 'H') {
                solidCells.emplace_back(m);
            }
        }
        return solidCells;
    }

    void MoveTwoAndClear(
            std::pair<int32_t, int32_t> coord,
            std::pair<int8_t, int8_t> &movement) {
        /// Marks two cells in front/behind of coord
        for (int i = 0; i < 2; i++) {
            coord.first += movement.first;
            coord.second += movement.second;
            if (isInBounds(coord) &&
                (this->maze[coord.first][coord.second] == 'H')) {
                this->maze[coord.first][coord.second] = 'O';
//                        std::to_string(drawAll++ %10)[0];
            }
        }
    }

    bool isInBounds(std::pair<int32_t, int32_t> &coord) const {
        if (coord.first >= x || coord.first < 0 ||
            coord.second >= y || coord.second < 0) {
            return false;
        }
        return true;
    }

    int drawAll{0};
};

int main(int argc, char **argv) {
    std::cout << "Please run this as ./program x y <filename>. Filename is "
                 "optional";
    if (argc < 3) {
        std::cerr << "ERROR: This function requires an x and y dimension for "
                     "maze size" << std::endl;
    }


    int32_t x = strtol(argv[1], nullptr, 10);
    int32_t y = strtol(argv[2], nullptr, 10);

    std::cout << "Starting..." << std::endl;
    // TODO: 43 and commented startpos/goalpos crashes

    std::chrono::time_point<std::chrono::system_clock> start, end;
    start = std::chrono::system_clock::now();
    auto maze = RecursiveBacktrackingMaze(x, y);
    end = std::chrono::system_clock::now();
    std::chrono::duration<double> elapsed_seconds = end - start;
    std::time_t end_time = std::chrono::system_clock::to_time_t(end);
    std::cout << "finished computation at " << std::ctime(&end_time)
              << "elapsed time: " << elapsed_seconds.count() << "s\n";
    std::cout << std::endl << "Done" << std::endl;

    if (argc == 4) {
        // They want a filename
        maze.saveStartPosToTxt(std::string(argv[3]) + "_startpos.txt");
        maze.saveMazeToTxt(std::string(argv[3]) + ".txt");
        maze.saveMazeToCsp(std::string(argv[3]) + ".csp");
    } else {
        maze.saveMazeToTxt();
        maze.saveMazeToCsp();
    }


    return EXIT_SUCCESS;
}
