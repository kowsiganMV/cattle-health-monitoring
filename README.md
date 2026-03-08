# Cattle Health Monitoring System — REST API

Backend service that receives bulk sensor data from ESP32 devices and stores it in MongoDB.

## Tech Stack

| Component | Choice | Why |
|-----------|--------|-----|
| Language | Python 3.12 | Clean, typed, great ecosystem |
| Framework | FastAPI | Async-native, auto-validation, OpenAPI docs |
| DB Driver | Motor | Async MongoDB driver, supports `insertMany` |
| Validation | Pydantic v2 | Automatic request validation with clear errors |
| Config | pydantic-settings | Type-safe env var loading from `.env` |

## Project Structure

```
C_RESTAPI/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app entry point
│   ├── config.py        # Environment variable settings
│   ├── database.py      # MongoDB connection & indexes
│   ├── logger.py        # Async logging to MongoDB logs collection
│   ├── models.py        # Pydantic request/response/DB models
│   ├── routes.py        # API endpoint definitions
│   └── services.py      # Data transformation & DB operations
├── data.json            # Sample ESP32 sensor data
├── requirements.txt
├── Dockerfile
├── .env                 # Local environment variables (not committed)
├── .env.example         # Template for .env
└── .gitignore
```

## System Architecture

```
ESP32 Device → FastAPI Backend → MongoDB Atlas (Database: CDataBase)
```

Collections: `cattle` · `cattle_sensor_data_ts` · `cattle_health_events` · `logs`

## MongoDB Schema

**Database:** `CDataBase`

### Collection: `cattle`
Stores cattle metadata (CID, name, farm, breed, age, status).

### Collection: `cattle_sensor_data_ts` *(Time Series)*
Stores transformed time-series sensor readings from ESP32 devices.

| Config | Value |
|--------|-------|
| Type | Time Series |
| timeField | `timestamp_iso` |
| metaField | `cid` |
| granularity | `seconds` |

Example document:
```json
{
  "cid": 1,
  "timestamp_iso": "2026-02-04T23:31:48.120Z",
  "timestamp_ms": 2122,
  "temperature": 28.47,
  "accel": { "ax": -3384, "ay": -8684, "az": 13392 },
  "gyro":  { "gx": -145,  "gy": 84,    "gz": -12 },
  "heart": { "signal": 1818, "peak": 1, "down": 0, "bpm": 0 },
  "created_at": "2026-02-04T23:35:00Z"
}
```

### Collection: `cattle_health_events`
Stores alerts and anomaly events.

### Collection: `logs` *(Time Series)*
Stores structured backend operation logs for debugging and monitoring.

| Config | Value |
|--------|-------|
| Type | Time Series |
| timeField | `timestamp` |
| metaField | `service` |
| granularity | `seconds` |

Example document:
```json
{
  "timestamp": "2026-03-08T10:45:22Z",
  "service": "sensor_api",
  "level": "INFO",
  "action": "bulk_insert",
  "collection": "cattle_sensor_data_ts",
  "cid": 1,
  "records_count": 1000,
  "message": "Sensor data uploaded successfully"
}
```

### Indexes
```
cattle:                  { cid: 1 }  (unique)
cattle_sensor_data_ts:   { cid: 1, timestamp_iso: -1 }
cattle_health_events:    { cid: 1 }, { timestamp: -1 }
logs:                    { service: 1, timestamp: -1 }, { cid: 1 }
```

## Data Transformation

ESP32 sends flat data → backend converts to structured format:

| Raw (ESP32) | Structured (MongoDB) |
|-------------|---------------------|
| `temp_c` | `temperature` |
| `ax, ay, az` | `accel: { ax, ay, az }` |
| `gx, gy, gz` | `gyro: { gx, gy, gz }` |
| `signal, peak, down, bpm` | `heart: { signal, peak, down, bpm }` |

## API

### Cattle Management

#### `POST /api/v1/cattle`
Register a new cattle in the system.

```bash
curl -X POST http://localhost:8000/api/v1/cattle \
  -H "Content-Type: application/json" \
  -d '{ "cid": 1, "name": "Cow-01", "farm_id": "Farm-A", "breed": "HF", "age": 4, "status": "active" }'
```

**Response:**
```json
{ "success": true, "message": "Cattle created successfully", "cid": 1 }
```

