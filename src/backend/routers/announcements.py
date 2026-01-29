"""
Announcements endpoints for the High School Management System API
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from pydantic import BaseModel

from ..database import announcements_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


class AnnouncementCreate(BaseModel):
    title: str
    message: str
    start_date: Optional[str] = None
    expiration_date: str
    created_by: str


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    start_date: Optional[str] = None
    expiration_date: Optional[str] = None


@router.get("/active")
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get all active announcements (within date range)"""
    today = date.today().isoformat()
    
    all_announcements = announcements_collection.find()
    active_announcements = []
    
    for announcement in all_announcements:
        # Check if announcement is expired
        if announcement.get("expiration_date") and announcement["expiration_date"] < today:
            continue
        
        # Check if announcement has started (if start_date is set)
        if announcement.get("start_date") and announcement["start_date"] > today:
            continue
        
        active_announcements.append(announcement)
    
    return active_announcements


@router.get("")
def get_all_announcements() -> List[Dict[str, Any]]:
    """Get all announcements (for management interface)"""
    return announcements_collection.find()


@router.post("")
def create_announcement(announcement: AnnouncementCreate) -> Dict[str, Any]:
    """Create a new announcement (requires authentication)"""
    
    # Validate expiration date
    try:
        if announcement.expiration_date:
            datetime.fromisoformat(announcement.expiration_date)
        if announcement.start_date:
            datetime.fromisoformat(announcement.start_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    announcement_data = announcement.dict()
    announcement_data["created_at"] = datetime.now().isoformat()
    
    result = announcements_collection.insert_one(announcement_data)
    announcement_data["_id"] = str(result.inserted_id)
    
    return announcement_data


@router.put("/{announcement_id}")
def update_announcement(announcement_id: str, announcement: AnnouncementUpdate) -> Dict[str, Any]:
    """Update an existing announcement (requires authentication)"""
    
    # Find the announcement
    existing = announcements_collection.find_one({"_id": announcement_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Validate dates if provided
    update_data = announcement.dict(exclude_unset=True)
    try:
        if "expiration_date" in update_data and update_data["expiration_date"]:
            datetime.fromisoformat(update_data["expiration_date"])
        if "start_date" in update_data and update_data["start_date"]:
            datetime.fromisoformat(update_data["start_date"])
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if update_data:
        announcements_collection.update_one(
            {"_id": announcement_id},
            {"$set": update_data}
        )
    
    # Return updated announcement
    updated = announcements_collection.find_one({"_id": announcement_id})
    return updated


@router.delete("/{announcement_id}")
def delete_announcement(announcement_id: str) -> Dict[str, str]:
    """Delete an announcement (requires authentication)"""
    
    existing = announcements_collection.find_one({"_id": announcement_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    announcements_collection.update_one(
        {"_id": announcement_id},
        {"$set": {"_deleted": True}}
    )
    
    return {"message": "Announcement deleted successfully"}
