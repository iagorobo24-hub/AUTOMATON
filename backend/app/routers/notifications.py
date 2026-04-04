from fastapi import APIRouter, Depends
from typing import Optional
from ..services.notifications import NotificationService
from ..api.deps import get_notification_service

router = APIRouter()


@router.get("/")
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Get notifications"""
    notifications = await notification_service.get_notifications(unread_only, limit)
    unread_count = await notification_service.get_unread_count()
    return {"notifications": notifications, "unread_count": unread_count}


@router.get("/count")
async def get_notification_count(
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Get unread notification count"""
    count = await notification_service.get_unread_count()
    return {"unread_count": count}


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Mark a notification as read"""
    success = await notification_service.mark_as_read(notification_id)
    return {"success": success}


@router.post("/read-all")
async def mark_all_notifications_read(
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Mark all notifications as read"""
    count = await notification_service.mark_all_as_read()
    return {"marked_count": count}


@router.delete("/{notification_id}")
async def dismiss_notification(
    notification_id: str,
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Dismiss/delete a notification"""
    success = await notification_service.dismiss_notification(notification_id)
    return {"success": success}


@router.delete("/")
async def dismiss_all_notifications(
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Dismiss all notifications"""
    count = await notification_service.dismiss_all()
    return {"dismissed_count": count}


@router.get("/activity")
async def get_activity_feed(
    agent_id: Optional[str] = None,
    type_filter: Optional[str] = None,
    limit: int = 100,
    notification_service: NotificationService = Depends(get_notification_service),
):
    """Get activity feed"""
    events = await notification_service.get_activity_feed(agent_id, type_filter, limit)
    return {"events": events}
