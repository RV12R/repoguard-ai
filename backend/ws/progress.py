"""
WebSocket endpoint for real-time scan progress streaming.
"""
import asyncio
import json
import logging
from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

# Active WebSocket connections per scan
_connections: dict[str, list[WebSocket]] = {}


async def register(scan_id: str, ws: WebSocket):
    """Register a WebSocket connection for a scan."""
    await ws.accept()
    if scan_id not in _connections:
        _connections[scan_id] = []
    _connections[scan_id].append(ws)


async def unregister(scan_id: str, ws: WebSocket):
    """Remove a WebSocket connection."""
    if scan_id in _connections:
        _connections[scan_id] = [c for c in _connections[scan_id] if c != ws]
        if not _connections[scan_id]:
            del _connections[scan_id]


async def broadcast(scan_id: str, message: dict):
    """Send a message to all connections for a scan."""
    if scan_id not in _connections:
        return
    dead = []
    for ws in _connections[scan_id]:
        try:
            await ws.send_text(json.dumps(message))
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connections[scan_id].remove(ws)


async def send_log(scan_id: str, message: str):
    """Send a log message."""
    await broadcast(scan_id, {"type": "log", "message": message})


async def send_progress(scan_id: str, progress: int, status: str):
    """Send progress update."""
    await broadcast(scan_id, {"type": "progress", "progress": progress, "status": status})


async def send_result(scan_id: str, scan_data: dict):
    """Send final scan result."""
    await broadcast(scan_id, {"type": "result", "scan": scan_data})
