import psutil
import numpy as np
import pickle
import datetime
import os

MODEL_FILE = os.path.expanduser("~/Desktop/cyber-lab/data/ml_model.pkl")

def get_current_stats():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    try:
        connections = len(psutil.net_connections(kind='inet'))
    except:
        connections = 0
    processes = len(psutil.pids())
    return [cpu, memory, disk, connections, processes]

def detect():
    if not os.path.exists(MODEL_FILE):
        return {"error": "Model not trained yet. Run ml_trainer.py first."}
    with open(MODEL_FILE, 'rb') as f:
        model = pickle.load(f)
    stats = get_current_stats()
    X = np.array([stats])
    prediction = model.predict(X)[0]
    score = model.decision_function(X)[0]
    is_anomaly = prediction == -1
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = {
        'timestamp': now,
        'cpu': stats[0],
        'memory': stats[1],
        'disk': stats[2],
        'connections': stats[3],
        'processes': stats[4],
        'anomaly_score': round(float(score), 4),
        'is_anomaly': is_anomaly,
        'status': '🔴 ANOMALY DETECTED' if is_anomaly else '✅ Normal'
    }
    return result

if __name__ == '__main__':
    print("🧠 Cyber Lab — ML Anomaly Detector")
    print("=" * 40)
    result = detect()
    if 'error' in result:
        print(f"❌ {result['error']}")
    else:
        print(f"Time: {result['timestamp']}")
        print(f"CPU: {result['cpu']}%")
        print(f"Memory: {result['memory']}%")
        print(f"Disk: {result['disk']}%")
        print(f"Connections: {result['connections']}")
        print(f"Processes: {result['processes']}")
        print(f"Anomaly Score: {result['anomaly_score']}")
        print(f"Status: {result['status']}")
