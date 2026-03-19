"""
Scan router — handles scan creation, retrieval, and PDF downloads.
"""
import asyncio
import uuid
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Response

from models.schemas import (
    ScanRequest, ScanResponse, ScanHistoryItem, ScanStatus, VulnerabilityOut,
)
from services.git_service import GitService
from services.static_analyzer import StaticAnalyzer
from services.ai_analyzer import AIAnalyzer
from services.report_generator import ReportGenerator
from services.supabase_client import DBService
from ws import progress

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")

# In-memory store for scan results (supplements DB)
_scan_results: dict[str, ScanResponse] = {}
_pdf_cache: dict[str, bytes] = {}


def _calculate_risk_score(vulns: list[VulnerabilityOut]) -> int:
    """Calculate risk score 0-100 based on vulnerability count and severity."""
    if not vulns:
        return 0
    weights = {"critical": 25, "high": 15, "medium": 8, "low": 3, "info": 1}
    score = sum(weights.get(v.severity, 5) for v in vulns)
    return min(100, score)


async def _run_scan(scan_id: str, repo_url: str, github_token: Optional[str] = None):
    """Background task: clone → analyze → AI review → generate report."""
    try:
        # Phase 1: Clone
        await progress.send_progress(scan_id, 10, "cloning")
        await progress.send_log(scan_id, f"→ Cloning {repo_url}...")
        await DBService.update_scan(scan_id, {"status": "cloning"})

        async with GitService.clone_repo(repo_url, github_token) as repo_path:
            languages = GitService.detect_languages(repo_path)
            file_count = GitService.count_files(repo_path)
            await progress.send_log(scan_id, f"✓ Cloned ({file_count} files, {len(languages)} languages: {', '.join(languages)})")

            # Phase 2: Static Analysis
            await progress.send_progress(scan_id, 30, "analyzing")
            await progress.send_log(scan_id, "→ Running Semgrep + Bandit analysis...")
            await DBService.update_scan(scan_id, {"status": "analyzing"})

            static_vulns = await StaticAnalyzer.analyze(repo_path)
            for v in static_vulns:
                severity_label = v.severity.upper()
                await progress.send_log(scan_id, f"  {severity_label}: {v.title} in {v.file_path}")
            await progress.send_log(scan_id, f"✓ Static analysis complete — {len(static_vulns)} findings")

            # Phase 3: AI Review
            await progress.send_progress(scan_id, 55, "ai_review")
            await progress.send_log(scan_id, "→ Running AI deep review...")
            await DBService.update_scan(scan_id, {"status": "ai_review"})

            ai_vulns = await AIAnalyzer.analyze(repo_path)
            for v in ai_vulns:
                severity_label = v.severity.upper()
                await progress.send_log(scan_id, f"  {severity_label}: {v.title}")
            await progress.send_log(scan_id, f"✓ AI review complete — {len(ai_vulns)} findings")

            # Combine all vulnerabilities
            all_vulns = static_vulns + ai_vulns
            risk_score = _calculate_risk_score(all_vulns)

            # Phase 4: Generate Report
            await progress.send_progress(scan_id, 80, "generating_report")
            await progress.send_log(scan_id, "→ Generating PDF report...")
            await DBService.update_scan(scan_id, {"status": "generating_report"})

            scan_result = ScanResponse(
                id=scan_id,
                repo_url=repo_url,
                status=ScanStatus.COMPLETED,
                risk_score=risk_score,
                vulnerabilities=all_vulns,
                summary=f"Found {len(all_vulns)} vulnerabilities across {file_count} files. "
                        f"Risk score: {risk_score}/100. "
                        f"Languages analyzed: {', '.join(languages) if languages else 'N/A'}.",
                created_at=_scan_results.get(scan_id, ScanResponse(
                    id=scan_id, repo_url=repo_url, status=ScanStatus.QUEUED,
                    created_at=datetime.utcnow().isoformat(), progress=0, languages_detected=[]
                )).created_at,
                completed_at=datetime.utcnow().isoformat(),
                progress=100,
                languages_detected=languages,
            )

            # Generate PDF
            try:
                pdf_bytes = ReportGenerator.generate(scan_result)
                _pdf_cache[scan_id] = pdf_bytes
                await progress.send_log(scan_id, f"✓ Report generated — Risk Score: {risk_score}/100")
            except Exception as e:
                await progress.send_log(scan_id, f"WARN: PDF generation failed: {e}")

        # Cleanup done automatically by context manager
        await progress.send_log(scan_id, "→ Cleaning up temporary files...")
        await progress.send_log(scan_id, f"✓ DONE — Scan complete. {len(all_vulns)} vulnerabilities found.")

        # Save results
        _scan_results[scan_id] = scan_result
        await DBService.update_scan(scan_id, {
            "status": "completed",
            "risk_score": risk_score,
            "vulnerability_count": len(all_vulns),
        })

        await progress.send_progress(scan_id, 100, "completed")
        await progress.send_result(scan_id, scan_result.model_dump())

    except Exception as e:
        logger.exception(f"Scan {scan_id} failed:")
        error_result = ScanResponse(
            id=scan_id,
            repo_url=repo_url,
            status=ScanStatus.FAILED,
            summary=f"Scan failed: {str(e)}",
            created_at=datetime.utcnow().isoformat(),
            progress=0,
            languages_detected=[],
        )
        _scan_results[scan_id] = error_result
        await DBService.update_scan(scan_id, {"status": "failed"})
        await progress.send_log(scan_id, f"ERROR: {str(e)}")
        await progress.send_progress(scan_id, 0, "failed")


