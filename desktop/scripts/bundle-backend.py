#!/usr/bin/env python3
"""
Bundle the Python backend for desktop distribution using PyInstaller.

This creates a standalone executable that can be bundled with the Tauri app.
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path


def main():
    # Get project paths
    script_dir = Path(__file__).parent
    desktop_dir = script_dir.parent
    project_root = desktop_dir.parent
    
    print(f"Project root: {project_root}")
    print(f"Desktop dir: {desktop_dir}")
    
    # Output directory for bundled backend
    output_dir = desktop_dir / "bundled-backend"
    output_dir.mkdir(exist_ok=True)
    
    # PyInstaller spec file content
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

project_root = Path(r"{project_root}")
src_dir = project_root / "src"

a = Analysis(
    [str(project_root / "src" / "main.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        (str(src_dir / "config"), "src/config"),
        (str(src_dir / "strategies"), "src/strategies"),
    ],
    hiddenimports=[
        "uvicorn.logging",
        "uvicorn.lifespan.on",
        "uvicorn.lifespan.off",
        "uvicorn.lifespan",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.protocols.http.httptools_impl",
        "uvicorn.protocols.websockets.websockets_impl",
        "fastapi",
        "pydantic",
        "numpy",
        "pandas",
        "yfinance",
        "redis",
        "aiohttp",
        "websockets",
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='xfactor-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False for production
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    # Write spec file
    spec_file = output_dir / "xfactor-backend.spec"
    spec_file.write_text(spec_content)
    print(f"Created PyInstaller spec: {spec_file}")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Run PyInstaller
    print("\nBuilding backend executable...")
    result = subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "--workpath", str(output_dir / "build"),
            "--distpath", str(output_dir / "dist"),
            str(spec_file),
        ],
        cwd=str(project_root),
    )
    
    if result.returncode == 0:
        print(f"\n✅ Backend bundled successfully!")
        print(f"   Output: {output_dir / 'dist' / 'xfactor-backend'}")
    else:
        print(f"\n❌ Build failed with code {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    main()

