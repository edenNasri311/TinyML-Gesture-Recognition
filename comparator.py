# Read the content of the first file
with open('random_values.txt', 'r') as file1:
    lines_file1 = file1.readlines()

# Read the content of the second file
with open('results_file.txt', 'r') as file2:
    lines_file2 = file2.readlines()

# with open('cpu_mem_usage.txt', 'r') as usage_file:
#     line = usage_file.readline().strip()
#     data = line.split(",")
#
#     cpu_usage_begin = float(data[0])
#     cpu_usage_end = float(data[1])
#     memory_usage_begin = float(data[2])
#     memory_usage_end = float(data[3])

# Merge lines from both files into new lines
merged_lines = []
success_counter = 0
for line1, line2 in zip(lines_file1, lines_file2):
    merged_lines.append('Anticipated Gesture: ' + str(line1.strip()) + ", " + 'Predicted Gesture: ' + str(line2.split(":")[0].strip()) + ', Success Percentage: ' + str(line2.split(":")[1].strip()))
    if line1.strip() == line2.split(":")[0].strip():
        success_counter += 1

merged_lines.append("\n***********************************************************************************\n")
merged_lines.append(f"Percentage of successful gestures: {(success_counter/(len(lines_file2))) * 100}%")
# merged_lines.append("\n***********************************************************************************\n")
# merged_lines.append(f"CPU Usage: End: {cpu_usage_end:.5f}%, Start: {cpu_usage_begin:.5f}%, Total: {(cpu_usage_end - cpu_usage_begin):.5f}%\n")
# merged_lines.append(f"Memory Usage: End: {memory_usage_end:.5f}% Start: {memory_usage_begin:.5f}%, Total: {(memory_usage_end - memory_usage_begin):.5f}%\n")


# Write the merged lines to a new file
with open('merged_file.txt', 'w') as merged_file:
    for line in merged_lines:
        merged_file.write(line + '\n')
