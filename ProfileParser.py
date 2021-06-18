# importing the required module
import matplotlib.pyplot as plt
import math
import random
from datetime import datetime
import csv
random.seed(datetime.now())

highest_rl_reached = 505 + 1
highest_csp_reached = 355 + 1


def rolling_check_stdout(string: str):
    steps = ""

    for idx in range(len(string)):
        if string[idx] == "S":
            if string[idx:idx + 6] == "Steps:":
                for char in string[idx + 6:]:
                    if char == '\\':
                        break
                    else:
                        steps += char

    return int(steps)


def rolling_check_stderr(string: str):
    time = ""
    mem = ""

    for idx in range(len(string)):
        if string[idx] == "U":
            if string[idx:idx+18] == "Usertime(seconds):":
                for char in string[idx+18:]:
                    if char == '\\':
                        break
                    else:
                        time += char

        if string[idx] == "M":
            if string[idx:idx+31] == "Maximumresidentsetsize(kbytes):":
                for char in string[idx+31:]:
                    if char == "\\":
                        break
                    else:
                        mem += char

    return float(time), int(mem)


def read_rl_file(filename):
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


def read_csp_file(filename):
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


rl_time_arr = []
rl_mem_arr = []
rl_step_arr = []
rl_size_arr = []

for i in range(5, highest_rl_reached, 10):
    out, err = read_rl_file(f"profiles/rl/{i}")
    time, mem = rolling_check_stderr(err)
    steps = rolling_check_stdout(out)
    rl_time_arr.append(time)
    rl_mem_arr.append(mem)
    if steps < 1000:
        rl_step_arr.append(steps)
    else:
        rl_step_arr.append(None)
    rl_size_arr.append(i)

for i in range(len(rl_time_arr)):
    print(f"({rl_size_arr[i]}, {rl_time_arr[i]}, {rl_mem_arr[i]}, {rl_step_arr[i]})")

csp_time_arr = []
csp_mem_arr = []
csp_step_arr = []
csp_size_arr = []

for i in range(5, highest_csp_reached, 10):
    steps, time, mem = read_csp_file(f"profiles/csp/{i}")
    csp_time_arr.append(time)
    csp_mem_arr.append(mem)
    csp_step_arr.append(steps)
    csp_size_arr.append(i)

for i in range(len(csp_time_arr)):
    print(f"({csp_size_arr[i]}, {csp_time_arr[i]}, {csp_mem_arr[i]}, {csp_step_arr[i]})")

linear = []
exp = []
log = []
nlog = []
poly = []
exp3 = []
for i in range(5, 506, 10):
    linear.append(i)
    exp.append(2**i)
    log.append(math.log(i))
    nlog.append(i*math.log(i))
    poly.append(i**2)
    exp3.append(3**i)


with open("report/assets/results.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Size", "CSP Path Length", "CSP Time Taken", "CSP Memory Usage", "RL Path Length", "RL Time Taken", "RL Memory Usage"])
    for i in range(len(csp_size_arr)):
        if rl_step_arr[i] is None:
            step = "N/A"
        else:
            step = rl_step_arr[i]
        writer.writerow([csp_size_arr[i], csp_step_arr[i], csp_time_arr[i], csp_mem_arr[i], step, rl_time_arr[i], rl_mem_arr[i]])
    for i in range(len(csp_size_arr), len(rl_size_arr)):
        if rl_step_arr[i] is None:
            step = "N/A"
        else:
            step = rl_step_arr[i]
        writer.writerow([rl_size_arr[i], "N/A", "N/A", "N/A", step, rl_time_arr[i], rl_mem_arr[i]])

fig,ax=plt.subplots()
ax.plot(rl_size_arr, rl_time_arr, color='red', label="RL Time Taken")
ax.plot(csp_size_arr, csp_time_arr, color='blue', label="CSP Time Taken")

ax.plot(rl_size_arr, linear, color='green', label="O(n)")
# ax.plot(rl_size_arr, exp, color='black', label="O(2^n)")
# ax.plot(rl_size_arr, exp3, color='brown', label="O(3^n)")
ax.plot(rl_size_arr, log, color='purple', label="O(log n)")
ax.plot(rl_size_arr, nlog, color='pink', label="O(nlog n)")
ax.plot(rl_size_arr, poly, color='gray', label="O(n^2)")
ax.set_xlabel('Maze Size')
ax.set_ylabel('Time Taken')
ax.legend(loc=0)

ax2 = ax.twinx()
ax2.plot(rl_size_arr, rl_step_arr, label="RL Steps")
ax2.plot(csp_size_arr, csp_step_arr, label="CSP Steps")
ax2.set_ylabel("Number of Steps")
ax2.legend(loc=1)

plt.title('Maze Size vs Time Complexity and Accuracy')

plt.savefig("TimeAndSteps.png", format="png")

plt.clf()

fig,ax=plt.subplots()

ax.plot(rl_size_arr, rl_step_arr, label="RL Steps")
ax.plot(csp_size_arr, csp_step_arr, label="CSP Steps")
ax.set_xlabel("Maze Size")
ax.set_ylabel("Number of Steps")
ax.legend(loc=1)

plt.title('Maze Size vs Number of Steps')

plt.savefig("StepsOnly.png", format="png")

plt.clf()



fig,ax=plt.subplots()

ax.plot(rl_size_arr, rl_mem_arr, label="RL Mem Usage")
ax.plot(csp_size_arr, csp_mem_arr, label="CSP Mem Usage")
ax.set_xlabel("Maze Size")
ax.set_ylabel("Memory Usage")
ax.legend(loc=1)

plt.title('Maze Size vs Memory Usage')

plt.savefig("MemOnly.png", format="png")

plt.clf()
