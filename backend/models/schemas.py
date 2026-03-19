# Pydantic schemas for API request/response models
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum
import re


class ScanStatus(str, Enum):
    QUEUED = "queued"
    CLONING = "cloning"
    ANALYZING = "analyzing"
    AI_REVIEW = "ai_review"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ScanRequest(BaseModel):
    repo_url: str = Field(..., description="GitHub repository URL")
    github_token: Optional[str] = Field(None, description="GitHub token for private repos")

    @field_validator("repo_url")
    @classmethod
    def validate_github_url(cls, v: str) -> str:
        pattern = r"^https?://github\.com/[\w.\-]+/[\w.\-]+/?$"
        if not re.match(pattern, v.strip()):
            raise ValueError("Must be a valid GitHub repository URL (https://github.com/owner/repo)")
        # Sanitize: strip trailing slash, remove fragments/query
        return v.strip().rstrip("/").split("?")[0].split("#")[0]


class VulnerabilityOut(BaseModel):
    id: str
    title: str
    severity: Severity
    category: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    fix_suggestion: Optional[str] = None
    tool: str


class ScanResponse(BaseModel):
    id: str
    repo_url: str
    status: ScanStatus
    risk_score: int = 0
    vulnerabilities: list[VulnerabilityOut] = []
    summary: str = ""
    created_at: str
    completed_at: Optional[str] = None
    report_url: Optional[str] = None
    progress: int = 0
    languages_detected: list[str] = []


class ScanHistoryItem(BaseModel):
    id: str
    repo_url: str
    status: str
    risk_score: int
    vulnerability_count: int
    created_at: str


class FixRequest(BaseModel):
    github_token: str = Field(..., description="GitHub token with push access")


class FixResponse(BaseModel):
    branch: str
    pr_url: str


class ProgressMessage(BaseModel):
    type: str  # "log", "progress", "result"
    message: Optional[str] = None
    progress: Optional[int] = None
    status: Optional[str] = None
    scan: Optional[ScanResponse] = None
