import collections
import sys
import numpy as np
import matplotlib.pyplot as plt
from grid_world import GridWorld
from rl_agent import RLAgent


def plot_trace(agent, start, trace, title="test trajectory"):
    plt.plot(trace[:, 0], trace[:, 1], "ko-")
    plt.text(env.goal_pos[1], agent.size[0] - env.goal_pos[0] - 1, 'G')
    plt.text(start[1], agent.size[0] - start[0] - 1, 'S')
    plt.xlim([0, agent.size[1]])
    plt.ylim([0, agent.size[0]])


def plot_train(agent, rtrace, steps, trace, start):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(221)
    plt.plot(rtrace)
    plt.ylabel("sum of rewards")

    ax1 = fig.add_subplot(222)
    plt.plot(steps)
    plt.ylabel("# steps")

    # contour plot for agent.Q
    ax2 = fig.add_subplot(223)
    xs = range(agent.size[1])
    ys = range(agent.size[0])
    maxQ = np.max(agent.Q, axis=2)
    h_b = (maxQ == -np.inf)
    maxQ[h_b] = 0
    maxQ[h_b] = np.min(maxQ) - 100
    cs = plt.contourf(xs, ys[::-1], maxQ)
    plt.colorbar(cs)
    plt.text(env.goal_pos[1], agent.size[0] - env.goal_pos[0] - 1, 'G')
    plt.text(start[1], agent.size[0] - start[0] - 1, 'S')
    plt.ylabel("max agent.Q")

    # plot traces
    ax3 = fig.add_subplot(224)
    plot_trace(agent, start, trace, "trace of the last episode")

    plt.plot()
    plt.savefig("train.png", format="png")


if __name__ == '__main__':
    """
    This program has a couple of arguments settings
    length = 0 : Fails
    Length = 2 : maze_file_path, start position
    length = 3 : maze_file_path, start position, maximum steps
    length = 7 :
            1 : maze_file_path,
            2: start position
            3: gamma
            4: alpha
            5: epsilon
            6: max iterations
            7: maximum steps
    """
    if len(sys.arv) == 0:
        print("I need to know where the maze is and what its called!"\
              "Please do python3 RLSolver <mazelocation.txt> [Y, X]")
    if len(sys.argv) == 2:
        maze_location = sys.argv[0]
        start_location = sys.argv[1]
    env = GridWorld(sys.argv[0])
    env.print_map()

    agent = RLAgent(env)
    start = [8,2]
    if len(sys.argv == 3):
        rtrace, steps, trace = agent.train(start,
                                           gamma=0.99,
                                           alpha=0.1,
                                           epsilon=0.1,
                                           maxiter=100,
                                           maxstep=sys.argv[3])
    elif len(sys.argv) == 7:
        rtrace, steps, trace = agent.train(start,
                                           gamma=sys.argv[2],
                                           alpha=sys.argv[3],
                                           epsilon=sys.argv[4],
                                           maxiter=sys.argv[5],
                                           maxstep=sys.argv[6])
        )
    else:
        rtrace, steps, trace = agent.train(start,
                                        gamma=0.99,
                                        alpha=0.1,
                                        epsilon=0.1,
                                        maxiter=100,
                                        maxstep=1000)

    plot_train(agent, rtrace, steps, trace, start)

