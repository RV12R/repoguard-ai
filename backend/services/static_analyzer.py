"""
Static analysis orchestrator — runs Semgrep and Bandit, normalizes output.
"""
import asyncio
import json
import logging
import uuid
from typing import Optional

from models.schemas import VulnerabilityOut, Severity

logger = logging.getLogger(__name__)


SEVERITY_MAP = {
    "ERROR": Severity.CRITICAL,
    "WARNING": Severity.HIGH,
    "INFO": Severity.MEDIUM,
    "CRITICAL": Severity.CRITICAL,
    "HIGH": Severity.HIGH,
    "MEDIUM": Severity.MEDIUM,
    "LOW": Severity.LOW,
}


class StaticAnalyzer:
    """Run Semgrep + Bandit and normalize findings."""

    @staticmethod
    async def run_semgrep(repo_path: str) -> list[VulnerabilityOut]:
        """Run Semgrep auto-scan and parse JSON results."""
        vulns: list[VulnerabilityOut] = []
        try:
            process = await asyncio.create_subprocess_exec(
                "semgrep", "scan", "--json", "--config=auto", repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if stdout:
                data = json.loads(stdout.decode())
                for result in data.get("results", []):
                    severity_str = result.get("extra", {}).get("severity", "INFO").upper()
                    vulns.append(VulnerabilityOut(
                        id=str(uuid.uuid4())[:8],
                        title=result.get("check_id", "Unknown").split(".")[-1].replace("-", " ").title(),
                        severity=SEVERITY_MAP.get(severity_str, Severity.MEDIUM),
                        category=result.get("extra", {}).get("metadata", {}).get("category", "Security"),
                        description=result.get("extra", {}).get("message", "No description"),
                        file_path=result.get("path", "unknown"),
                        line_number=result.get("start", {}).get("line"),
                        code_snippet=result.get("extra", {}).get("lines", ""),
                        fix_suggestion=result.get("extra", {}).get("fix", None),
                        tool="Semgrep",
                    ))
        except FileNotFoundError:
            logger.warning("Semgrep not installed — skipping")
        except Exception as e:
            logger.error(f"Semgrep error: {e}")
        return vulns

    @staticmethod
    async def run_bandit(repo_path: str) -> list[VulnerabilityOut]:
        """Run Bandit (Python security linter) and parse JSON results."""
        vulns: list[VulnerabilityOut] = []
        try:
            process = await asyncio.create_subprocess_exec(
                "bandit", "-r", repo_path, "-f", "json", "-q",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await process.communicate()

            if stdout:
                data = json.loads(stdout.decode())
                for result in data.get("results", []):
                    severity_str = result.get("issue_severity", "MEDIUM").upper()
                    vulns.append(VulnerabilityOut(
                        id=str(uuid.uuid4())[:8],
                        title=result.get("issue_text", "Unknown Issue"),
                        severity=SEVERITY_MAP.get(severity_str, Severity.MEDIUM),
                        category="Security",
                        description=f"{result.get('issue_text', '')} (CWE: {result.get('issue_cwe', {}).get('id', 'N/A')})",
                        file_path=result.get("filename", "unknown"),
                        line_number=result.get("line_number"),
                        code_snippet=result.get("code", ""),
                        fix_suggestion=None,
                        tool="Bandit",
                    ))
        except FileNotFoundError:
            logger.warning("Bandit not installed — skipping")
        except Exception as e:
            logger.error(f"Bandit error: {e}")
        return vulns

    @classmethod
    async def analyze(cls, repo_path: str) -> list[VulnerabilityOut]:
        """Run all static analyzers in parallel."""
        semgrep_results, bandit_results = await asyncio.gather(
            cls.run_semgrep(repo_path),
            cls.run_bandit(repo_path),
        )
        # Deduplicate by file+line
        seen = set()
        combined = []
        for vuln in semgrep_results + bandit_results:
            key = (vuln.file_path, vuln.line_number, vuln.title)
            if key not in seen:
                seen.add(key)
                combined.append(vuln)
        return combined
