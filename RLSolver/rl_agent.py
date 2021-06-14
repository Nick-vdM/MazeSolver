import numpy as np

# top-left to (0,0)
def coord_convert(s, sz):
    return [s[1], sz[0]-s[0]-1]


class RLAgent:
    """
        Reinforcement Learning Agent Model for training/testing
        with Tabular function approximation

    """

    def __init__(self, env):
        self.env = env
        self.size = env.get_size()
        self.n_a = len(env.get_actions())
        # self.Q table including the surrounding border
        self.Q = np.zeros((self.size[0], self.size[1], self.n_a))

    def greedy(self, s):
        return np.argmax(self.Q[s[0], s[1]])

    def epsilon_greed(self, e, s):
        if np.random.rand() < e:
            return np.random.randint(self.n_a)
        else:
            return self.greedy(s)

    def train(self, start, **params):

        # parameters
        gamma = params.pop('gamma', 0.99)
        alpha = params.pop('alpha', 0.1)
        epsilon = params.pop('epsilon', 0.1)
        maxiter = params.pop('maxiter', 1000)
        maxstep = params.pop('maxstep', 1000)

        # init self.Q matrix
        self.Q[...] = 0
        self.Q[self.env._map == 'H'] = -np.inf

        # online train
        # rewards and step trace
        rtrace = []
        steps = []
        for j in range(maxiter):

            self.env.init(start)
            s = self.env.get_cur_state()
            # selection an action
            a = self.epsilon_greed(epsilon, s)

            rewards = []
            trace = np.array(coord_convert(s, self.size))
            # run simulation for max number of steps
            for step in range(maxstep):
                # move
                r = self.env.next(a)
                s1 = self.env.get_cur_state()
                a1 = self.epsilon_greed(epsilon, s1)

                rewards.append(r)
                trace = np.vstack((trace, coord_convert(s1, self.size)))

                # update self.Q table
                self.Q[s[0], s[1], a] += alpha * (r + gamma * np.max(self.Q[s1[0], s1[1], :]) - self.Q[s[0], s[1], a])

                if self.env.is_goal():  # reached the goal
                    self.Q[s1[0], s1[1], a1] = 0
                    break

                s = s1
                a = a1

            rtrace.append(np.sum(rewards))
            steps.append(step + 1)
        return rtrace, steps, trace  # last trace of trajectory

    def test(self, start, maxstep=1000):
        self.env.init(start)
        s = self.env.get_cur_state()
        a = np.argmax(self.Q[s[0], s[1], :])
        trace = np.array(coord_convert(s, self.size))
        for step in range(maxstep):
            self.env.next(a)
            s1 = self.env.get_cur_state()
            a1 = np.argmax(self.Q[s1[0], s1[1], :])
            trace = np.vstack((trace, coord_convert(s1, self.size)))
            if self.env.is_goal():  # reached the goal
                break
            a = a1

        return trace