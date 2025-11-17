import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import re

# List of CSVs and their titlesdx
csv_files = [
    'loadTests/loadTestingFunc2Thread10.csv',
    'loadTests/loadTestingFunc2Thread50.csv',
    'loadTests/loadTestingFunc2Thread500.csv',
]

LOOP_COUNT = 10
def extract_info(filename):
    # Extract sensor, batch, and thread/user info from filename
    sensor = re.search(r'Sensor(\d+)', filename)
    batch = re.search(r'Batch(\d+)', filename)
    thread = re.search(r'Thread(\d+)', filename)
    sensor_count = sensor.group(1) if sensor else '?'
    batch_size = batch.group(1) if batch else '?'
    user_count = thread.group(1) if thread else '10'
    return sensor_count, batch_size, user_count

fig = plt.figure(figsize=(28, 24))
# 3 columns: Response Time | Histogram | Failures
gs = gridspec.GridSpec(len(csv_files), 3, width_ratios=[3, 1.5, 1.5])

for idx, csv in enumerate(csv_files):
    df = pd.read_csv(csv)
    df['datetime'] = pd.to_datetime(df['timeStamp'], unit='ms')
    df = df.sort_values('datetime')
    df['success_bool'] = df['success'].astype(str).str.strip().str.upper() == 'TRUE'
    df['failure'] = ~df['success_bool']
    total_rows = len(df)
    num_failures = df['failure'].sum()
    failure_percent = (num_failures / total_rows) * 100
    sensor_count, batch_size, user_count = extract_info(csv)
    invocations = int(user_count) * LOOP_COUNT
    # --- Left: Response time over time ---
    ax_time = fig.add_subplot(gs[idx, 0])
    ax_time.plot(df['datetime'], df['elapsed'], marker='o', linestyle='-', alpha=0.7)
    ax_time.set_title('Response Time (ms) Over Time', fontsize=14)
    ax_time.set_xlabel('Datetime')
    ax_time.set_ylabel('Elapsed Time (ms)')
    ax_time.grid(True)

    # --- Middle: Histogram ---
    ax_hist = fig.add_subplot(gs[idx, 1])
    ax_hist.hist(df['elapsed'], bins=20, color='skyblue', edgecolor='black')
    ax_hist.set_title('Elapsed Time Histogram', fontsize=14)
    ax_hist.set_xlabel('Elapsed (ms)')
    ax_hist.set_ylabel('Frequency')
    ax_hist.tick_params(axis='both', which='major', labelsize=10)

    # --- Right: Failures bar graph ---
    ax_bar = fig.add_subplot(gs[idx, 2])
    bar_positions = [0, 1]
    bar1 = ax_bar.bar(bar_positions[0], num_failures, color='red', alpha=0.6, width=0.3, label='Failures')
    ax_bar.set_ylabel('Failures (count)', color='red')
    ax_bar.set_ylim(0, max(total_rows, 1))
    ax_bar.set_xticks(bar_positions)
    ax_bar.set_xticklabels(['Failures', '% Failures'])

    # Annotate number of failures
    for rect in bar1:
        height = rect.get_height()
        ax_bar.annotate(f'{int(height)}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 5),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=12, fontweight='bold', color='red')

    # Secondary y-axis for percentage
    ax_bar2 = ax_bar.twinx()
    bar2 = ax_bar2.bar(bar_positions[1], failure_percent, color='orange', alpha=0.5, width=0.3, label='% Failures')
    ax_bar2.set_ylabel('Failures (%)', color='orange')
    ax_bar2.set_ylim(0, 100)

    # Annotate percentage
    for rect in bar2:
        height = rect.get_height()
        ax_bar2.annotate(f'{height:.1f}%',
                         xy=(rect.get_x() + rect.get_width() / 2, height),
                         xytext=(0, 5),
                         textcoords="offset points",
                         ha='center', va='bottom', fontsize=12, fontweight='bold', color='orange')

    # Hide the unused bar slot for each axis
    if num_failures == 0:
        ax_bar.set_ylim(0, 1)
    if failure_percent == 0:
        ax_bar2.set_ylim(0, 1)

    # --- Row title with test parameters ---
    ax_time.text(0.5, 1.18,
        f'Users: {user_count} Invocations: {invocations}',
        transform=ax_time.transAxes,
        ha='center', va='bottom', fontsize=16, fontweight='bold', bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))

plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.suptitle('Load Test Results Overview Task 2', fontsize=28, fontweight='bold')
plt.show()