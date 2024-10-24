import os

def file_similarity(file1_path, file2_path):
    # Open both files
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        # Read lines from both files
        file1_lines = file1.readlines()
        file2_lines = file2.readlines()

        # Check if line counts are different
        if len(file1_lines) != len(file2_lines):
            return 0.0  # Files are not similar if line counts are different

        # Check line by line for similarity
        identical_lines = sum(1 for line1, line2 in zip(file1_lines, file2_lines) if line1 == line2)

        # Calculate the percentage of similarity
        total_lines = len(file1_lines)
        similarity_percentage = (identical_lines / total_lines) * 100

        return similarity_percentage


file1_path = 'random_values.txt'
file2_path = 'results_file.txt'
if os.path.isfile(file1_path) and os.path.isfile(file2_path):
    similarity_percentage = file_similarity(file1_path, file2_path)
    print(f"Percentage of similarity: {similarity_percentage:.2f}%")
else:
    print(f"Files {file1_path} or {file2_path} not exist!.")
