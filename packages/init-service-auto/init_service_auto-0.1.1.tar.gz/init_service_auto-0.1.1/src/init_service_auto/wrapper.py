import os
import subprocess
from pathlib import Path

def run():
    here = Path(__file__).resolve().parent
    binary = here / "bin" / "agent"
    subprocess.run([str(binary)])
