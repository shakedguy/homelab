# #!/usr/bin/env python3
# """
# Fast branch lister for fzf-tab git checkout/switch completion.

# Features:
#   - Caches per-repo branch listings on disk using refs/HEAD mtimes.
#   - Defaults to local branches only (fast). Set GIT_FZF_INCLUDE_REMOTES=1 to add remotes.
# Output format:
#   refname<TAB>short_sha<TAB>committerdate_relative<TAB>author
# """

# from __future__ import annotations

# import hashlib
# import json
# import os
# import subprocess
# import sys
# from pathlib import Path
# from typing import Iterable, List, Optional


# def run_git(args: list[str]) -> Optional[str]:
#     try:
#         return (
#             subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL)
#             .decode()
#             .strip()
#         )
#     except subprocess.CalledProcessError:
#         return None


# def git_dir() -> Optional[Path]:
#     out = run_git(["rev-parse", "--git-dir"])
#     return Path(out).resolve() if out else None


# def path_mtime(p: Path) -> int:
#     try:
#         return int(p.stat().st_mtime)
#     except FileNotFoundError:
#         return 0


# def cache_path(repo_git_dir: Path) -> Path:
#     cache_root = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
#     cache_root = cache_root / "git-fzf"
#     cache_root.mkdir(parents=True, exist_ok=True)
#     key = hashlib.sha1(str(repo_git_dir).encode()).hexdigest()
#     return cache_root / f"{key}.json"


# def load_cache(path: Path) -> Optional[dict]:
#     try:
#         return json.loads(path.read_text())
#     except Exception:
#         return None


# def save_cache(path: Path, data: dict) -> None:
#     try:
#         path.write_text(json.dumps(data))
#     except Exception:
#         pass


# def collect_branches(include_remotes: bool) -> List[str]:
#     refs = ["refs/heads"]
#     if include_remotes:
#         refs.append("refs/remotes")
#     out = run_git(
#         [
#             "for-each-ref",
#             "--sort=-committerdate",
#             '--format=%(refname:short)\t%(objectname:short)\t%(committerdate:relative)\t%(authorname)',
#             *refs,
#         ]
#     )
#     if out is None:
#         return []
#     return [line for line in out.splitlines() if line.strip()]


# def main() -> int:
#     repo_git_dir = git_dir()
#     if not repo_git_dir:
#         return 0

#     refs_mtime = path_mtime(repo_git_dir / "refs")
#     head_mtime = path_mtime(repo_git_dir / "HEAD")
#     include_remotes = os.environ.get("GIT_FZF_INCLUDE_REMOTES") == "1"

#     cpath = cache_path(repo_git_dir)
#     cache = load_cache(cpath)
#     if (
#         cache
#         and cache.get("refs_mtime") == refs_mtime
#         and cache.get("head_mtime") == head_mtime
#         and cache.get("include_remotes") == include_remotes
#     ):
#         entries = cache.get("entries", [])
#     else:
#         entries = collect_branches(include_remotes)
#         save_cache(
#             cpath,
#             {
#                 "refs_mtime": refs_mtime,
#                 "head_mtime": head_mtime,
#                 "include_remotes": include_remotes,
#                 "entries": entries,
#             },
#         )

#     sys.stdout.write("\n".join(entries))
#     return 0


# if __name__ == "__main__":
#     raise SystemExit(main())