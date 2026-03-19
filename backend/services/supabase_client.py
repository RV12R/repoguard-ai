"""
Supabase client — database operations for scans and vulnerabilities.
"""
import os
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

_client = None


def get_client():
    """Get or create Supabase client singleton."""
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            logger.warning("Supabase credentials not set — using in-memory store")
            return None
        try:
            from supabase import create_client
            _client = create_client(url, key)
        except Exception as e:
            logger.error(f"Failed to create Supabase client: {e}")
            return None
    return _client


# ── In-memory fallback store (for dev without Supabase) ──
_memory_store: dict[str, dict] = {}


class DBService:
    """Database operations — uses Supabase or in-memory fallback."""

    @staticmethod
    async def create_scan(scan_id: str, repo_url: str) -> dict:
        """Create a new scan record."""
        record = {
            "id": scan_id,
            "repo_url": repo_url,
            "status": "queued",
            "risk_score": 0,
            "vulnerability_count": 0,
            "created_at": datetime.utcnow().isoformat(),
        }
        client = get_client()
        if client:
            try:
                client.table("scans").insert(record).execute()
            except Exception as e:
                logger.error(f"DB insert error: {e}")
        _memory_store[scan_id] = record
        return record

    @staticmethod
    async def update_scan(scan_id: str, updates: dict) -> None:
        """Update scan record."""
        client = get_client()
        if client:
            try:
                client.table("scans").update(updates).eq("id", scan_id).execute()
            except Exception as e:
                logger.error(f"DB update error: {e}")
        if scan_id in _memory_store:
            _memory_store[scan_id].update(updates)

    @staticmethod
    async def get_scan(scan_id: str) -> Optional[dict]:
        """Get scan by ID."""
        client = get_client()
        if client:
            try:
                result = client.table("scans").select("*").eq("id", scan_id).single().execute()
                return result.data
            except Exception:
                pass
        return _memory_store.get(scan_id)

    @staticmethod
    async def get_all_scans() -> list[dict]:
        """Get all scans ordered by date."""
        client = get_client()
        if client:
            try:
                result = client.table("scans").select("*").order("created_at", desc=True).execute()
                return result.data or []
            except Exception:
                pass
        return sorted(_memory_store.values(), key=lambda x: x.get("created_at", ""), reverse=True)
