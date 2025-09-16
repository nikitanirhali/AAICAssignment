from flask import Flask, jsonify, request, abort
import glob
import os
import uuid
from datetime import datetime
from collections import Counter

app = Flask(__name__)

class LogEntry:
    def __init__(self, log_id, timestamp, level, component, message):
        self.log_id = log_id
        self.timestamp = timestamp
        self.level = level
        self.component = component
        self.message = message

    def to_dict(self):
        return {
            "log_id": self.log_id,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "level": self.level,
            "component": self.component,
            "message": self.message
        }

logs = []

LOG_DIR = "logs" 

def parse_log_line(line):
    try:
        parts = line.strip().split('\t')
        if len(parts) != 4:
            return None
        timestamp_str, level, component, message = parts
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return LogEntry(
            log_id=str(uuid.uuid4()),
            timestamp=timestamp,
            level=level,
            component=component,
            message=message
        )
    except Exception:
        return None

def load_logs():
    global logs
    logs.clear()
    files = glob.glob(os.path.join(LOG_DIR, "*.log"))
    for file_path in files:
        with open(file_path, 'r') as f:
            for line in f:
                log_entry = parse_log_line(line)
                if log_entry:
                    logs.append(log_entry)


load_logs()

def filter_logs(level=None, component=None, start_time=None, end_time=None):
    results = logs
    if level:
        results = [log for log in results if log.level == level]
    if component:
        results = [log for log in results if log.component == component]
    if start_time:
        results = [log for log in results if log.timestamp >= start_time]
    if end_time:
        results = [log for log in results if log.timestamp <= end_time]
    return results

@app.route("/logs", methods=["GET"])
def get_logs():
    level = request.args.get('level')
    component = request.args.get('component')
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')

    start_dt = None
    end_dt = None
    try:
        if start_time_str:
            start_dt = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        if end_time_str:
            end_dt = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        abort(400, description="Invalid date format. Use 'YYYY-MM-DD HH:MM:SS'.")

    filtered_logs = filter_logs(level, component, start_dt, end_dt)
    return jsonify([log.to_dict() for log in filtered_logs])

@app.route("/logs/stats", methods=["GET"])
def get_stats():
    total = len(logs)
    levels_counter = Counter(log.level for log in logs)
    components_counter = Counter(log.component for log in logs)
    return jsonify({
        "total_logs": total,
        "counts_per_level": dict(levels_counter),
        "counts_per_component": dict(components_counter)
    })

@app.route("/logs/<log_id>", methods=["GET"])
def get_log_by_id(log_id):
    for log in logs:
        if log.log_id == log_id:
            return jsonify(log.to_dict())
    abort(404, description="Log entry not found.")

if __name__ == "__main__":
    app.run(debug=True)