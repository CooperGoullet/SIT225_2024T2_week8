import time
import traceback
import csv
from datetime import datetime
from arduino_iot_cloud import ArduinoCloudClient
import pandas as pd
import matplotlib.pyplot as plt

# Arduino Cloud Configuration
DEVICE_ID = "0629dcd4-8bd9-4b74-abb0-07954884af79"
SECRET_KEY = "Z!UrpQKrv4JzYInsw6NRRiTvw"

# Variables to store sensor data temporarily
x_data = []
y_data = []
z_data = []
N = 50  # Number of samples before updating the graph

# Callback functions for x, y, z-axis data changes
def on_x_changed(client, value):
    if value is not None:
        x_data.append(value)
        print(f"Received X value: {value}")
    store_data_if_ready()

def on_y_changed(client, value):
    if value is not None:
        y_data.append(value)
        print(f"Received Y value: {value}")
    store_data_if_ready()

def on_z_changed(client, value):
    if value is not None:
        z_data.append(value)
        print(f"Received Z value: {value}")
    store_data_if_ready()

# Function to store data in CSV if N samples are collected
def store_data_if_ready():
    if len(x_data) >= N and len(y_data) >= N and len(z_data) >= N:
        timestamp = datetime.now()
        df = pd.DataFrame({
            'Timestamp': [timestamp] * N,
            'Accel X': x_data[-N:],
            'Accel Y': y_data[-N:],
            'Accel Z': z_data[-N:]
        })
        filename = f"Live_data_{timestamp.strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"Saved {filename}")
        
        # Plot the data and save the graph
        plot_graph(filename)
        plot_last_n_values(filename, N)

        # Clear the data lists after saving and plotting
        del x_data[:]
        del y_data[:]
        del z_data[:]

def plot_graph(filename):
    data = pd.read_csv(filename)
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    
    # Calculate the start and end times
    start_time = data['Timestamp'].min()
    end_time = data['Timestamp'].max()

    plt.figure(figsize=(12, 6))
    plt.plot(data['Timestamp'], data['Accel X'], label='Accel X', color='r')
    plt.plot(data['Timestamp'], data['Accel Y'], label='Accel Y', color='g')
    plt.plot(data['Timestamp'], data['Accel Z'], label='Accel Z', color='b')
    plt.xlabel('Time')
    plt.ylabel('Acceleration')
    plt.title('Accelerometer Data Over Time')
    plt.legend()
    plt.tight_layout()

    # Set the x-axis to only show the time range of the recorded data
    plt.xlim([start_time, end_time])

    # Save the plot as a PNG file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plt.savefig(f'accelerometer_plot_{timestamp}.png')
    plt.close() 

# Function to plot the last N values from a CSV file and save it as a PNG
def plot_last_n_values(filename, amount_to):
    data = pd.read_csv(filename)
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    
    last_n_data = data.tail(amount_to)
    
    # Calculate the start and end times for the last N data points
    start_time = last_n_data['Timestamp'].min()
    end_time = last_n_data['Timestamp'].max()

    plt.figure(figsize=(12, 6))
    plt.plot(last_n_data['Timestamp'], last_n_data['Accel X'], label='Accel X', color='r')
    plt.plot(last_n_data['Timestamp'], last_n_data['Accel Y'], label='Accel Y', color='g')
    plt.plot(last_n_data['Timestamp'], last_n_data['Accel Z'], label='Accel Z', color='b')
    plt.xlabel('Time')
    plt.ylabel('Acceleration')
    plt.title(f'Accelerometer Data Over Time (Last {amount_to} Values)')
    plt.legend()
    plt.tight_layout()

    # Set the x-axis to only show the time range of the last N data points
    plt.xlim([start_time, end_time])

    # Save the plot as a PNG file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    plt.savefig(f'last_n_accelerometer_plot_{timestamp}.png')
    plt.close()  
    
def create_client():
    return ArduinoCloudClient(
        device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY
    )

def main():
    print("Starting main function")

    # Instantiate Arduino cloud client
    client = create_client()

    # Register with cloud variables and listen for changes
    client.register("x_value", value=None, on_write=on_x_changed)
    client.register("y_value", value=None, on_write=on_y_changed)
    client.register("z_value", value=None, on_write=on_z_changed)
    
    # Start the cloud client to listen for data
    client.start()

def retry_main_function(max_retries, delay):
    retry_count = 0
    while retry_count < max_retries:
        try:
            main()
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            retry_count += 1
            print(f"Retrying {retry_count}/{max_retries}...")
            time.sleep(delay)  # Wait before retrying

if __name__ == "__main__":
    retry_main_function(5, 5)
