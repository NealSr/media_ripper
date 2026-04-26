import re
import subprocess
from tqdm import tqdm

def stream_progress(cmd, pattern, total=100, desc=""):
    """
    Run a subprocess and update a tqdm progress bar based on regex matches.

    Args:
        cmd: list[str] — command to run
        pattern: compiled regex with a named group 'pct'
        total: int — usually 100
        desc: str — label for the progress bar
    """
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    bar = tqdm(total=total, desc=desc, unit="%", leave=True)

    for line in proc.stdout:
        match = pattern.search(line)
        if match:
            pct = float(match.group("pct"))
            bar.n = pct
            bar.refresh()

    proc.wait()
    bar.n = total
    bar.refresh()
    bar.close()

    return proc.returncode
