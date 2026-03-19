"""
AI deep analysis service — uses Groq (primary) with Gemini fallback.
Detects: vulnerabilities, logic bugs, AI risks, Web3 issues.
"""
import os
import json
import logging
import uuid
from typing import Optional

from models.schemas import VulnerabilityOut, Severity

logger = logging.getLogger(__name__)

# System prompt for vulnerability analysis
ANALYSIS_PROMPT = """You are an expert security auditor. Analyze the following code for:

1. **Security Vulnerabilities**: SQL injection, XSS, CSRF, path traversal, auth issues, etc.
2. **Logic Bugs**: Race conditions, integer overflow, off-by-one, null pointer, etc.
3. **AI Risks** (if AI/LLM code detected): Prompt injection, data leakage, hallucination-prone patterns, unsafe deserialization of AI output.
4. **Web3/Solidity Issues** (if Solidity code detected): Reentrancy, access control flaws, integer overflow, front-running, oracle manipulation, unchecked return values.
5. **Optimization**: Performance issues, unnecessary complexity, memory leaks.

For each finding, respond with a JSON array of objects with these exact fields:
{
  "title": "Short descriptive title",
  "severity": "critical|high|medium|low|info",
  "category": "Category name",
  "description": "Detailed explanation of the vulnerability",
  "file_path": "path/to/file",
  "line_number": 42,
  "code_snippet": "The problematic code",
  "fix_suggestion": "How to fix it"
}

Return ONLY a valid JSON array. If no issues found, return [].
Be thorough but avoid false positives. Focus on real exploitable issues."""


def _collect_code_files(repo_path: str, max_files: int = 30, max_size: int = 8000) -> str:
    """Collect source files content into a single string for analysis."""
    code_extensions = {".py", ".js", ".ts", ".tsx", ".jsx", ".sol", ".rs", ".go", ".java", ".rb", ".php"}
    files_content = []
    total_chars = 0

    for root, dirs, files in os.walk(repo_path):
        # Skip hidden/vendor dirs
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "vendor", "__pycache__", ".git")]
        for fname in sorted(files):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in code_extensions:
                continue
            filepath = os.path.join(root, fname)
            relpath = os.path.relpath(filepath, repo_path)
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(max_size)
                files_content.append(f"\n--- FILE: {relpath} ---\n{content}")
                total_chars += len(content)
                if len(files_content) >= max_files or total_chars > 100000:
                    break
            except Exception:
                continue
        if len(files_content) >= max_files or total_chars > 100000:
            break

    return "\n".join(files_content)


class AIAnalyzer:
    """AI-powered code analysis using Groq (primary) and Gemini (fallback)."""

    @staticmethod
    async def _call_groq(code_context: str) -> Optional[list[dict]]:
        """Call Groq API (Llama 3.3 70B)."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.info("No GROQ_API_KEY set — skipping Groq")
            return None

        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=api_key)
            response = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": ANALYSIS_PROMPT},
                    {"role": "user", "content": f"Analyze this codebase:\n{code_context}"},
                ],
                temperature=0.1,
                max_tokens=4096,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if content:
                parsed = json.loads(content)
                # Handle both {"vulnerabilities": [...]} and [...]
                if isinstance(parsed, dict):
                    return parsed.get("vulnerabilities", parsed.get("findings", []))
                return parsed if isinstance(parsed, list) else []
        except Exception as e:
            logger.error(f"Groq API error: {e}")
        return None

    @staticmethod
    async def _call_gemini(code_context: str) -> Optional[list[dict]]:
        """Call Gemini API (fallback)."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.info("No GEMINI_API_KEY set — skipping Gemini fallback")
            return None

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = await model.generate_content_async(
                f"{ANALYSIS_PROMPT}\n\nAnalyze this codebase:\n{code_context}",
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=4096,
                    response_mime_type="application/json",
                ),
            )
            if response.text:
                parsed = json.loads(response.text)
                if isinstance(parsed, dict):
                    return parsed.get("vulnerabilities", parsed.get("findings", []))
                return parsed if isinstance(parsed, list) else []
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
        return None

    @staticmethod
    async def _call_xai(code_context: str) -> Optional[list[dict]]:
        """Call xAI API (grok-2) via standard httpx since it is OpenAI-compatible."""
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            return None

        try:
            import httpx
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": "grok-2-latest",
                "messages": [
                    {"role": "system", "content": ANALYSIS_PROMPT},
                    {"role": "user", "content": f"Analyze this codebase:\n{code_context}"},
                ],
                "temperature": 0.1,
                "stream": False
            }
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post("https://api.x.ai/v1/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                if content:
                    parsed = json.loads(content)
                    if isinstance(parsed, dict):
                        return parsed.get("vulnerabilities", parsed.get("findings", []))
                    return parsed if isinstance(parsed, list) else []
        except Exception as e:
            logger.error(f"xAI API error: {e}")
        return None

    @classmethod
    async def analyze(cls, repo_path: str) -> list[VulnerabilityOut]:
        """Run AI analysis with xAI primary, Groq secondary, and Gemini fallback."""
        code_context = _collect_code_files(repo_path)
        if not code_context.strip():
            return []

        # Cascade fallback: xAI -> Groq -> Gemini
        raw_findings = await cls._call_xai(code_context)
        if raw_findings is None:
            raw_findings = await cls._call_groq(code_context)
        if raw_findings is None:
            raw_findings = await cls._call_gemini(code_context)
        
        if raw_findings is None:
            logger.warning("No AI provider available — skipping AI analysis")
            return []

        # Convert to VulnerabilityOut
        vulns = []
        severity_map = {"critical": Severity.CRITICAL, "high": Severity.HIGH, "medium": Severity.MEDIUM, "low": Severity.LOW, "info": Severity.INFO}
        for finding in raw_findings:
            try:
                vulns.append(VulnerabilityOut(
                    id=str(uuid.uuid4())[:8],
                    title=finding.get("title", "Unknown Issue"),
                    severity=severity_map.get(finding.get("severity", "medium").lower(), Severity.MEDIUM),
                    category=finding.get("category", "AI Review"),
                    description=finding.get("description", ""),
                    file_path=finding.get("file_path", "unknown"),
                    line_number=finding.get("line_number"),
                    code_snippet=finding.get("code_snippet"),
                    fix_suggestion=finding.get("fix_suggestion"),
                    tool="AI-Review",
                ))
            except Exception as e:
                logger.warning(f"Failed to parse AI finding: {e}")
        return vulns
