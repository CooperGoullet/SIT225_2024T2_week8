import cv2
import time
import traceback
import csv
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from arduino_iot_cloud import ArduinoCloudClient
import threading

# Arduino Cloud Configuration
DEVICE_ID = "0629dcd4-8bd9-4b74-abb0-07954884af79"
SECRET_KEY = "Z!UrpQKrv4JzYInsw6NRRiTvw"

# Variables to store sensor data temporarily
x_data = []
y_data = []
z_data = []
time_data = []

# Initialize the webcam
cap = cv2.VideoCapture(0)

# Callback functions for x, y, z
def on_x_changed(client, value):
    if value is not None:
        x_data.append(value)
        time_data.append(datetime.now())
        print(f"Received X value: {value}")

def on_y_changed(client, value):
    if value is not None:
        y_data.append(value)
        print(f"Received Y value: {value}")

def on_z_changed(client, value):
    if value is not None:
        z_data.append(value)
        print(f"Received Z value: {value}")

def create_client():
    return ArduinoCloudClient(
        device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY
    )

def start_client(client):
    # Register with cloud variables and listen for changes
    client.register("x_value", value=None, on_write=on_x_changed)
    time.sleep(0.5)
    client.register("y_value", value=None, on_write=on_y_changed)
    time.sleep(0.5)
    client.register("z_value", value=None, on_write=on_z_changed)
    time.sleep(0.5)

    # Start the cloud client to listen for data
    client.start()

def capture_image(sequence_number):
    ret, frame = cap.read()
    if ret:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        image_filename = f"{sequence_number}_{timestamp}.jpg"
        cv2.imwrite(image_filename, frame)
        print(f"Captured image saved as {image_filename}")
        return image_filename, timestamp
    return None, None

def save_data_and_graph(sequence_number, timestamp):
    # Convert data to a DataFrame
    data_points = pd.DataFrame({
        'Time': time_data,
        'Acc_X': x_data,
        'Acc_Y': y_data,
        'Acc_Z': z_data
    })
    
    csv_filename = f"{sequence_number}_{timestamp}.csv"
    # Save data to CSV
    data_points.to_csv(csv_filename, index=False)
    print(f"Data saved to {csv_filename}")

    # Plot the data
    plt.figure()
    plt.plot(data_points['Acc_X'], label='Acc_X')
    plt.plot(data_points['Acc_Y'], label='Acc_Y')
    plt.plot(data_points['Acc_Z'], label='Acc_Z')
    plt.legend()
    plt.title(f"Accelerometer Data - {timestamp}")
    plt_filename = f"{sequence_number}_{timestamp}.png"
    plt.savefig(plt_filename)
    plt.close()
    print(f"Graph saved as {plt_filename}")

async def main():
    print("Starting main function")

    # Instantiate Arduino cloud client
    client = create_client()
    client_thread = threading.Thread(target=start_client, args=(client,))
    client_thread.start()

def retry_main_function(max_retries, delay):
    retry_count = 0
    while retry_count < max_retries:
        try:
            asyncio.run(main())
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            traceback.print_exc()
            retry_count += 1
            print(f"Retrying {retry_count}/{max_retries}...")
            time.sleep(delay)

if __name__ == "__main__":
    retry_main_function(5, 5)

    sequence_number = 1
    activity_data = []

    while sequence_number <= 180: 
        print(f"Starting capture for sequence {sequence_number}")

        # Capture an image
        image_filename, timestamp = capture_image
