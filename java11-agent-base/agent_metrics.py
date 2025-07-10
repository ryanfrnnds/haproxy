from pathlib import Path
import os, time

CGROOT = Path("/sys/fs/cgroup")
CPU_DIR = CGROOT / "cpu"
CPUACCT_DIR = CGROOT / "cpuacct"
MEM_DIR = CGROOT / "memory"

def _read(p: Path) -> int:
    return int(p.read_text().strip())

def _cpu_pct_v1(sample=0.2) -> float:
    usage0 = _read(CPUACCT_DIR / "cpuacct.usage")
    quota = _read(CPU_DIR / "cpu.cfs_quota_us")
    period = _read(CPU_DIR / "cpu.cfs_period_us")
    time.sleep(sample)
    usage1 = _read(CPUACCT_DIR / "cpuacct.usage")
    delta = usage1 - usage0

    if quota < 0:
        vcpus = os.cpu_count() or 1
        pct = delta / (sample * 1e9 * vcpus) * 100
    else:
        pct = delta / (quota * 1000) * (period / (sample * 1e6)) * 100
    return min(100.0, max(0.0, pct))

def _mem_pct_v1() -> float:
    current = _read(MEM_DIR / "memory.usage_in_bytes")
    limit = _read(MEM_DIR / "memory.limit_in_bytes")
    return current / limit * 100

def cpu_pct(sample=0.2):
    return _cpu_pct_v1(sample)

def mem_pct():
    return _mem_pct_v1()