#### `GET /api/v1/cattle`
List all registered cattle.

```bash
curl http://localhost:8000/api/v1/cattle
```

**Response:**
```json
[
  { "cid": 1, "name": "Cow-01", "farm_id": "Farm-A", "breed": "HF", "age": 4, "status": "active", "created_at": "2026-02-04T23:31:48Z" },
  { "cid": 2, "name": "Cow-02", "farm_id": "Farm-A", "breed": "Jersey", "age": 3, "status": "active", "created_at": "2026-02-05T10:00:00Z" }
]
```

#### `GET /api/v1/cattle/{cid}`
Get metadata for a specific cattle.

```bash
curl http://localhost:8000/api/v1/cattle/1
```

**Response:**
```json
{ "cid": 1, "name": "Cow-01", "farm_id": "Farm-A", "breed": "HF", "age": 4, "status": "active", "created_at": "2026-02-04T23:31:48Z" }
```

#### `PUT /api/v1/cattle/{cid}`
Update cattle metadata. Only send fields you want to change.

```bash
curl -X PUT http://localhost:8000/api/v1/cattle/1 \
  -H "Content-Type: application/json" \
  -d '{ "breed": "Jersey", "age": 5 }'
```

**Response:**
```json
{ "success": true, "message": "Cattle updated successfully", "cid": 1 }
```

---

### Sensor Data Ingestion

#### `POST /api/v1/cattle/sensor/bulk`

Receive bulk sensor data from an ESP32 device, transform, and store in MongoDB.

> **Validation:** The cattle must be registered (via `POST /api/v1/cattle`) before sensor data can be ingested. Returns `404` if the cattle does not exist.

**Request:**
```json
{
  "cid": 1,
  "data": [
    {
      "timestamp_iso": "2026-02-04T23:31:48.120",
      "timestamp_ms": 2122,
      "temp_c": 28.47,
      "ax": -3384, "ay": -8684, "az": 13392,
      "gx": -145, "gy": 84, "gz": -12,
      "signal": 1818, "peak": 1, "down": 0, "bpm": 0
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "cid": 1,
  "inserted_count": 1,
  "message": "Successfully inserted 1 sensor readings for cattle 1"
}
```

---

### Sensor Data Retrieval

#### `GET /`
Health check — verify the server is running.

#### `GET /api/v1/cattle/latest`
Get the latest sensor reading for **every cattle** (dashboard overview).

```bash
curl http://localhost:8000/api/v1/cattle/latest
```

**Response:**
```json
[
  {
    "cid": 1,
    "timestamp_iso": "2026-02-04T23:31:50.120",
    "temperature": 28.51,
    "accel": { "ax": -3400, "ay": -8688, "az": 13424 },
    "gyro": { "gx": -161, "gy": 62, "gz": -11 },
    "heart": { "signal": 1833, "peak": 0, "down": 0, "bpm": 0 }
  }
]
```

#### `GET /api/v1/cattle/{cid}/latest`
Get the most recent sensor reading for a cattle.

```bash
curl http://localhost:8000/api/v1/cattle/1/latest
```

**Response:**
```json
{
  "cid": 1,
  "timestamp_iso": "2026-02-04T23:31:50.120",
  "timestamp_ms": 4122,
  "temperature": 28.51,
  "accel": { "ax": -3400, "ay": -8688, "az": 13424 },
  "gyro": { "gx": -161, "gy": 62, "gz": -11 },
  "heart": { "signal": 1833, "peak": 0, "down": 0, "bpm": 0 },
  "created_at": "2026-02-04T23:35:00Z"
}
```

#### `GET /api/v1/cattle/{cid}/recent?limit=100`
Get the last N sensor records (newest first).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 100 | Number of records (1–5000) |

```bash
curl "http://localhost:8000/api/v1/cattle/1/recent?limit=50"
```

#### `GET /api/v1/cattle/{cid}/last-hour`
Get all sensor readings from the past 1 hour (sorted ascending).

```bash
curl http://localhost:8000/api/v1/cattle/1/last-hour
```

#### `GET /api/v1/cattle/{cid}/range?start=...&end=...`
Get sensor readings between two ISO 8601 timestamps.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `start` | datetime | ✅ | Start time (ISO 8601) |
| `end` | datetime | ✅ | End time (ISO 8601) |

