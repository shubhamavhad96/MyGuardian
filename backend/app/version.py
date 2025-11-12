import os
import hashlib
from pathlib import Path
from datetime import datetime

def get_shadow_mode() -> bool:
    return os.getenv("GUARDRAIL_MODE", "enforce").lower() == "shadow"

def get_git_sha():
    sha = os.getenv("GIT_SHA")
    if sha:
        return sha
    
    try:
        git_dir = Path(__file__).parent.parent.parent / ".git"
        if git_dir.exists():
            head_file = git_dir / "HEAD"
            if head_file.exists():
                ref = head_file.read_text().strip()
                if ref.startswith("ref: "):
                    ref_path = git_dir / ref[5:]
                    if ref_path.exists():
                        return ref_path.read_text().strip()[:7]
                else:
                    return ref[:7]
    except Exception:
        pass
    
    return "unknown"

def get_git_tag():
    return os.getenv("GIT_TAG", "dev")

def get_policy_hash():
    try:
        policy_path = Path(__file__).parent.parent / "policy.yaml"
        if policy_path.exists():
            content = policy_path.read_text()
            return hashlib.sha256(content.encode()).hexdigest()[:8]
    except Exception:
        pass
    return "unknown"

def get_build_time():
    build_time = os.getenv("BUILD_TIME")
    if build_time:
        return build_time
    return datetime.utcnow().isoformat() + "Z"

def get_version_info():
    return {
        "git_sha": get_git_sha(),
        "git_tag": get_git_tag(),
        "policy_hash": get_policy_hash(),
        "build_time": get_build_time(),
        "version": "0.1-day6",
        "shadow_mode": get_shadow_mode(),
        "mode": os.getenv("GUARDRAIL_MODE", "enforce")
    }

