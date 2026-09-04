import serial
import csv
import time
import matplotlib.pyplot as plt

# --- CONFIGURATION ---
SERIAL_PORT = '/dev/cu.usbserial-0001' # MUST MATCH YOUR PORT
BAUD_RATE = 115200
FILENAME = "dataset_metal.csv" 
NUM_SAMPLES_TO_COLLECT = 100 
EXPECTED_LENGTH = 600 

def log_data():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=3)
        print(f"Connected to {SERIAL_PORT}. Waiting for ESP32...")
        time.sleep(2) 
        ser.reset_input_buffer()

        # --- SET UP THE LIVE GRAPH ---
        plt.ion() # Turn on interactive mode
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.set_title(f"Live Echo QA: {FILENAME}")
        ax.set_xlabel("Time (Milliseconds)")
        ax.set_ylabel("Voltage (0-4095)")
        ax.set_ylim(0, 4095)
        ax.set_xlim(0, 3.0) # Lock X-axis to our 3.0ms cutoff
        ax.grid(True)
        
        # Create an empty blue line that we will update on every loop
        live_line, = ax.plot([], [], color='blue')
        plt.show() # Pop the window open

        # --- START LOGGING ---
        with open(FILENAME, mode='w', newline='') as file:
            writer = csv.writer(file)
            samples_collected = 0
            
            print(f"\n--- READY TO LOG {FILENAME} ---")
            print("Adjust your material, then press Enter to fire the sensor.")
            print("Type 'q' and press Enter to quit early.\n")

            while samples_collected < NUM_SAMPLES_TO_COLLECT:
                user_input = input(f"[{samples_collected}/{NUM_SAMPLES_TO_COLLECT}] Press Enter to capture... ")
                
                if user_input.lower() == 'q':
                    print("Quitting early...")
                    break
                
                # Command the ESP32 to fire
                ser.write(b'1')
                
                wave_data = []
                waiting_for_start = True
                
                while True:
                    line_bytes = ser.readline()
                    if not line_bytes:
                        print("  -> Timeout: ESP32 didn't respond. Try again.")
                        break 
                        
                    line = line_bytes.decode('utf-8').strip()
                    
                    if waiting_for_start:
                        if line == "START":
                            waiting_for_start = False
                    else:
                        if line == "END":
                            break
                        if line.isdigit():
                            wave_data.append(int(line))
                
                # Verify, Save, and Graph
                if len(wave_data) == EXPECTED_LENGTH:
                    writer.writerow(wave_data)
                    samples_collected += 1
                    print(f"  -> Success! Wave {samples_collected} saved.")
                    
                    # Instantly update the live graph
                    time_ms = [i * 0.005 for i in range(EXPECTED_LENGTH)]
                    live_line.set_xdata(time_ms)
                    live_line.set_ydata(wave_data)
                    plt.pause(0.01) # Force the window to physically refresh
                    
                elif len(wave_data) > 0:
                    print(f"  -> Error: Corrupted wave (caught {len(wave_data)} samples). Not saved.")
                        
        print(f"\nFinished! Safely closed and saved {samples_collected} waves to {FILENAME}")
        plt.ioff() # Turn off interactive mode
        plt.show() # Keep the final wave on screen until you close it manually
        ser.close()
        
    except Exception as e:
        print(f"Error: {e}")
        print("CRITICAL: Is the Arduino Serial Monitor closed? Is the COM port correct?")

if __name__ == "__main__":
    log_data()