# importing the required module
import matplotlib.pyplot as plt
import math
import random
from datetime import datetime
import csv

random.seed(datetime.now())

highest_rl_reached = 505 + 1
highest_csp_reached = 355 + 1


class ProfileParser:
    def __init__(self):
        self.rl_time_arr = []
        self.rl_mem_arr = []
        self.rl_step_arr = []
        self.rl_size_arr = []

        for i in range(5, highest_rl_reached, 10):
            out, err = self.read_rl_file(f"profiles/rl/{i}")
            time, mem = self.rolling_check_stderr(err)
            steps = self.rolling_check_stdout(out)
            self.rl_time_arr.append(time)
            self.rl_mem_arr.append(mem)
            if steps < 1000:
                self.rl_step_arr.append(steps)
            else:
                self.rl_step_arr.append(None)
            self.rl_size_arr.append(i)

        for i in range(len(self.rl_time_arr)):
            print(f"({self.rl_size_arr[i]}, {self.rl_time_arr[i]}, {self.rl_mem_arr[i]}, {self.rl_step_arr[i]})")

        self.csp_time_arr = []
        self.csp_mem_arr = []
        self.csp_step_arr = []
        self.csp_size_arr = []

        for i in range(5, highest_csp_reached, 10):
            steps, time, mem = self.read_csp_file(f"profiles/csp/{i}")
            self.csp_time_arr.append(time)
            self.csp_mem_arr.append(mem)
            self.csp_step_arr.append(steps)
            self.csp_size_arr.append(i)

        for i in range(len(self.csp_time_arr)):
            print(f"({self.csp_size_arr[i]}, {self.csp_time_arr[i]}, {self.csp_mem_arr[i]}, {self.csp_step_arr[i]})")

        self.linear = []
        self.exp = []
        self.log = []
        self.nlog = []
        self.poly = []
        self.exp3 = []
        for i in range(5, 506, 10):
            self.linear.append(i)
            self.exp.append(2 ** i)
            self.log.append(math.log(i))
            self.nlog.append(i * math.log(i))
            self.poly.append(i ** 2)
            self.exp3.append(3 ** i)

        with open("report/assets/results.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                ["Size", "CSP Path Length", "CSP Time Taken", "CSP Memory Usage", "RL Path Length", "RL Time Taken",
                 "RL Memory Usage"])
            for i in range(len(self.csp_size_arr)):
                if self.rl_step_arr[i] is None:
                    step = "N/A"
                else:
                    step = self.rl_step_arr[i]
                writer.writerow(
                    [self.csp_size_arr[i], self.csp_step_arr[i],
                     self.csp_time_arr[i], self.csp_mem_arr[i], step,
                     self.rl_time_arr[i],
                     self.rl_mem_arr[i]])
            for i in range(len(self.csp_size_arr), len(self.rl_size_arr)):
                if self.rl_step_arr[i] is None:
                    step = "N/A"
                else:
                    step = self.rl_step_arr[i]
                writer.writerow(
                    [self.rl_size_arr[i], "N/A", "N/A", "N/A", step, self.rl_time_arr[i], self.rl_mem_arr[i]])

    def rolling_check_stdout(self, string: str):
        steps = ""

        for idx in range(len(string)):
            if string[idx] == "S":
                if string[idx:idx + 6] == "Steps:":
                    for char in string[idx + 6:]:
                        if char == '\\':
                            break
                        else:
                            steps += char

        print('steps', steps)
        return int(steps)

    def rolling_check_stderr(self, string: str):
        time = ""
        mem = ""

        for idx in range(len(string)):
            if string[idx] == "U":
                if string[idx:idx + 18] == "Usertime(seconds):":
                    for char in string[idx + 18:]:
                        if char == '\\':
                            break
                        else:
                            time += char

            if string[idx] == "M":
                if string[idx:idx + 31] == "Maximumresidentsetsize(kbytes):":
                    for char in string[idx + 31:]:
                        if char == "\\":
                            break
                        else:
                            mem += char

        return float(time), int(mem)

    def read_rl_file(self, filename):
        file = open(filename, "r")

        stdout = ""
        stderr = ""

        out_hit = False
        err_hit = False
        for line in file:
            separated = line.split(sep=" ")
            for word in separated:
                if word[:6] == "stdout":
                    stdout = word
                    out_hit = True
                elif word[:6] == "stderr":
                    err_hit = True
                    stderr = word
                elif out_hit and not err_hit:
                    stdout += word
                else:
                    stderr += word

        return stdout, stderr

    def read_csp_file(self, filename):
        file = open(filename, "r")

        line_num = 1
        steps = 1  # Since we're counting arrows, need to add 1 for init
        time = 0.0
        mem = 0.0
        for line in file:
            if line_num == 6:
                words = line.split(sep=" ")
                for word in words:
                    if word == "->":
                        steps += 1
                        line_num += 1
            elif line_num == 17:
                time = float(line[10:-2])
                line_num += 1
            elif line_num == 18:
                mem = float(line[22:-3])
                line_num += 1
            else:
                line_num += 1
                continue

        return steps, time, mem


