import subprocess, shlex

def site_reachable(url: str, timeout: int = 8) -> str:
    try:
        cmd = f"curl -I -L --max-time {timeout} -s -o /dev/null -w '%{{http_code}}' {shlex.quote(url)}"
        code = subprocess.check_output(cmd, shell=True, text=True).strip()
        return code if code.isdigit() else "NA"
    except Exception:
        return "NA"