```bash
curl "http://localhost:8000/api/v1/cattle/1/range?start=2026-02-04T22:00:00&end=2026-02-04T23:59:59"
```

---

### Health Events

#### `GET /api/v1/cattle/{cid}/health-events?limit=50`
Get health alerts for a specific cattle, newest first.

```bash
curl "http://localhost:8000/api/v1/cattle/1/health-events?limit=20"
```

**Response:**
```json
[
  { "cid": 1, "event": "High Temperature", "value": 39.2, "status": "warning", "timestamp": "2026-02-04T23:40:00Z" }
]
```

#### `GET /api/v1/health-events/recent?limit=50`
Get recent health alerts across all cattle (dashboard alert panel).

```bash
curl "http://localhost:8000/api/v1/health-events/recent?limit=20"
```

**Response:**
```json
[
  { "cid": 1, "event": "High Temperature", "value": 39.2, "status": "warning", "timestamp": "2026-02-04T23:40:00Z" },
  { "cid": 2, "event": "Low Activity", "value": 12.0, "status": "alert", "timestamp": "2026-02-04T23:38:00Z" }
]
```

---

### API Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/v1/cattle` | Register a new cattle |
| `GET` | `/api/v1/cattle` | List all cattle |
| `GET` | `/api/v1/cattle/{cid}` | Get cattle metadata |
| `PUT` | `/api/v1/cattle/{cid}` | Update cattle metadata |
| `POST` | `/api/v1/cattle/sensor/bulk` | Bulk ingest sensor data from ESP32 |
| `GET` | `/api/v1/cattle/latest` | Latest reading for all cattle (dashboard) |
| `GET` | `/api/v1/cattle/{cid}/latest` | Most recent sensor reading |
| `GET` | `/api/v1/cattle/{cid}/recent?limit=N` | Last N sensor records |
| `GET` | `/api/v1/cattle/{cid}/last-hour` | Readings from the past hour |
| `GET` | `/api/v1/cattle/{cid}/range?start=&end=` | Readings in a time range |
| `GET` | `/api/v1/cattle/{cid}/health-events` | Health events for a cattle |
| `GET` | `/api/v1/health-events/recent?limit=N` | Recent health alerts (all cattle) |

## Setup & Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your MongoDB URI and settings
```

### 3. Run Development Server
```bash
python -m app.main
# or
uvicorn app.main:app --reload --port 8000
```

### 4. Open API Docs
Visit `http://localhost:8000/docs` for interactive Swagger UI.

## Deployment

### Docker
```bash
docker build -t cattle-api .
docker run -p 8000:8000 --env-file .env cattle-api
```

### Cloud Platforms (Render / Railway / AWS)
1. Push code to GitHub
2. Connect repository to platform
3. Set environment variables (`MONGODB_URI`, `DATABASE_NAME`, `API_SECRET_KEY`)
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
5. Deploy

### VPS (Ubuntu)
```bash
# Install Python 3.12
sudo apt update && sudo apt install python3.12 python3.12-venv

# Clone and setup
git clone <repo-url> && cd C_RESTAPI
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env && nano .env  # Set MONGODB_URI

# Run with process manager
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## System Logging

The backend records all database actions and important system events in the `logs` Time Series collection.

**Logged operations:**
- Cattle creation and updates
- Sensor bulk uploads (success and failure)
- Invalid cattle ID rejections
- Database errors

**Log levels:** `INFO`, `WARNING`, `ERROR`, `DEBUG`

**Service identifiers:** `sensor_api`, `cattle_api`, `health_event_api`, `system`

---

## Test with Sample Data

First register a cattle, then send sensor data:

```bash
# 1. Register the cattle
curl -X POST http://localhost:8000/api/v1/cattle \
  -H "Content-Type: application/json" \
  -d '{ "cid": 1, "name": "Cow-01", "farm_id": "Farm-A", "breed": "HF", "age": 4, "status": "active" }'

# 2. Send sensor data
curl -X POST http://localhost:8000/api/v1/cattle/sensor/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "cid": 1,
    "data": [{
      "timestamp_iso": "2026-02-04T23:31:48.120",
      "timestamp_ms": 2122,
      "temp_c": 28.47,
      "ax": -3384, "ay": -8684, "az": 13392,
      "gx": -145, "gy": 84, "gz": -12,
      "signal": 1818, "peak": 1, "down": 0, "bpm": 0
    }]
  }'
```
