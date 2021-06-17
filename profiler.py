import os
import subprocess


class Profiler:
    def __init__(self):
        self.filename = ''
        self.delete_files = True
        self.RL_model = 0
        self.engine = 0
        self.maze_generator_path = 'maze_generator/maze_generator'
        self.X = 50
        self.Y = 50
        self.csp_model = 'PAT Solver/mazeSolverModularMark.csp'
        pass

    def execute(self):
        self._init_dirs()
        self._run_maze_gen()
        self._generate_csp_file()
        self._run_csp_file()
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
        os.system('./' + self.maze_generator_path + ' ' +
                  str(self.X) + ' ' + str(self.Y) + ' temp/mazes/' + self.filename)
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
        model_out = '../profiles/csp/' + self.filename
        self.pat3_print = \
           subprocess.check_output(['mono', 'PAT3/Pat3.Console.exe',
                                    '-engine', str(self.engine),
                                    self.csp_model_and_maze, model_out])
        print('test', self.pat3_print)

    def _run_RL_model(self):
        # TODO: Test whether this prints the start pos correctly
        with open(self.txt_start_pos, 'r') as f:
            start_pos = f.read()
        split_start = start_pos.split(' ')
        self.rl_time_verbose = subprocess.run([
            '/usr/bin/time', '-v', 'python3',
            self.RL_model, split_start[0], split_start[1]
        ], capture_output=True)

        self._save_string_to_file(self.rl_time_verbose, 'profiles/rl/'\
                                  + self.filename)

    def _save_string_to_file(self, string, filepath):
        f = open(filepath, 'wt')
        print(string, file=f)



class ProfilerBuilder:
    """
    Generates a profiler
    """
    def __init__(self):
        self._profiler = Profiler()
        # Set everything to defaults
        self.set_filename('maze') \
            .set_RL_model('RLSolver/rl_script.py') \
            .set_maze_generator_path('maze_generator/maze_generator')

    def set_filename(self, filename):
        self._profiler.filename = filename
        return self

    def set_maze_generator_path(self, path):
        self._profiler.maze_generator_path = path
        return self

    def set_maze_XY(self, X, Y):
        self._profiler.X = X
        self._profiler.Y = Y
        return self

    def set_RL_model(self, RL_model):
        self._profiler.RL_model = RL_model
        return self

    def set_csp_engine(self, engine='DFS'):
        """
        Can be BFS or DFS
        """
        # There are only two possible states so its fine to just force
        # it into two things
        if engine.lower() == 'dfs':
            self._profiler.engine = 0
        else:
            self._profiler.engine = 1

        return self

    def get_profiler(self):
        return self._profiler


def extract_csp_profiles(csp_profile_directory):
    pass

def extract_RL_profiles(RL_profile_directory):
    pass

def extract_profile_dirs(main_directory):
    # TODO: Open all of the profile directories and save them as a single
    # file with the format of
    # dict{'XShape, YShape' : [path length, time to solve in seconds, memory used in MB]}
    pass

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
    for i in range(5, 500, 15):
        print("Doing", i)
        profiler = ProfilerBuilder()              \
            .set_filename(str(i))                 \
            .set_RL_model('RLSolver/rl_script.py')\
            .set_maze_XY(i, i)                  \
            .set_csp_engine('DFS')                \
            .get_profiler()

        profiler.execute()
    print("COMPLETED ALL PROFILING")

    delete_directory('temp')
