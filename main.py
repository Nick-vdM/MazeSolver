import os

class Profiler:
    def execute():
        pass

    def _init_temp_dir(self):
        """
        Initializes the temporary directory that everything 'temporary'
        will get thrown into
        """
        pass

    def _run_maze_gen(self, maze_output_file):
        pass

    def _generate_csp_file(self):
        """
        Generates the CSP file by appending the model to the maze.csp file
        """
        pass

    def _run_csp_file(self, profile_output):
        pass

    def _run_RL_model(self, profile_output):
        pass

    def _delete_temp_files(self):
        """
        Deletes the entire temporary directory
        """
        pass

class ProfilerFactory:
    """
    Generates a profiler
    """
    def __init__(self):
        self._profiler = Profiler()

    def set_filename(self, filename):
        self._profiler.filename = filename
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
    profiler = ProfilerFactory() \
        .set_filename('maze')    \
        .set_RL_model()          \
        .set_engine('DFS')       \
        .get_profiler()

    profiler.execute()
    



    print("Test!")
    pass
