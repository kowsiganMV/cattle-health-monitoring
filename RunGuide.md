# Cattle Health Monitoring System — Run Guide

A complete guide to configure and run the backend API server.

---

## Prerequisites

- Python 3.12+
- MongoDB (local instance or MongoDB Atlas cloud cluster)
- pip (Python package manager)

---

## Step 1 — Configure Environment Variables

Before running the server, you must set up the `.env` file with your configuration.

### Create the `.env` file

```bash
cp .env.example .env
```

### Edit `.env` with your values

Open the `.env` file and update the following variables:

```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/CDataBase
DATABASE_NAME=CDataBase
API_SECRET_KEY=your_secret_key_here
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### Configuration Details

| Variable | Description | Required | Example |
|---|---|---|---|
| `MONGODB_URI` | MongoDB connection string (Atlas or local) | ✅ Yes | `mongodb+srv://user:pass@cluster.mongodb.net/CDataBase` |
| `DATABASE_NAME` | Name of the MongoDB database | ✅ Yes | `CDataBase` |
| `API_SECRET_KEY` | Secret key for API security | ✅ Yes | Any strong random string |
| `SERVER_HOST` | Host address the server binds to | Optional | `0.0.0.0` (default) |
| `SERVER_PORT` | Port number for the server | Optional | `8000` (default) |

> **For local MongoDB:** Use `MONGODB_URI=mongodb://localhost:27017/CDataBase`
>
> **For MongoDB Atlas:** Use the connection string from your Atlas dashboard.

### MongoDB Database Structure

The backend automatically creates the time series collection and indexes on startup.

**Database:** `CDataBase`

| Collection | Type | Description |
|---|---|---|
| `cattle` | Standard | Cattle metadata (unique index on `cid`) |
| `cattle_sensor_data_ts` | **Time Series** | Sensor readings (`timeField: timestamp_iso`, `metaField: cid`, `granularity: seconds`) |
| `cattle_health_events` | Standard | Health alerts and anomaly events |
| `logs` | **Time Series** | Backend operation logs (`timeField: timestamp`, `metaField: service`, `granularity: seconds`) |

---

## Step 2 — Set Up Virtual Environment

### Create virtual environment

```bash
python3 -m venv venv
```

### Activate virtual environment

**Linux / macOS:**
```bash
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

After activation you should see `(venv)` prefix in your terminal.

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `fastapi` — Web framework
- `uvicorn` — ASGI server
- `motor` — Async MongoDB driver
- `pydantic` — Data validation
- `pydantic-settings` — Environment variable loading
- `python-dotenv` — `.env` file support

---

## Step 4 — Run the Server

### Development mode (with auto-reload)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or using Python directly:

```bash
python -m app.main
```

### Production mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

```bash
docker build -t cattle-api .
docker run -p 8000:8000 --env-file .env cattle-api
```

### Verify the server is running

Open your browser or use curl:

```bash
curl http://localhost:8000/
```

Expected response:

```json
{
  "status": "ok",
  "service": "Cattle Health Monitoring API"
}
```

---

## Step 5 — Open API Documentation

FastAPI auto-generates interactive API docs.

| Docs | URL |
|---|---|
| Swagger UI | [http://localhost:8000/docs](http://localhost:8000/docs) |
| ReDoc | [http://localhost:8000/redoc](http://localhost:8000/redoc) |

---

## API Endpoints

### 1. Health Check

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/` |
| **Description** | Check if the API server is running |

**Request:**

```bash
curl http://localhost:8000/
```

**Response:**

```json
{
  "status": "ok",
  "service": "Cattle Health Monitoring API"
}
```

---

### 2. Create Cattle

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/api/v1/cattle` |
| **Description** | Register a new cattle in the system |

**Request:**

```bash
curl -X POST http://localhost:8000/api/v1/cattle \
  -H "Content-Type: application/json" \
  -d '{
    "cid": 1,
    "name": "Cow-01",
    "farm_id": "Farm-A",
    "breed": "HF",
    "age": 4,
    "status": "active"
  }'
```

**Response (200):**

```json
{
  "success": true,
  "message": "Cattle created successfully",
  "cid": 1
}
```

**Conflict Error (409):** Returned when `cid` already exists.

---

### 3. List All Cattle

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/v1/cattle` |
| **Description** | List all registered cattle |

**Request:**

```bash
curl http://localhost:8000/api/v1/cattle
```

**Response (200):**

```json
[
  { "cid": 1, "name": "Cow-01", "farm_id": "Farm-A", "breed": "HF", "age": 4, "status": "active", "created_at": "2026-02-04T23:31:48Z" }
]
```

---

