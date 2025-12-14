#!/usr/bin/env python3
"""Build x64 backend using Rosetta"""
import os
import sys
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
BINARIES_DIR = SCRIPT_DIR.parent / "src-tauri" / "binaries"

def main():
    print("Building x64 backend via Rosetta...")
    
    # Ensure binaries dir exists
    BINARIES_DIR.mkdir(parents=True, exist_ok=True)
    
    output_name = "xfactor-backend-x86_64-apple-darwin"
    output_path = BINARIES_DIR / output_name
    
    # Build using PyInstaller
    spec_file = SCRIPT_DIR / "backend.spec"
    run_backend = SCRIPT_DIR / "run_backend.py"
    
    cmd = [
        "arch", "-x86_64", sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", output_name,
        "--distpath", str(BINARIES_DIR),
        "--workpath", str(SCRIPT_DIR / "build_x64"),
        "--specpath", str(SCRIPT_DIR),
        "--clean",
        "--noconfirm",
        str(run_backend)
    ]
    
    print(f"Running: {' '.join(cmd[:6])}...")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    
    if result.returncode == 0 and output_path.exists():
        os.chmod(output_path, 0o755)
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"✓ x64 backend built: {output_path}")
        print(f"  Size: {size_mb:.1f} MB")
    else:
        print("✗ Build failed")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
