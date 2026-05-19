import psutil
import pandas as pd
import numpy as np
import json
import time
import datetime
import os
from sklearn.ensemble import IsolationForest
import pickle

DATA_FILE = os.path.expanduser("~/Desktop/cyber-lab/data/ml_data.csv")
MODEL_FILE = os.path.expanduser("~/Desktop/cyber-lab/data/ml_model.pkl")

def collect_sample():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    try:
        connections = len(psutil.net_connections(kind='inet'))
    except:
        connections = 0
    processes = len(psutil.pids())
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        'timestamp': timestamp,
        'cpu': cpu,
        'memory': memory,
        'disk': disk,
        'connections': connections,
        'processes': processes
    }

def collect_training_data(samples=50):
    print(f"🧠 Collecting {samples} samples of your system behaviour...")
    print("This will take about 2 minutes. Keep using your system normally.\n")
    data = []
    for i in range(samples):
        sample = collect_sample()
        data.append(sample)
        print(f"  Sample {i+1}/{samples} — CPU: {sample['cpu']}% | Memory: {sample['memory']}% | Connections: {sample['connections']}")
        time.sleep(2)
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if os.path.exists(DATA_FILE):
        existing = pd.read_csv(DATA_FILE)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    print(f"\n✅ Saved {len(df)} total samples to {DATA_FILE}")
    return df

def train_model():
    if not os.path.exists(DATA_FILE):
        print("❌ No training data found. Run with --collect first.")
        return
    df = pd.read_csv(DATA_FILE)
    print(f"\n🔧 Training Isolation Forest on {len(df)} samples...")
    features = ['cpu', 'memory', 'disk', 'connections', 'processes']
    X = df[features].values
    model = IsolationForest(
        contamination=0.05,
        random_state=42,
        n_estimators=100
    )
    model.fit(X)
    with open(MODEL_FILE, 'wb') as f:
        pickle.dump(model, f)
    print(f"✅ Model trained and saved to {MODEL_FILE}")
    print(f"\n📊 Training Summary:")
    print(f"   Samples used: {len(df)}")
    print(f"   Features: {features}")
    print(f"   Algorithm: Isolation Forest")
    print(f"   Contamination: 5% (flags top 5% unusual readings)")
    scores = model.decision_function(X)
    print(f"   Avg anomaly score: {np.mean(scores):.3f}")
    print(f"\n🚀 ML model ready! Now run: python3 scripts/ml_detector.py")

if __name__ == '__main__':
    import sys
    if '--collect' in sys.argv:
        collect_training_data(50)
    elif '--train' in sys.argv:
        train_model()
    else:
        print("Usage:")
        print("  python3 scripts/ml_trainer.py --collect   # collect training data")
        print("  python3 scripts/ml_trainer.py --train     # train the model")