@router.post("/scan", response_model=ScanResponse)
async def start_scan(req: ScanRequest, background_tasks: BackgroundTasks):
    """Start a new security scan."""
    scan_id = str(uuid.uuid4())[:12]

    scan = ScanResponse(
        id=scan_id,
        repo_url=req.repo_url,
        status=ScanStatus.QUEUED,
        created_at=datetime.utcnow().isoformat(),
        progress=0,
        languages_detected=[],
    )
    _scan_results[scan_id] = scan
    await DBService.create_scan(scan_id, req.repo_url)

    # Run scan in background
    background_tasks.add_task(_run_scan, scan_id, req.repo_url, req.github_token)
    return scan


@router.get("/scan/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: str):
    """Get scan status and results."""
    if scan_id in _scan_results:
        return _scan_results[scan_id]
    db_scan = await DBService.get_scan(scan_id)
    if db_scan:
        return ScanResponse(
            id=db_scan["id"],
            repo_url=db_scan["repo_url"],
            status=db_scan["status"],
            risk_score=db_scan.get("risk_score", 0),
            created_at=db_scan["created_at"],
            progress=100 if db_scan["status"] == "completed" else 0,
            languages_detected=[],
        )
    raise HTTPException(status_code=404, detail="Scan not found")


@router.get("/scans", response_model=list[ScanHistoryItem])
async def list_scans():
    """List all scans."""
    db_scans = await DBService.get_all_scans()
    return [
        ScanHistoryItem(
            id=s["id"],
            repo_url=s["repo_url"],
            status=s["status"],
            risk_score=s.get("risk_score", 0),
            vulnerability_count=s.get("vulnerability_count", 0),
            created_at=s["created_at"],
        )
        for s in db_scans
    ]


@router.get("/scan/{scan_id}/report")
async def download_report(scan_id: str):
    """Download PDF report for a completed scan."""
    if scan_id not in _pdf_cache:
        # Try to regenerate from stored results
        if scan_id in _scan_results and _scan_results[scan_id].status == ScanStatus.COMPLETED:
            try:
                pdf_bytes = ReportGenerator.generate(_scan_results[scan_id])
                _pdf_cache[scan_id] = pdf_bytes
            except Exception:
                raise HTTPException(status_code=500, detail="Failed to generate report")
        else:
            raise HTTPException(status_code=404, detail="Report not found")

    return Response(
        content=_pdf_cache[scan_id],
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=repoguard-report-{scan_id}.pdf"},
    )
