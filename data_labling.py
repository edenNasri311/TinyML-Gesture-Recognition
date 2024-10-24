import os

direction_dict = {"r": "Right", "l": "Left", "u": "Up", "d": "Down", "t": "Test"}

# Define input directory based on user input
while True:
    direction = input("Enter the desired direction (r, l, u, d, t): ").lower()
    input_directory = direction

    # Validate user input
    if input_directory not in ['r', 'l', 'u', 'd', 't']:
        print("Invalid direction. Please enter one of the following: r, l, u, d, t")
    else:
        break

output_file_path = f"{direction_dict[direction]}.csv"

with open(output_file_path, 'w') as output_file:
    # Initialize variables to track the gesture sequence and label
    output_file.write(f"timestamp,aX,aY,aZ,gX,gY,gZ,button,latitude,longitude\n")

    # Iterate over files in the input directory
    for filename in os.listdir(direction_dict[input_directory]):
        if filename.endswith(".txt"):
            input_file_path = os.path.join(direction_dict[input_directory], filename)

            # Open the input file for reading
            with open(input_file_path, 'r') as input_file:
                # Read all lines from the input file
                input_lines = input_file.readlines()

                gesture_samples = []

                # Iterate through each line in the input file
                for line in input_lines:
                    # Split the line into individual values
                    values = line.strip().split(',')
                    # Extract the last value (button press indicator)
                    button_press = int(values[-1])

                    # Check if the button is pressed
                    if button_press == 1:
                        # If button is pressed, add the sample to the gesture sequence
                        gesture_samples.append(values)  # Include all values

                    elif button_press == 0 and gesture_samples:
                        # If button is released, and we have a gesture sequence
                        # Label the entire sequence as the direction and write it to the output file
                        if len(gesture_samples) < 70:
                            for i in range(70 - len(gesture_samples)):
                                gesture_samples.append([
                                                           "0"] * 10)  # 10 values: timestamp, aX, aY, aZ, gX, gY, gZ, button, latitude, longitude

                        elif len(gesture_samples) > 70:
                            gesture_samples = gesture_samples[0:70]

                        if len(gesture_samples) > 1:  # Only write if there are multiple samples in the sequence
                            for sample in gesture_samples:
                                # Add the timestamp to each sample
                                labeled_sample = ','.join(sample) + '\n'
                                output_file.write(labeled_sample)
                        gesture_samples = []  # Reset gesture_samples

            # if input_directory == "t":
            #     os.remove(input_file_path)
