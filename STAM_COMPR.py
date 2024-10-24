# Read the content of the first file
with open('random_values.txt', 'r') as file1:
    lines_file1 = file1.readlines()

# Read the content of the second file
with open('results_file.txt', 'r') as file2:
    lines_file2 = file2.readlines()

# Merge lines from both files into new lines
merged_lines = []
for line1, line2 in zip(lines_file1, lines_file2):
    merged_lines.append('Anticipated Gesture: ' + str(line1.strip()) + ", " + 'Predicted Gesture: ' + str(line2.split(":")[0].strip()) + ', Success Percentage: ' + str(line2.split(":")[1].strip()))

# Write the merged lines to a new file
with open('merged_file.txt', 'w') as merged_file:
    for line in merged_lines:
        merged_file.write(line + '\n')
