import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("assignmentResults.csv")

ax=df.plot(kind='scatter', x='Size', y=['CSP Time Taken', 'RL Time Taken'])
ax.set_ylabel('Time')
plt.title('Maze Size vs Time Taken')
plt.tight_layout()
plt.show()


ax=df.plot(kind='line', x='Size', y=['RL Path Length','CSP Path Length'])

ax.set_ylabel('Path Length')
plt.title('Maze Size Vs Path Length')
plt.tight_layout()
plt.show()

ax=df.plot(kind='line', x='Size', y=['RL Memory Usage','CSP Memory Usage'])

ax.set_ylabel('Memory Usage')
plt.title('Maze Size Vs memory Usage')
plt.tight_layout()
plt.show()

