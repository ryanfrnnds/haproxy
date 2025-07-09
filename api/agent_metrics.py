from pathlib import Path          #  ←  Faltava esta linha
import os, time
# ── localizar subpastas v1 ─────────────────────────────────────────────
CGROOT = Path("/sys/fs/cgroup")
CPU_DIR      = CGROOT / "cpu"         # quota / period vivem aqui
CPUACCT_DIR  = CGROOT / "cpuacct"     # usage vive aqui
MEM_DIR      = CGROOT / "memory"

def _read(p: Path) -> int:
    return int(p.read_text().strip())

# ── CPU % (v1) ─────────────────────────────────────────────────────────
def _cpu_pct_v1(sample=0.2) -> float:
    usage0 = _read(CPUACCT_DIR / "cpuacct.usage")      # ns
    quota  = _read(CPU_DIR / "cpu.cfs_quota_us")       # µs
    period = _read(CPU_DIR / "cpu.cfs_period_us")      # µs
    time.sleep(sample)
    usage1 = _read(CPUACCT_DIR / "cpuacct.usage")
    delta  = usage1 - usage0                           # ns

    if quota < 0:                                     # quota == -1 → sem limite
        vcpus = os.cpu_count() or 1
        pct = delta / (sample * 1e9 * vcpus) * 100
    else:
        pct = delta / (quota * 1000) * (period / (sample * 1e6)) * 100
    return min(100.0, max(0.0, pct))

# ── MEM % (v1) ─────────────────────────────────────────────────────────
def _mem_pct_v1() -> float:
    current = _read(MEM_DIR / "memory.usage_in_bytes")
    limit   = _read(MEM_DIR / "memory.limit_in_bytes")
    return current / limit * 100

# ── API pública ────────────────────────────────────────────────────────
def cpu_pct(sample=0.2):
    return _cpu_pct_v1(sample)

def mem_pct():
    return _mem_pct_v1()

# aliases retro-compatíveis
cpu_pct_cgroup = cpu_pct
mem_pct_cgroup = mem_pct