class GraphMaker:
    def __init__(self, parsed_data):
        self.pp =  parsed_data
        self.make_general_graph()
        self.make_steps_graph()
        self.make_memory_graph()

    def make_general_graph(self):
        fig, ax = plt.subplots()
        ax.plot(self.pp.rl_size_arr, self.pp.rl_time_arr, color='red', label="RL Time Taken")
        ax.plot(self.pp.csp_size_arr, self.pp.csp_time_arr, color='blue', label="CSP Time Taken")

        ax.plot(self.pp.rl_size_arr, self.pp.linear, color='green', label="O(n)")
        # ax.plot(rl_size_arr, exp, color='black', label="O(2^n)")
        # ax.plot(rl_size_arr, exp3, color='brown', label="O(3^n)")
        ax.plot(self.pp.rl_size_arr, self.pp.log, color='purple', label="O(log n)")
        ax.plot(self.pp.rl_size_arr, self.pp.nlog, color='pink', label="O(nlog n)")
        ax.plot(self.pp.rl_size_arr, self.pp.poly, color='gray', label="O(n^2)")
        ax.set_xlabel('Maze Size')
        ax.set_ylabel('Time Taken')
        ax.legend(loc=0)

        ax2 = ax.twinx()
        ax2.plot(self.pp.rl_size_arr, self.pp.rl_step_arr, label="RL Steps")
        ax2.plot(self.pp.csp_size_arr, self.pp.csp_step_arr, label="CSP Steps")
        ax2.set_ylabel("Number of Steps")
        ax2.legend(loc=1)

        plt.title('Maze Size vs Time Complexity and Accuracy')

        plt.savefig("TimeAndSteps.png", format="png")

        plt.clf()

    def make_steps_graph(self):
        fig, ax = plt.subplots()

        ax.plot(self.pp.rl_size_arr, self.pp.rl_step_arr, label="RL Steps")
        ax.plot(self.pp.csp_size_arr, self.pp.csp_step_arr, label="CSP Steps")
        ax.set_xlabel("Maze Size")
        ax.set_ylabel("Number of Steps")
        ax.legend(loc=1)

        plt.title('Maze Size vs Number of Steps')

        plt.savefig("StepsOnly.png", format="png")

        plt.clf()

    def make_memory_graph(self):
        fig, ax = plt.subplots()

        ax.plot(self.pp.rl_size_arr, self.pp.rl_mem_arr, label="RL Mem Usage")
        ax.plot(self.pp.csp_size_arr, self.pp.csp_mem_arr, label="CSP Mem Usage")
        ax.set_xlabel("Maze Size")
        ax.set_ylabel("Memory Usage")
        ax.legend(loc=1)

        plt.title('Maze Size vs Memory Usage')

        plt.savefig("MemOnly.png", format="png")

        plt.clf()


GraphMaker(ProfileParser())
