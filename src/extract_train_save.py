import pandas as pd
import numpy as np
import xgboost as xgb
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report
import os

# mapping: foam = 0, metal = 1, paper = 2
file_map = {
    0: ['foam_1.csv', 'foam_2.csv'],
    1: ['metal_1.csv', 'metal_2.csv'],
    2: ['paper_1.csv', 'paper_2.csv']
}

def load_data():
    all_data = []
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    for label, files in file_map.items():
        for f in files:
            file_path = os.path.join(base_dir, f)
            if os.path.exists(file_path):
                df = pd.read_csv(file_path, header=None)
                df['target'] = label
                all_data.append(df)
            else:
                print(f"{f} not found")
    
    if not all_data:
        raise ValueError("csv not found")
    return pd.concat(all_data, ignore_index=True)

# feature extraction
def extract_features(data_df):
    raw = data_df.drop('target', axis=1)
    feat = pd.DataFrame()
    
    feat['variance'] = raw.var(axis=1) # Overall signal energy
    feat['p2p'] = raw.max(axis=1) - raw.min(axis=1) # Total swing
    feat['tail_std'] = raw.iloc[:, 300:].std(axis=1) # ending std
    feat['attack_std'] = raw.iloc[:, :200].std(axis=1) # starting std
    
    return feat

# train model on 100% data
df = load_data()
X = extract_features(df)
y = df['target']

# using XGBoost
model_final = xgb.XGBClassifier(
    objective='multi:softprob', 
    num_class=3,
    random_state=42
)

model_final.fit(X, y)

# save model to material_model.json
model_filename = "material_model.json"
model_final.save_model(model_filename)
