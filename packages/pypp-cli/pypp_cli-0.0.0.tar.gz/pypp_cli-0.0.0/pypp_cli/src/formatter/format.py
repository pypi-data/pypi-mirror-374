import os
import subprocess
from functools import partial
from multiprocessing import Pool
from pathlib import Path


def _format_file(file: Path, cpp_dir: Path):
    # clang-format -i --style=file main.cpp
    subprocess.run(
        ["clang-format", "-i", "--style=file", str(file)], cwd=cpp_dir, check=True
    )


def pypp_format(files_added_or_modified: list[Path], cpp_dir: Path):
    num_cores = os.cpu_count() or 1  # Fallback to 1 if None
    with Pool(num_cores) as p:  # Adjust number of workers
        p.map(partial(_format_file, cpp_dir=cpp_dir), files_added_or_modified)
    print(
        f"Py++ format finished. "
        f"files formatted: {len(files_added_or_modified)}, "
        f"cores used: {num_cores}"
    )
