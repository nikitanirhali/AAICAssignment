# Flask Log API

A REST API to read and analyze log files.

## Endpoints

- `GET /logs` → Fetch logs (supports filters: level, component, start_time, end_time)
- `GET /logs/stats` → Statistics summary
- `GET /logs/{log_id}` → Fetch specific log by ID

## Run Locally

```bash
pip3 install -r requirements.txt
python3 app.py
