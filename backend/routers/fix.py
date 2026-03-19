"""
Fix router — create fix branches with AI-generated patches.
"""
import logging
from fastapi import APIRouter, HTTPException

from models.schemas import FixRequest, FixResponse
from services.fix_service import FixService
from routers.scan import _scan_results

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


@router.post("/fix/{scan_id}", response_model=FixResponse)
async def apply_fixes(scan_id: str, req: FixRequest):
    """Create a GitHub branch with fixes for scan vulnerabilities."""
    if scan_id not in _scan_results:
        raise HTTPException(status_code=404, detail="Scan not found")

    scan = _scan_results[scan_id]
    if scan.status != "completed":
        raise HTTPException(status_code=400, detail="Scan is not completed")

    if not scan.vulnerabilities:
        raise HTTPException(status_code=400, detail="No vulnerabilities to fix")

    try:
        result = await FixService.apply_fixes(
            repo_url=scan.repo_url,
            vulnerabilities=scan.vulnerabilities,
            github_token=req.github_token,
        )
        return FixResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
