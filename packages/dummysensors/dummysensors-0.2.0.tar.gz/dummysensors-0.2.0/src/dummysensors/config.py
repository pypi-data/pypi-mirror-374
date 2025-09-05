from __future__ import annotations
from typing import Callable, Dict
from .orchestrator import run_stream
from .io import jsonl_writer
from .io import csv_writer
from pathlib import Path

DEFAULT_CONFIG_CANDIDATES = (
    "config.sensors.yaml",
    "config.sensors.yml",
    "dummysensors.yaml",
    "dummysensors.yml",
)

def find_config_path(start: str | None = None) -> str | None:
    """Return first matching config file path from DEFAULT_CONFIG_CANDIDATES in `start` or CWD."""
    base = Path(start) if start else Path.cwd()
    for name in DEFAULT_CONFIG_CANDIDATES:
        cand = base / name
        if cand.exists():
            return str(cand)
    return None

def _writer_for_decl(decl: dict):
    fmt = str(decl.get("type", "jsonl")).lower()
    path = decl.get("path")
    if fmt == "csv":
        if not path:
            raise ValueError("CSV output requires 'path' in config.")
        return csv_writer(str(path))
    # default jsonl; if path is None -> stdout
    return jsonl_writer(path)

def run_from_config(path: str) -> None:
    try:
        import yaml  # type: ignore
    except ImportError as e:
        raise RuntimeError("Install PyYAML to use --config (pip install pyyaml)") from e

    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    rate = float(cfg.get("rate", 5))
    duration = cfg.get("duration")
    count = cfg.get("count")

    # outputs
    writers: Dict[str, Callable[[dict], None]] = {}
    for out in cfg.get("outputs", []):
        k = out.get("for", "*")
        writers[k] = _writer_for_decl(out)

    # partitioning
    partition_by = cfg.get("partition_by", "none")

    # build spec_str z drzewa devices
    # devices: [{id: "engine-A", sensors: [{kind:"temp", count:2}, ...]}, ...]
    parts = []
    for dev in cfg.get("devices", []):
        sid = dev["id"]
        items = []
        for s in dev.get("sensors", []):
            kind = s["kind"]
            cnt = int(s.get("count", 1))
            items.append(f"{kind}*{cnt}")
        parts.append(f"device={sid}: " + ",".join(items))
    spec_str = "; ".join(parts)

    run_stream(
        spec_str,
        rate_hz=rate,
        duration_s=duration,
        total_count=count,
        writer_for_type=writers,
        partition_by=partition_by,
    )