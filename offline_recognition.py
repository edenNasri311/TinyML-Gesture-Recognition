import os
import sys
import numpy as np
import pandas as pd
import tensorflow as tf
import psutil

with open('stamm.txt', 'r') as file1:
    length_moves = int(file1.readline())

# os.remove('stamm.txt')
print("Value of length_moves:", length_moves)

# Get CPU usage
cpu_usage_begin = psutil.cpu_percent()
# Get memory usage
memory_usage_begin = psutil.virtual_memory().percent

# Set a fixed random seed value, for reproducibility, this will allow us to get
# the same random numbers each time the notebook is run
SEED = 1337
np.random.seed(SEED)
tf.random.set_seed(SEED)

# the list of gestures that data is available for
GESTURES = [
    "Test",
]

SAMPLES_PER_GESTURE = 70

NUM_GESTURES = len(GESTURES)

# create a one-hot encoded matrix that is used in the output.
ONE_HOT_ENCODED_GESTURES = np.eye(NUM_GESTURES)

inputs = []
outputs = []


# Return the move with at least 90% success, else return None.
def get_result_move(results_dict: dict) -> str:
    for move in results_dict:
        if results_dict[move] > 0.9:
            return move

    return None


# read each csv file and push an input and output
for gesture_index in range(NUM_GESTURES):
    gesture = GESTURES[gesture_index]

    output = ONE_HOT_ENCODED_GESTURES[gesture_index]

    df = pd.read_csv(gesture + ".csv")

    # calculate the number of gesture recordings in the file
    num_recordings = int(df.shape[0] / SAMPLES_PER_GESTURE)

    if length_moves != num_recordings:
        print(f"Mismatch detected - expected {length_moves} and received {num_recordings}. Exits.")
        sys.exit(1)

    for i in range(num_recordings):
        tensor = []
        for j in range(SAMPLES_PER_GESTURE):
            index = i * SAMPLES_PER_GESTURE + j
            # normalize the input data, between 0 to 1:
            # - acceleration is between: -4 to +4
            # - gyroscope is between: -100 to +100
            tensor += [
                (df['aX'][index] + 4) / 8,
                (df['aY'][index] + 4) / 8,
                (df['aZ'][index] + 4) / 8,
                (df['gX'][index] + 20) / 40,
                (df['gY'][index] + 20) / 40,
                (df['gZ'][index] + 20) / 40,
                (df['latitude'][index] + 90) / 180,  # Normalize latitude between 0 and 1
                (df['longitude'][index] + 180) / 360  # Normalize longitude between 0 and 1
            ]

        inputs.append(tensor)
        outputs.append(output)

# convert the list to numpy array
inputs = np.array(inputs)
outputs = np.array(outputs)

inputs = inputs.astype(np.float32)

interpreter = tf.lite.Interpreter(model_path="gesture_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
# Get CPU usage
cpu_usage_end = psutil.cpu_percent()
# Get memory usage
memory_usage_end = psutil.virtual_memory().percent

results_file = "results_file.txt"

with open(results_file, 'w') as output_file:
    for input in range(num_recordings):
        interpreter.set_tensor(input_details[0]['index'], [inputs[input]])
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])
        results_dict = {'Right': output_data[0][0], 'Left': output_data[0][1], 'Up': output_data[0][2],
                        'Down': output_data[0][3]}

        result_move = get_result_move(results_dict)
        if result_move is not None:
            print(f"#{str(input + 1)}. {result_move}: {results_dict[result_move]}\n")
            output_file.write(f"{result_move}: {results_dict[result_move]}\n")
        else:
            print(f"Input number {str(input + 1)} cannot be identified.\n")
            output_file.write(f"Input number {str(input + 1)} cannot be identified.\n")



print(f"CPU Usage: End: {cpu_usage_end}%, Start: {cpu_usage_begin}%, Total: {cpu_usage_end - cpu_usage_begin}%\n")
print(
    f"Memory Usage: End: {memory_usage_end}% Start: {memory_usage_begin}%, Total: {memory_usage_end - memory_usage_begin}%\n")
