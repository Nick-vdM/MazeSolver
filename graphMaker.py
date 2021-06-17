# importing the required module
import matplotlib.pyplot as plt
import math
import random
from datetime import datetime
random.seed(datetime.now())


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

time_arr = []
mem_arr = []
size_arr = []

for i in range(5, 325, 10):
    out, err = read_rl_file(f"profiles/rl/{i}")
    time, mem = rolling_check_stderr(err)
    time_arr.append(time)
    mem_arr.append(mem)
    size_arr.append(i)

for i in range(len(time_arr)):
    print(f"({size_arr[i]}, {time_arr[i]}, {mem_arr[i]})")

#Size
x = [] 
for i in range(0,10000):
    x.insert(len(x),i)

maxSize = len(x)
print(maxSize)

#Time taken
y = [] 
for i in range(0,(maxSize)*2,2):
    y.insert(len(y),i)

endValue = y[-1]

linearX = endValue/(maxSize-1)
linear = []
for i in range(0,maxSize):
    linear.insert(len(linear),i*linearX)
    
expCoef = endValue/((maxSize-1)**2)
exp = []
for i in range(0,maxSize):
    exp.insert(len(exp),(i**2)*expCoef)

logCoef = endValue/(math.log(maxSize-1,10))
log = []
for i in range(1,maxSize+1):
    log.insert(len(log),math.log(i,10)*logCoef)

nlogCoef = endValue/((maxSize-1)*math.log(maxSize-1,10))
nlog = []
for i in range(1,maxSize+1):
    nlog.insert(len(nlog),(i*math.log(i,10)*nlogCoef))

line = []
for i in range(0,maxSize):
    line.insert(len(line),endValue)

exp3Coef = endValue/((maxSize-1)**3)
exp3 = []
for i in range(0,maxSize):
    exp3.insert(len(exp3),(i**3)*exp3Coef)


plt.xlabel('Time')
plt.ylabel('Size')
plt.title('Size vs Time complexity')
  
plt.plot(x, y, color='red')
plt.plot(x, linear, color='blue')
plt.plot(x, exp, color='green')
plt.plot(x, log, color='black')
plt.plot(x, nlog, color='brown')
plt.plot(x, line, color='purple')
plt.plot(x, exp3, color='pink')

# function to show the plot
plt.show()