### 4. Get Cattle by ID

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/v1/cattle/{cid}` |
| **Description** | Get metadata for a specific cattle |

**Request:**

```bash
curl http://localhost:8000/api/v1/cattle/1
```

**Response (200):**

```json
{
  "cid": 1,
  "name": "Cow-01",
  "farm_id": "Farm-A",
  "breed": "HF",
  "age": 4,
  "status": "active",
  "created_at": "2026-02-04T23:31:48Z"
}
```

---

### 5. Update Cattle

| | |
|---|---|
| **Method** | `PUT` |
| **URL** | `/api/v1/cattle/{cid}` |
| **Description** | Update cattle metadata (only send fields to change) |

**Request:**

```bash
curl -X PUT http://localhost:8000/api/v1/cattle/1 \
  -H "Content-Type: application/json" \
  -d '{ "breed": "Jersey", "age": 5 }'
```

**Response (200):**

```json
{
  "success": true,
  "message": "Cattle updated successfully",
  "cid": 1
}
```

---

### 6. Bulk Sensor Data Ingestion

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/api/v1/cattle/sensor/bulk` |
| **Content-Type** | `application/json` |
| **Description** | Receive bulk sensor data from an ESP32 device, transform it, and store in MongoDB |

> **Note:** The cattle must be registered (via `POST /api/v1/cattle`) before sensor data can be ingested. Returns `404` if the cattle does not exist.

**Request Body Format:**

```json
{
  "cid": 1,
  "data": [
    {
      "timestamp_iso": "2026-02-04T23:31:48.120",
      "timestamp_ms": 2122,
      "temp_c": 28.47,
      "ax": -3384,
      "ay": -8684,
      "az": 13392,
      "gx": -145,
      "gy": 84,
      "gz": -12,
      "signal": 1818,
      "peak": 1,
      "down": 0,
      "bpm": 0
    }
  ]
}
```

**Request Fields:**

| Field | Type | Description |
|---|---|---|
| `cid` | int | Cattle ID (must be > 0) |
| `data` | array | Array of sensor readings (1 to 5000 rows) |

**Each sensor row fields:**

| Field | Type | Description |
|---|---|---|
| `timestamp_iso` | string | ISO 8601 timestamp |
| `timestamp_ms` | int | Millisecond timestamp |
| `temp_c` | float | Temperature in Celsius |
| `ax`, `ay`, `az` | int | Accelerometer values (X, Y, Z) |
| `gx`, `gy`, `gz` | int | Gyroscope values (X, Y, Z) |
| `signal` | int | Heart signal value |
| `peak` | int | Heart signal peak flag |
| `down` | int | Heart signal down flag |
| `bpm` | float | Beats per minute |

**Example curl command:**

```bash
curl -X POST http://localhost:8000/api/v1/cattle/sensor/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "cid": 1,
    "data": [
      {
        "timestamp_iso": "2026-02-04T23:31:48.120",
        "timestamp_ms": 2122,
        "temp_c": 28.47,
        "ax": -3384,
        "ay": -8684,
        "az": 13392,
        "gx": -145,
        "gy": 84,
        "gz": -12,
        "signal": 1818,
        "peak": 1,
        "down": 0,
        "bpm": 0
      },
      {
        "timestamp_iso": "2026-02-04T23:31:48.320",
        "timestamp_ms": 2322,
        "temp_c": 28.51,
        "ax": -3404,
        "ay": -8668,
        "az": 13436,
        "gx": -161,
        "gy": 62,
        "gz": -11,
        "signal": 1833,
        "peak": 0,
        "down": 0,
        "bpm": 0
      }
    ]
  }'
```

**Success Response (200):**

```json
{
  "success": true,
  "cid": 1,
  "inserted_count": 2,
  "message": "Successfully inserted 2 sensor readings for cattle 1"
}
```

**Validation Error Response (422):**

Returned when request body fails validation (missing fields, wrong types, invalid timestamp, etc.)

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "data", 0, "temp_c"],
      "msg": "Field required"
    }
  ]
}
```

**Server Error Response (500):**

```json
{
  "detail": "Database insertion failed: <error message>"
}
```

**Cattle Not Found Error (404):**

```json
{
  "detail": "Cattle with CID 1 is not registered"
}
```

---

### 7. Get Latest Sensor Reading for All Cattle (Dashboard)

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/v1/cattle/latest` |
| **Description** | Returns the latest sensor reading for every cattle. Used for dashboard overview. |

**Request:**

```bash
curl http://localhost:8000/api/v1/cattle/latest
```

**Response (200):**

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

---

### 8. Get Latest Sensor Reading for a Cattle

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/v1/cattle/{cid}/latest` |
| **Description** | Returns the most recent sensor reading for a specific cattle |

**Request:**

```bash
curl http://localhost:8000/api/v1/cattle/1/latest
```

**Response (200):**

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

---

### 9. Get Last N Sensor Records

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/v1/cattle/{cid}/recent?limit=N` |
| **Description** | Returns the last N sensor records, newest first |

| Parameter | Type | Default | Description |
|---|---|---|---|
| `cid` | int (path) | — | Cattle ID |
| `limit` | int (query) | 100 | Number of records to return (1–5000) |

**Request:**

```bash
curl "http://localhost:8000/api/v1/cattle/1/recent?limit=50"
```

**Response (200):** Array of sensor readings (same structure as `/latest`), sorted newest first.

