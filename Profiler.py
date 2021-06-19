import os
import subprocess
import sys
import math

manual_run_bat = True
regen_mazes = True


class Profiler:
    def __init__(self, filename='maze',
                 RL_model='RLSolver/rl_script.py',
                 engine=0,  # DFS
                 maze_generator_path='maze_generator/maze_generator',
                 X=50,
                 Y=50,
                 csp_model='PAT Solver/mazeSolverModularMark.csp'):
        # All of the default values in case the builder messes up
        self.filename = filename
        self.RL_model = RL_model
        self.engine = engine
        self.maze_generator_path = maze_generator_path
        self.X = X
        self.Y = Y
        self.csp_model = csp_model

    def execute(self):
        self._init_dirs()
        print("Generating maze")
        self._run_maze_gen()
        self._generate_csp_file()
        if not manual_run_bat:
            print("Running CSP")
            self._run_csp_file()
        print("Running RL")
        self._run_RL_model()

    def _init_dirs(self):
        """
        Initializes the temporary directory that everything 'temporary'
        will get thrown into
        """
        self._if_dir_not_exist_make('temp')
        self._if_dir_not_exist_make('temp/mazes')
        self._if_dir_not_exist_make('temp/csp_models')
        self._if_dir_not_exist_make('temp/csp_out')

        self._if_dir_not_exist_make('profiles')
        self._if_dir_not_exist_make('profiles/csp')
        self._if_dir_not_exist_make('profiles/rl')

    def _if_dir_not_exist_make(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)

    def _run_maze_gen(self):
        if regen_mazes:
            os.system('./' + self.maze_generator_path + ' ' + str(self.X) + ' ' + str(
                self.Y) + ' temp/mazes/' + self.filename)
        self.csp_maze_path = 'temp/mazes/' + self.filename + '.csp'
        self.txt_maze_path = 'temp/mazes/' + self.filename + '.txt'
        self.txt_start_pos = 'temp/mazes/' + self.filename + '_startpos.txt'

    def _generate_csp_file(self):
        """
        Generates the CSP file by appending the model to the maze.csp file.
        """
        self.csp_model_and_maze = 'temp/csp_out/' + self.filename + '.csp'
        os.system('cat ' + self.csp_maze_path + ' \"' +
                  self.csp_model + '\" > ' +
                  self.csp_model_and_maze)

    def _run_csp_file(self):
        """
        Just runs PAT3.Console. In theory the output file should have
        everything we need. Note, this requires the mono package which you can
        download like this:
        https://www.mono-project.com/download/stable/#download-lin
        """
        # Note PAT is pretty silly. The input file is relative to the current
        # working directory and the output file is relative to the actual
        # executable. Which in our case, is at two different places.
        print("Running csp")
        model_out = '../profiles/csp/' + self.filename
        self.pat3_print = \
            subprocess.check_output(['mono', 'PAT3/PAT3.Console.exe',
                                     '-engine', str(self.engine),
                                     self.csp_model_and_maze, model_out])
        print("CSP did", self.pat3_print)

    def _run_RL_model(self):
        with open(self.txt_start_pos, 'r') as f:
            start_pos = f.read()
        split_start = start_pos.split(' ')
        max_length = str(int((self.X * math.log(self.X, math.e))))
        max_iterations = str(int(10 * self.X * math.log(self.X, math.e)))


        # self.rl_time_verbose = subprocess.run([
        #     '/usr/bin/time', '-v', 'python3',
        #     self.RL_model, self.txt_maze_path,
        #     split_start[0], split_start[1]
        # ], capture_output=True)

        self.rl_time_verbose = subprocess.run([
            '/usr/bin/time', '-v', 'python3',
            self.RL_model, self.txt_maze_path,
            split_start[0], split_start[1],
            max_length, max_iterations
        ], capture_output=True)

        self._save_string_to_file(self.rl_time_verbose, 'profiles/rl/' \
                                  + self.filename)

    def _save_string_to_file(self, string, filepath):
        print("Saving to file", filepath)
        f = open(filepath, 'wt')
        print(string, file=f)


def delete_directory(directory):
    """
    Deletes the entire temporary directory
    """
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


if __name__ == '__main__':
    # For now I'm just going to initialise a basic one
    # NOTE: If you're running this on windows, you'll have to swap the
    # maze_generator path. This can probably just get changed to a program
    # argument
    for i in range(5, 506, 10):
        print("Doing", i)
        profiler = Profiler()

        profiler.filename = str(i)
        profiler.RL_model = 'RLSolver/rl_script.py'
        profiler.X = i
        profiler.Y = i
        profiler.engine = 0

        profiler.execute()
    print("COMPLETED ALL PROFILING")

    if manual_run_bat:
        print("Temp files have been left to allow the PAT loop batch file to run.")
        print("Delete contents of temp directory when PAT loop has been run and completed.")

    if not manual_run_bat:
        delete_directory('temp')
