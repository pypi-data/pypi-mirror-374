from __future__ import annotations
from typing import Callable
from .registry import make_sensor
from .spec import parse_spec
import time
import json
import sys

def run_stream(
    spec_str: str,
    rate_hz: float,
    duration_s: float | None,
    total_count: int | None,
    writer_for_type: dict[str, Callable[[dict], None]],
    partition_by: str = "none",  # <--- NEW
):
    period = 1.0 / rate_hz if rate_hz > 0 else 0.0
    devices = parse_spec(spec_str)

    instances: list[tuple[str, str, str, object]] = []
    for d in devices:
        idx = {}
        for s in d.sensors:
            idx.setdefault(s.kind, 0)
            for _ in range(s.count):
                sensor = make_sensor(s.kind, **s.params)
                sid = f"{s.kind}-{idx[s.kind]}"
                instances.append((d.id, sid, s.kind, sensor))
                idx[s.kind] += 1

    default_writer = writer_for_type.get("*", lambda x: (sys.stdout.write(json.dumps(x)+"\n"), None)[1])

    # cache writerów per klucz (type/device/*)
    cache: dict[str, Callable[[dict], None]] = {}

    def _key(rec: dict) -> str:
        if partition_by == "device":
            return rec["device_id"]
        if partition_by == "type":
            return rec["type"]
        return "*"  # none

    def _writer_for(rec: dict) -> Callable[[dict], None]:
        k = _key(rec)
        if k in cache:
            return cache[k]
        # jeżeli jest mapowanie po konkretnym typie, użyj go
        if k in writer_for_type:
            cache[k] = writer_for_type[k]
        else:
            cache[k] = default_writer
        return cache[k]

    t0 = time.perf_counter()
    n = total_count if total_count is not None else int((duration_s or 0) * rate_hz)
    for i in range(n):
        t_s = time.perf_counter() - t0
        for dev, sid, kind, sensor in instances:
            val = sensor.read(t_s)  # type: ignore[attr-defined]
            rec = {"ts_ms": int(t_s*1000), "device_id": dev, "sensor_id": sid, "type": kind, "value": val}
            _writer_for(rec)(rec)
        if period > 0:
            t_next = t0 + (i + 1) * period
            while time.perf_counter() < t_next:
                time.sleep(min(0.002, t_next - time.perf_counter()))