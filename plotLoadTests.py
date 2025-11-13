import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv('loadTests/loadTesting.csv')

# Convert timestamp (epoch ms) to datetime
df['datetime'] = pd.to_datetime(df['timeStamp'], unit='ms')

# Sort by datetime to ensure the plot line is correct
df = df.sort_values('datetime')

# Create a figure with two subplots (side by side)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Plot response time (elapsed) over actual datetime
ax1.plot(df['datetime'], df['elapsed'], marker='o', linestyle='-', alpha=0.7)
ax1.set_title('Response Time (ms) Over Time')
ax1.set_xlabel('Datetime')
ax1.set_ylabel('Elapsed Time (ms)')
ax1.grid(True)

# Plot histogram of response times
ax2.hist(df['elapsed'], bins=20, color='skyblue', edgecolor='black')
ax2.set_title('Histogram of Response Times')
ax2.set_xlabel('Elapsed Time (ms)')
ax2.set_ylabel('Frequency')

plt.tight_layout()
plt.show()