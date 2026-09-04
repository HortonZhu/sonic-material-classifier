import pandas as pd
import numpy as np
import xgboost as xgb
import serial
import time
import os
import matplotlib.pyplot as plt

# finds directory of current file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "material_model.json")

SERIAL_PORT = '/dev/cu.usbserial-0001'
BAUD_RATE = 115200
target_names = ['Foam', 'Metal', 'Paper']

# load model
model = xgb.XGBClassifier()
model.load_model(MODEL_PATH)

# 2. FEATURE EXTRACTION
def get_features(raw_list):
    raw = pd.DataFrame([raw_list])
    feat = pd.DataFrame()
    feat['variance'] = raw.var(axis=1)
    feat['p2p'] = raw.max(axis=1) - raw.min(axis=1)
    feat['tail_std'] = raw.iloc[:, 300:].std(axis=1)
    feat['attack_std'] = raw.iloc[:, :200].std(axis=1)
    return feat

# 3. demo loop
try:
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
        print("port working")
        time.sleep(2) 
        
        plt.ion() 
        fig, ax = plt.subplots(figsize=(10, 4))
        
        while True:
            print("\n" + "="*30)
            
            # any button will trigger
            plt.waitforbuttonpress() 
            
            ser.reset_input_buffer()
            ser.write(b'1')

            wave_data = []
            capture = False
            start_time = time.time()
            
            while (time.time() - start_time) < 2:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line == "START":
                    capture = True
                    continue
                if line == "END":
                    break
                if capture and line.isdigit():
                    wave_data.append(int(line))
            
            if len(wave_data) == 600:
                features = get_features(wave_data)
                prediction = model.predict(features)[0]
                probs = model.predict_proba(features)[0]
                material = target_names[prediction]
                conf = probs[prediction] * 100
                
                print(f"Material: {material.upper()}")

                ax.clear()
                ax.plot(wave_data, color='blue')
                ax.set_title(f"Result: {material}")
                ax.set_ylim(0, 4095)
                ax.grid(True, alpha=0.3)
                plt.draw()
                plt.pause(0.1) 
            else:
                print(f"ERROR: Only got {len(wave_data)} points.")

except Exception as e:
    print(f"Error: {e}")