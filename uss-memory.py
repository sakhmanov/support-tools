import os
import psutil
import subprocess 
from prettytable import PrettyTable

# The script is using USS memory metrics instead of RSS 
# https://gmpy.dev/blog/2016/real-process-memory-and-environ-in-python

def bytes_to_shortest_unit(byte):
    units = ["bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    unit_index = 0
    while byte >= 1024 and unit_index < len(units) - 1:
        byte /= 1024
        unit_index += 1
    return str(round(byte, 3)) + " " + units[unit_index]

# Get list of processes 
pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]

# Get memory utilization of each process 
memory_usage = {}
swap_usage = {}
for pid in pids:
    try:
        process = psutil.Process(int(pid))
#        memory_usage[process.name()] = process.memory_info().rss
        memory_usage[process.name()] = process.memory_full_info().uss
        swap_usage[process.name()] = process.memory_full_info().swap
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

# Aggregate memory utilization by process name
aggregated_memory_usage = {}
for proc, mem in memory_usage.items():
    if proc in aggregated_memory_usage:
        aggregated_memory_usage[proc] += mem
    else:
        aggregated_memory_usage[proc] = mem

# Aggregate swap utilization by process name
aggregated_swap_usage = {}
for proc, mem in swap_usage.items():
    if proc in aggregated_swap_usage:
        aggregated_swap_usage[proc] += mem
    else:
        aggregated_swap_usage[proc] = mem
        
# Sort by memory size
sorted_memory_usage = sorted(aggregated_memory_usage.items(), key=lambda x: x[1], reverse=True)[0:14]

# Create a PrettyTable instance
table = PrettyTable()

# Add column names
table.field_names = ["Process Name", "Unique Set Size", "Swap Usage", "-Xss", "-Xms", "-Xmx", "CPU Quota"]

# Add row data
for proc, mem in sorted_memory_usage:
    cmdline=[x.cmdline() for x in psutil.process_iter() if x.name() == proc][0]
    xms=''
    xmx=''
    xss=''
    # Iterate through the command line arguments
    for arg in cmdline:
        # Check if the argument starts with '-Xss or -Xms or -Xmx'
        if arg.startswith('-Xss'):
            xss=arg[4:]
        if arg.startswith('-Xms'):
            xms=arg[4:]
        if arg.startswith('-Xmx'):
            xmx=arg[4:]

    # Define the command and the variables
    command = "systemctl cat {proc} 2> /dev/null | grep ^CPUQuota | cut -f2 -d="

    # Execute the command
    output = subprocess.check_output(command.format(proc=proc), shell=True)

    table.add_row([proc, 
                   bytes_to_shortest_unit(mem), 
                   bytes_to_shortest_unit(aggregated_swap_usage[proc]),
                   xss, 
                   xms, 
                   xmx,
                   output.decode().strip()])

# Print the table
print(table)
