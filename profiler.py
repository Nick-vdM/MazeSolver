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
        if self.delete_files:
            self._delete_temp_files()

    def _init_dirs(self):
        """
        Initializes the temporary directory that everything 'temporary'
        will get thrown into
        """
        # TODO: Change all of these paths into variables
        self._if_dir_not_exist_make('temp')
        self._if_dir_not_exist_make('temp/mazes')
        self._if_dir_not_exist_make('temp/csp_models')
        self._if_dir_not_exist_make('temp/csp_out')

        self._if_dir_not_exist_make('profiles')
        self._if_dir_not_exist_make('profiles/csp')
        self._if_dir_not_exist_make('profiles/rl')

    def _if_dir_not_exist_make(self, path):
        print("testing", path)
        if not os.path.isdir(path):
            print("Making", path)
            os.mkdir(path)

    def _run_maze_gen(self):
        # TODO: Change these os.system arguments to use f"" instead so its
        # a bit more readable
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
        os.system('cat ' + self.csp_maze_path + ' ' +
                  self.csp_model + ' > ' +
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
        model_out = '../temp/csp_out/' + self.filename + '.txt'
        print(os.getcwd())
        self.pat3_print = \
           subprocess.run(['mono', '\"PAT3/Pat3.Console.exe\"',
                                    '-engine', str(self.engine),
                                    self.csp_model, model_out])
        print(self.pat3_print)

    def _run_RL_model(self):
        # TODO: Test whether this prints the start pos correctly
        with open(self.txt_start_pos, 'r') as f:
            start_pos = f.read()

        RL_command = 'python3 ' + self.RL_model + ' ' + \
                     self.txt_maze_path + ' ' + \
                     start_pos
        self.rl_time_verbose = subprocess.run([
            '/usr/bin/time', '-v', RL_command
        ], capture_output=True)

        self._save_string_to_file(self.rl_time_verbose, 'profiles/rl/'\
                                  + self.filename + '_profile.txt')

    def _save_string_to_file(self, string, filepath):
        f = open(filepath, 'wt')
        print(string, file=f)

    def _delete_temp_files(self):
        """
        Deletes the entire temporary directory
        """
        try:
            os.rmdir('temp')
        except OSError as e:
            print("Error: tried to delete temp", e.strerror)


class ProfilerBuilder:
    """
    Generates a profiler
    """
    def __init__(self):
        self._profiler = Profiler()
        # Set everything to defaults
        self.set_filename('maze') \
            .set_delete_temp_files(True) \
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

    def set_delete_temp_files(self, delete_files):
        self._profiler.delete_files = delete_files
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

if __name__ == '__main__':
    # For now I'm just going to initialise a basic one
    # NOTE: If you're running this on windows, you'll have to swap the
    # maze_generator path. This can probably just get changed to a program
    # argument
    profiler = ProfilerBuilder() \
        .set_filename('maze') \
        .set_RL_model('RLSolver/rl_script.py') \
        .set_csp_engine('DFS') \
        .get_profiler()

    profiler.execute()
