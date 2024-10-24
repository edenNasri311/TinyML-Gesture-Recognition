import os
import socket
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import datetime
import signal
import sys

# Use a style for the plot
style.use('fivethirtyeight')

direction_dict = {"r": "Right", "l": "Left", "u": "Up", "d": "Down", "t": "Test"}

# TCP Server class definition
class TCPServer:
    def __init__(self, host='192.168.0.101', port=57665):
        self.host = host
        self.port = port
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clientSockets = []
        self.running = True
        self.data = []
        self.movement = None

        # Prompt user to input the movement
        self.get_movement()

        # Generate a timestamped filename
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = f"imu_data_{direction_dict[self.movement]}_{timestamp}.txt"

        # Create directory if not exists
        self.directory = os.path.join(os.getcwd(), direction_dict[self.movement])
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # Open the file for writing
        self.file = open(os.path.join(self.directory, self.filename), "w")

    def get_movement(self):
        # Prompt user for movement input
        while True:
            movement = input("Enter the movement you are recording (r, l, u, d, t): ").lower()
            if movement in ['r', 'l', 'u', 'd', 't']:
                self.movement = movement
                break
            else:
                print("Invalid movement. Please enter one of the following: r, l, u, d, t")

    def handle_client_connection(self, clientSocket, address):
        print(f"Accepted connection from {address}")
        buffer = ""
        while self.running:
            try:
                data = clientSocket.recv(1024)
                if not data:
                    break
                buffer += data.decode()
                while "\r\n" in buffer:
                    message, buffer = buffer.split("\r\n", 1)
                    try:
                        parts = message.split(':')
                        if len(parts) > 1:
                            imu_data = list(map(float, parts[1].split(',')))
                            self.data.append(imu_data)
                            # Write to the pre-opened file
                            self.file.write(message + "\n")
                    except ValueError as e:
                        print(f"Error processing data '{message}': {e}")
            except ConnectionResetError:
                break
        print(f"Connection closed by {address}")
        clientSocket.close()
        self.clientSockets.remove(clientSocket)

    def start(self):
        self.serverSocket.bind((self.host, self.port))
        self.serverSocket.listen(5)
        print(f"Server listening on {self.host}:{self.port}")
        while self.running:
            try:
                clientSocket, address = self.serverSocket.accept()
                self.clientSockets.append(clientSocket)
                clientThread = threading.Thread(target=self.handle_client_connection, args=(clientSocket, address))
                clientThread.start()
            except KeyboardInterrupt:
                print("\nServer is shutting down.")
                self.running = False
        # Close all client sockets
        for cs in self.clientSockets:
            cs.close()
        # Close the server socket
        self.serverSocket.close()
        # Close the file
        self.file.close()
        print(f"Data recorded to {os.path.join(self.directory, self.filename)}")

def animate(i, server):
    # Ensure there's enough data to plot
    if len(server.data) > 0:
        data = np.array(server.data[-200:])  # Take the last 200 data points
        # Update the data for each line
        line1.set_data(data[:, 0], data[:, 1])  # Timestamp vs AccX
        line2.set_data(data[:, 0], data[:, 2])  # Timestamp vs AccY
        line3.set_data(data[:, 0], data[:, 3])  # Timestamp vs AccZ
        line4.set_data(data[:, 0], data[:, 7])  # Timestamp vs Button
        line5.set_data(data[:, 0], data[:, 8])  # Timestamp vs Latitude
        line6.set_data(data[:, 0], data[:, 9])  # Timestamp vs Longitude
        # Adjusting plot limits
        plt.xlim(np.min(data[:, 0]), np.max(data[:, 0]))  # Dynamically adjust x-axis limits
        plt.ylim(-3, 3)  # Fixed y-axis limits as per your specification

        # Update plot labels if needed
        plt.xlabel('Time')
        plt.ylabel('Acceleration (g) / GPS')
        plt.title('Real-time Acceleration and GPS Data')

def sigint_handler(signal, frame):
    print('\nCtrl+C detected. Exiting gracefully.')
    server.running = False
    plt.close()  # Close the plot window
    sys.exit(0)

if __name__ == '__main__':
    server = TCPServer()

    # Start the TCP server in a separate thread
    server_thread = threading.Thread(target=server.start, daemon=True)
    server_thread.start()

    # Set signal handler for Ctrl+C
    signal.signal(signal.SIGINT, sigint_handler)

    fig, ax = plt.subplots()
    line1, = ax.plot([], [], lw=2, label='Acc X')
    line2, = ax.plot([], [], lw=2, label='Acc Y')
    line3, = ax.plot([], [], lw=2, label='Acc Z')
    line4, = ax.plot([], [], lw=2, label='Button')
    line5, = ax.plot([], [], lw=2, label='Latitude')
    line6, = ax.plot([], [], lw=2, label='Longitude')
    plt.legend()

    ani = animation.FuncAnimation(fig, animate, fargs=(server,), interval=10, cache_frame_data=False)

    plt.show()

    # Wait for the server thread to join
    server_thread.join()
