import random

# Define the set of possible values
possible_values = ['Right', 'Left', 'Up', 'Down']
input_moves = input("Enter number of gestures: ")
length_moves = int(input_moves)
with open('stamm.txt', 'w') as file1:
    file1.write(f"{length_moves}")

# Write the random values to a file
with open('random_values.txt', 'w') as file:
    random_values = [random.choice(possible_values) for _ in range(length_moves)]
    file.write('\n'.join(random_values))
    file.write("\n")

    print("Random values have been written to 'random_values.txt'.")