---

### 10. Get Sensor Data for Last 1 Hour

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/v1/cattle/{cid}/last-hour` |
| **Description** | Returns all sensor readings from the past 1 hour, sorted ascending |

**Request:**

```bash
curl http://localhost:8000/api/v1/cattle/1/last-hour
```

**Response (200):** Array of sensor readings sorted by timestamp ascending.

---

### 11. Get Sensor Data Between Time Range

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/v1/cattle/{cid}/range?start=ISO_TIME&end=ISO_TIME` |
| **Description** | Returns sensor readings between two timestamps |

| Parameter | Type | Required | Description |
|---|---|---|---|
| `cid` | int (path) | ✅ | Cattle ID |
| `start` | datetime (query) | ✅ | Start time in ISO 8601 format |
| `end` | datetime (query) | ✅ | End time in ISO 8601 format |

**Request:**

```bash
curl "http://localhost:8000/api/v1/cattle/1/range?start=2026-02-04T22:00:00&end=2026-02-04T23:59:59"
```

**Response (200):** Array of sensor readings within the time range, sorted ascending.

**Validation Error (400):** Returned when `start` >= `end`:

```json
{
  "detail": "'start' must be before 'end'"
}
```

---

### 12. Get Health Events for a Cattle

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/v1/cattle/{cid}/health-events?limit=N` |
| **Description** | Returns health alerts for a specific cattle, newest first |

| Parameter | Type | Default | Description |
|---|---|---|---|
| `cid` | int (path) | — | Cattle ID |
| `limit` | int (query) | 50 | Number of events to return (1–500) |

**Request:**

```bash
curl "http://localhost:8000/api/v1/cattle/1/health-events?limit=20"
```

**Response (200):**

```json
[
  { "cid": 1, "event": "High Temperature", "value": 39.2, "status": "warning", "timestamp": "2026-02-04T23:40:00Z" }
]
```

---

### 13. Get Recent Health Events (All Cattle)

| | |
|---|---|
| **Method** | `GET` |
| **URL** | `/api/v1/health-events/recent?limit=N` |
| **Description** | Returns recent health alerts across all cattle. Used for dashboard alert panel. |

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | int (query) | 50 | Number of events to return (1–500) |

**Request:**

```bash
curl "http://localhost:8000/api/v1/health-events/recent?limit=20"
```

**Response (200):**

```json
[
  { "cid": 1, "event": "High Temperature", "value": 39.2, "status": "warning", "timestamp": "2026-02-04T23:40:00Z" },
  { "cid": 2, "event": "Low Activity", "value": 12.0, "status": "alert", "timestamp": "2026-02-04T23:38:00Z" }
]
```

---

### API Summary Table

| # | Method | Endpoint | Description |
|---|--------|----------|-------------|
| 1 | `GET` | `/` | Health check |
| 2 | `POST` | `/api/v1/cattle` | Register a new cattle |
| 3 | `GET` | `/api/v1/cattle` | List all cattle |
| 4 | `GET` | `/api/v1/cattle/{cid}` | Get cattle metadata |
| 5 | `PUT` | `/api/v1/cattle/{cid}` | Update cattle metadata |
| 6 | `POST` | `/api/v1/cattle/sensor/bulk` | Bulk ingest sensor data from ESP32 |
| 7 | `GET` | `/api/v1/cattle/latest` | Latest reading for all cattle (dashboard) |
| 8 | `GET` | `/api/v1/cattle/{cid}/latest` | Most recent sensor reading |
| 9 | `GET` | `/api/v1/cattle/{cid}/recent?limit=N` | Last N sensor records |
| 10 | `GET` | `/api/v1/cattle/{cid}/last-hour` | Readings from the past hour |
| 11 | `GET` | `/api/v1/cattle/{cid}/range?start=&end=` | Readings in a time range |
| 12 | `GET` | `/api/v1/cattle/{cid}/health-events` | Health events for a cattle |
| 13 | `GET` | `/api/v1/health-events/recent?limit=N` | Recent health alerts (all cattle) |

The API transforms the flat ESP32 sensor format into a structured MongoDB document:

```
Raw (from ESP32)              →    Stored (in MongoDB)
─────────────────────────────      ─────────────────────────────
temp_c: 28.47                 →    temperature: 28.47
ax: -3384                     →    accel: { ax: -3384,
ay: -8684                              ay: -8684,
az: 13392                              az: 13392 }
gx: -145                      →    gyro:  { gx: -145,
gy: 84                                 gy: 84,
gz: -12                                gz: -12 }
signal: 1818                   →    heart: { signal: 1818,
peak: 1                                peak: 1,
down: 0                                down: 0,
bpm: 0                                 bpm: 0 }
```

---

## Quick Start (All Commands Together)

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Test the API (in another terminal)
curl http://localhost:8000/
```

---

## Stopping the Server

Press `Ctrl + C` in the terminal where the server is running.

To deactivate the virtual environment:

```bash
deactivate
```
