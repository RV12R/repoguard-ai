"""
Git clone service — securely clones repos into temp dirs and auto-deletes.
"""
import os
import shutil
import tempfile
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

logger = logging.getLogger(__name__)


class GitService:
    """Clone GitHub repos into temporary directories with auto-cleanup."""

    @staticmethod
    @asynccontextmanager
    async def clone_repo(
        repo_url: str,
        github_token: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Clone a GitHub repo to a temp directory.
        Yields the temp directory path. Auto-deletes on exit.
        """
        tmp_dir = tempfile.mkdtemp(prefix="repoguard_")
        try:
            # Build clone URL (inject token for private repos)
            clone_url = repo_url
            if github_token:
                # https://github.com/owner/repo -> https://{token}@github.com/owner/repo
                clone_url = repo_url.replace(
                    "https://github.com",
                    f"https://{github_token}@github.com",
                )

            import asyncio
            import shutil
            
            git_exe = shutil.which("git") or "git"

            process = await asyncio.create_subprocess_exec(
                git_exe, "clone", "--depth", "1", "--single-branch", clone_url, tmp_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                # Remove token from error messages
                if github_token:
                    error_msg = error_msg.replace(github_token, "***")
                raise RuntimeError(f"Git clone failed: {error_msg}")

            logger.info(f"Cloned repo to {tmp_dir}")
            yield tmp_dir

        finally:
            # Auto-delete: no persistent storage of code
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir, ignore_errors=True)
                logger.info(f"Cleaned up temp dir: {tmp_dir}")

    @staticmethod
    def detect_languages(repo_path: str) -> list[str]:
        """Detect programming languages in the repo by file extension."""
        extensions: dict[str, str] = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".jsx": "JavaScript",
            ".sol": "Solidity",
            ".rs": "Rust",
            ".go": "Go",
            ".java": "Java",
            ".rb": "Ruby",
            ".php": "PHP",
            ".c": "C",
            ".cpp": "C++",
            ".cs": "C#",
            ".swift": "Swift",
            ".kt": "Kotlin",
        }
        detected = set()
        for root, _, files in os.walk(repo_path):
            # Skip hidden dirs and node_modules
            if any(part.startswith(".") or part == "node_modules" for part in root.split(os.sep)):
                continue
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in extensions:
                    detected.add(extensions[ext])
        return sorted(detected)

    @staticmethod
    def count_files(repo_path: str) -> int:
        """Count source files in repo (excluding hidden/vendor dirs)."""
        count = 0
        for root, _, files in os.walk(repo_path):
            if any(part.startswith(".") or part in ("node_modules", "vendor", "__pycache__") for part in root.split(os.sep)):
                continue
            count += len(files)
        return count
