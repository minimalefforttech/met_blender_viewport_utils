#!/usr/bin/env python
import os
import sys
import shutil
from pathlib import Path
from typing import List

_INSTALL_DIRS = ["PYTHON",]
_INSTALL_FILES = ["LICENSE", "README.md"]

def _copy_files(source_path:Path, target_path:Path, dirs:List[str], files:List[str]):
    for dirname in dirs:
        src = source_path / dirname
        dest = target_path / dirname
        if os.path.exists(dest):
            shutil.rmtree(dest)
        
        shutil.copytree(src, dest)
    
    for file in files:
        src = source_path / file
        dest = target_path / file
        shutil.copy(src, dest)


def build(source_path:Path, build_path:Path, install_path:Path, targets:List[str]):
    targets = targets or []
    
    _copy_files(source_path, build_path, _INSTALL_DIRS, _INSTALL_FILES)
    if "install" in targets:
        _copy_files(build_path, install_path, _INSTALL_DIRS, _INSTALL_FILES)


if __name__ == "__main__":
    build(
        source_path=Path(os.environ["REZ_BUILD_SOURCE_PATH"]),
        build_path=Path(os.environ["REZ_BUILD_PATH"]),
        install_path=Path(os.environ["REZ_BUILD_INSTALL_PATH"]),
        targets=sys.argv[1:]
    )