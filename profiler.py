import os


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
        if not os.path.isdir(path):
            os.mkdir(path)

    def _run_maze_gen(self):
        os.system('./' + self.maze_generator_path,
                  self.X, self.Y, 'temp/mazes/' + self.filename)
        self.csp_maze_path = 'temp/mazes/' + self.filename + '.csp'
        self.txt_maze_path = 'temp/mazes/' + self.filename + '.txt'

    def _generate_csp_file(self):
        """
        Generates the CSP file by appending the model to the maze.csp file
        """
        self.csp_model_and_maze = 'temp/csp/' + self.filename + '.csp'
        os.system('cat', self.csp_maze_path, self.csp_model, '>',
                    self.csp_model_and_maze)

    def _run_csp_file(self):
        """
        Just runs PAT3.Console. In theory the output file should have
        everything we need
        """
        model_out = 'temp/csp_out/' + self.filename + '.txt'

        self.csp_time_verbose = os.system('PAT3.Console -engine ' +
                                          str(self.engine), \
                                          self.csp_model,  model_out)

    def _run_RL_model(self):
        # TODO Customise the RL parameters. I'm not sure what they are
        RL_command = 'python3 ' + self.RL_model
        self.rl_time_verbose = os.system('/usr/bin/time -v', RL_command)

        self._save_string_to_file(self.rl_time_verbose, 'profiles/rl/'\
                                  + self.filename + '_profile.txt')

    def _save_string_to_file(self, string, filepath):
        f = open(filepath)
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
            .set_RL_model() \
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
        return profiler


if __name__ == '__main__':
    # For now I'm just going to initialise a basic one
    # NOTE: If you're running this on windows, you'll have to swap the
    # maze_generator path. This can probably just get changed to a program
    # argument
    profiler = ProfilerBuilder() \
        .set_filename('maze') \
        .set_RL_model() \
        .set_engine('DFS') \
        .get_profiler()

    profiler.execute()
