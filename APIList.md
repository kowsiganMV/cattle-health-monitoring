# Cattle Health Monitoring — API List

Base URL: `http://localhost:8000`

---

## Authorization

All endpoints (except `/`) require the `X-API-Key` header.

```
X-API-Key: cattle_monitoring_secure_key
```

Missing or invalid key → `401 Unauthorized`.

---

## Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Check if the API server is running |

---

## Cattle Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/cattle` | Register a new cattle in the system |
| `GET` | `/api/v1/cattle` | List all registered cattle |
| `GET` | `/api/v1/cattle/{cid}` | Get metadata for a specific cattle |
| `PUT` | `/api/v1/cattle/{cid}` | Update cattle metadata (name, breed, age, status, farm_id) |

---

## Sensor Data Ingestion

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/cattle/sensor/bulk` | Bulk ingest sensor data from ESP32, transform and store in MongoDB. **Cattle must exist first (404 if not).** |

**Body:** `{ "cid": int, "data": [ ...sensor rows ] }`

---

## Sensor Data Retrieval

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/cattle/latest` | Latest sensor reading for **all cattle** — dashboard overview |
| `GET` | `/api/v1/cattle/{cid}/latest` | Most recent single sensor reading for a cattle |
| `GET` | `/api/v1/cattle/{cid}/recent?limit=N` | Last **N** sensor records (default 100, max 5000), newest first |
| `GET` | `/api/v1/cattle/{cid}/last-hour` | All sensor readings from the **past 1 hour**, sorted ascending |
| `GET` | `/api/v1/cattle/{cid}/range?start=ISO&end=ISO` | Sensor readings between two timestamps — for charts and analytics |

---

## Health Events

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/cattle/{cid}/health-events?limit=N` | Health alerts for a specific cattle (default 50) |
| `GET` | `/api/v1/health-events/recent?limit=N` | Recent health alerts across all cattle — dashboard alert panel |

---

## Parameters

| Parameter | Location | Type | Description |
|-----------|----------|------|-------------|
| `cid` | path | int | Cattle ID |
| `limit` | query | int | Number of records to return |
| `start` | query | datetime | Start time in ISO 8601 format |
| `end` | query | datetime | End time in ISO 8601 format |

---

## Interactive Docs

| UI | URL |
|----|-----|
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
