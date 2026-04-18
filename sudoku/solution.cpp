#include <omp.h>
#include <iostream>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <complex>
#include <chrono>
#include <iomanip>
#include <vector>


class Sudoku {
private:
    char data[9][9];

public:

    Sudoku() {
        memset(data, '0', sizeof(data));
    }

    // Constructor that accepts an input string
    Sudoku(const char* input) {
        parse(input);
    }

    // Copy constructor
    Sudoku(const Sudoku& other) {
        memcpy(data, other.data, sizeof(data));
    }

    // Check whether placing val at (x, y) is valid.
    bool isAllowed(char val, int x, int y) const {
        // Check if 'val' exists in row or column
        for (int i = 0; i < 9; ++i) {
            if (data[y][i] == val) return false;
            if (data[i][x] == val) return false;
        }
        // Check in 3x3 subgrid
        int cellBaseX = 3 * (x / 3);
        int cellBaseY = 3 * (y / 3);
        for (int yy = cellBaseY; yy < cellBaseY + 3; ++yy) {
            for (int xx = cellBaseX; xx < cellBaseX + 3; ++xx) {
                if (data[yy][xx] == val) return false;
            }
        }
        return true;
    }

    template <typename Callback>
    void solve(Callback onSolve, int depth = 99999) {
        for (int y = 0; y < 9; ++y) {
            for (int x = 0; x < 9; ++x) {
                if (data[y][x] == '0') {
                    // Try digits 1-9
                    for (char val = '1'; val <= '9'; ++val) {
                        if (isAllowed(val, x, y)) {
                            if (depth < 20) {
                                // With copy
                                Sudoku s = (*this);
                                #pragma omp task firstprivate(x, y, s, depth)
			                    {
                                    s.data[y][x] = val;
                                    s.solve(onSolve, depth+1);
                                }
                            } else {
                                // With backtracking without copy
                                data[y][x] = val;
                                solve(onSolve, depth+1);
                                data[y][x] = '0';
                            }
                        }
                    }
                    return;
                }
            }
        }

        onSolve(*this); // Complete solution found
    }

    template <typename Callback>
    void solveParallel(Callback onSolve, int depth = 0) {
        #pragma omp parallel
        {
            #pragma omp single
            {
                solve(onSolve, depth);
            }
        } 
    }


    // Parse input string to fill the Sudoku grid
    void parse(const char* input) {
        int len = strlen(input);
        for (int i = 0; i < 9*9; ++i) {
            int row = i / 9;
            int col = i % 9;

            if (i < len && '0' < input[i] && input[i] <= '9')
                data[row][col] = input[i];
            else
                data[row][col] = '0';
        }
    }

    // Print the Sudoku board to the provided output stream (default std::cout)
    void print(std::ostream& out = std::cout) const {
        for (int row = 0; row < 9; ++row) {
            for (int col = 0; col < 9; ++col) {
                out << data[row][col] << (col < 8 ? " " : "");
            }
            out << std::endl;
        }
    }
};


int main()
{
        // Start measuring time 
        auto begin = std::chrono::high_resolution_clock::now();


    // Read and parse all Sudoku puzzles into a vector of Sudoku objects
    std::vector<Sudoku> sudokus;

    char input[9*9+1];
    while (std::cin.getline(input, sizeof(input))) {
        sudokus.emplace_back(input);
    }

	for (size_t i = 0; i < sudokus.size(); ++i) {
		sudokus[i].solveParallel([&](const Sudoku& solution) {
			// omp_set_lock(&lock);
			std::cout << "Thread id: " << omp_get_thread_num() << std::endl;
			std::cout << "Sudoku #" << i << std::endl;
			solution.print();
			std::cout << std::endl;
			// omp_unset_lock(&lock);
		});
	}

        // Stop measuring time and calculate the elapsed time
        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double> elapsed = end - begin;

	std::cout << "Elapsed time: " << std::fixed << std::setprecision(9)
	          << elapsed.count() << "s" << std::endl;
	return 0;
}
