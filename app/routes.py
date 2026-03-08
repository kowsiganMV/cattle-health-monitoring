"""
API route definitions.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth import verify_api_key
from app.models import (
    SensorBulkRequest,
    BulkInsertResponse,
    SensorReadingResponse,
    CattleResponse,
    CattleLatestStatus,
    CattleCreate,
    CattleUpdate,
    CattleCreateResponse,
    CattleUpdateResponse,
    HealthEventResponse,
)
from app.services import (
    bulk_insert_sensor_data,
    get_cattle_metadata,
    get_latest_sensor_data,
    get_recent_records,
    get_last_hour_data,
    get_range_data,
    get_all_cattle_latest,
    create_cattle,
    update_cattle,
    get_all_cattle,
    get_cattle_health_events,
    get_recent_health_events,
)

cattle_router = APIRouter(prefix="/api/v1/cattle", tags=["Cattle Management"], dependencies=[Depends(verify_api_key)])
sensor_router = APIRouter(prefix="/api/v1/cattle", tags=["Sensor Data"], dependencies=[Depends(verify_api_key)])
health_router = APIRouter(prefix="/api/v1", tags=["Health Events"], dependencies=[Depends(verify_api_key)])


# ══════════════════════════════════════════
#  Cattle Management
# ══════════════════════════════════════════


@cattle_router.post("", response_model=CattleCreateResponse)
async def create_new_cattle(data: CattleCreate):
    """Register a new cattle in the system."""
    try:
        await create_cattle(data)
        return CattleCreateResponse(
            success=True,
            message="Cattle created successfully",
            cid=data.cid,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@cattle_router.get("", response_model=list[CattleResponse])
async def list_all_cattle():
    """List all registered cattle."""
    results = await get_all_cattle()
    if not results:
        raise HTTPException(status_code=404, detail="No cattle found")
    return results


@cattle_router.put("/{cid}", response_model=CattleUpdateResponse)
async def update_existing_cattle(cid: int, data: CattleUpdate):
    """Update metadata for a specific cattle."""
    result = await update_cattle(cid, data)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Cattle with cid {cid} not found")
    return CattleUpdateResponse(
        success=True,
        message="Cattle updated successfully",
        cid=cid,
    )


@cattle_router.get("/{cid}", response_model=CattleResponse)
async def get_cattle(cid: int):
    """Get metadata for a specific cattle by CID."""
    cattle = await get_cattle_metadata(cid)
    if not cattle:
        raise HTTPException(status_code=404, detail=f"Cattle with cid {cid} not found")
    return cattle


# ══════════════════════════════════════════
#  Sensor Data Ingestion & Retrieval
# ══════════════════════════════════════════


@sensor_router.post("/sensor/bulk", response_model=BulkInsertResponse)
async def ingest_bulk_sensor_data(request: SensorBulkRequest):
    """
    Receive bulk sensor data from an ESP32 device.

    - Validates CID and all sensor rows via Pydantic
    - Transforms flat ESP32 format → structured MongoDB schema
    - Inserts all documents using insertMany for efficiency
    """
    try:
        inserted = await bulk_insert_sensor_data(request.cid, request.data)
        return BulkInsertResponse(
            success=True,
            cid=request.cid,
            inserted_count=inserted,
            message=f"Successfully inserted {inserted} sensor readings for cattle {request.cid}",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database insertion failed: {str(e)}")


@sensor_router.get("/latest", response_model=list[CattleLatestStatus])
async def get_all_latest():
    """
    Get the latest sensor reading for every cattle.
    Used for dashboard overview of all animals.
    """
    results = await get_all_cattle_latest()
    if not results:
        raise HTTPException(status_code=404, detail="No sensor data found")
    return results


@sensor_router.get("/{cid}/latest", response_model=SensorReadingResponse)
async def get_latest(cid: int):
    """Get the most recent sensor reading for a cattle."""
    doc = await get_latest_sensor_data(cid)
    if not doc:
        raise HTTPException(status_code=404, detail=f"No sensor data found for cid {cid}")
    return doc


@sensor_router.get("/{cid}/recent", response_model=list[SensorReadingResponse])
async def get_recent(
    cid: int,
    limit: int = Query(default=100, ge=1, le=5000, description="Number of recent records"),
):
    """Get the last N sensor records for a cattle, newest first."""
    docs = await get_recent_records(cid, limit)
    if not docs:
        raise HTTPException(status_code=404, detail=f"No sensor data found for cid {cid}")
    return docs


@sensor_router.get("/{cid}/last-hour", response_model=list[SensorReadingResponse])
async def get_last_hour(cid: int):
    """Get all sensor readings from the last 1 hour for a cattle."""
    docs = await get_last_hour_data(cid)
    if not docs:
        raise HTTPException(status_code=404, detail=f"No sensor data in the last hour for cid {cid}")
    return docs


@sensor_router.get("/{cid}/range", response_model=list[SensorReadingResponse])
async def get_range(
    cid: int,
    start: datetime = Query(..., description="Start time (ISO 8601)"),
    end: datetime = Query(..., description="End time (ISO 8601)"),
):
    """Get sensor readings between two timestamps for a cattle."""
    if start >= end:
        raise HTTPException(status_code=400, detail="'start' must be before 'end'")
    docs = await get_range_data(cid, start, end)
    if not docs:
        raise HTTPException(status_code=404, detail=f"No sensor data in the given range for cid {cid}")
    return docs


# ══════════════════════════════════════════
#  Health Events
# ══════════════════════════════════════════


@cattle_router.get("/{cid}/health-events", response_model=list[HealthEventResponse])
async def get_health_events(
    cid: int,
    limit: int = Query(default=50, ge=1, le=500, description="Number of events"),
):
    """Get health events for a specific cattle, newest first."""
    docs = await get_cattle_health_events(cid, limit)
    if not docs:
        raise HTTPException(status_code=404, detail=f"No health events found for cid {cid}")
    return docs


@health_router.get("/health-events/recent", response_model=list[HealthEventResponse])
async def get_recent_events(
    limit: int = Query(default=50, ge=1, le=500, description="Number of recent events"),
):
    """Get recent health events across all cattle (dashboard alerts)."""
    docs = await get_recent_health_events(limit)
    if not docs:
        raise HTTPException(status_code=404, detail="No health events found")
    return docs
