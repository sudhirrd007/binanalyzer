from main.app.database_sync import DatabaseSync

from typing import Optional, List, Any
import logging
from pydantic import BaseModel, Field, field_validator, create_model
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body
from typing import Annotated

logging.basicConfig(level=logging.INFO)

database_sync_obj = DatabaseSync()

router = APIRouter()


# Sync Database -----------------------------------------------------------------------------------------------
class SyncDatabaseResponse(BaseModel):
    isSuccess: bool
    message: str


@router.get(
    "/sync_transactions",
    response_model=SyncDatabaseResponse,
    summary="Sync the database with the latest transactions from Binance",
)
async def sync_transactions():
    try:
        database_sync_obj.sync_database()
        return SyncDatabaseResponse(
            isSuccess=True, message="Database Synced Successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
