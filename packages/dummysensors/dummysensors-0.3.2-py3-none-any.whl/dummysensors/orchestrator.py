from __future__ import annotations
from typing import Callable
from .registry import make_sensor
from .spec import parse_spec
from typing import Dict
from typing import Any
from typing import List
from typing import Tuple
import time
import json
import sys

# default priorities if not given
_DEFAULT_PRIORITY = {"irradiance": 0, "pv_power": 1, "load": 2, "soc": 3}

def _sensor_priority(kind: str, override: int | None) -> int:
    if override is not None:
        return int(override)
    return _DEFAULT_PRIORITY.get(kind, 10)

def run_stream(
    spec_str: str,
    rate_hz: float,
    duration_s: float | None,
    total_count: int | None,
    writer_for_type: Dict[str, Callable[[dict], None]],
    partition_by: str = "none",
    devices_cfg: List[dict] | None = None,
) -> None:
    """
    Smart orchestrator:
      - builds instances either from devices_cfg (YAML) or from spec_str
      - per-sensor priority and (optional) per-sensor rate_hz
      - per-device tick context (e.g., irradiance -> pv_power -> load -> soc)
    """
    period_global = 1.0 / rate_hz if rate_hz > 0 else 0.0

    # 1) Build instances
    #    item: (device_id, sensor_id, kind, sensor_obj, priority, rate_hz_individual)
    instances: list[tuple[str, str, str, Any, int, float | None]] = []

    if devices_cfg:
        for dev in devices_cfg:
            did = dev["id"]
            idx: Dict[str, int] = {}
            for s in dev.get("sensors", []):
                kind = s["kind"]
                cnt = int(s.get("count", 1))
                prio = _sensor_priority(kind, s.get("priority"))
                rate_ind = s.get("rate_hz")  # None -> use global
                params = s.get("params", {}) or {}
                idx.setdefault(kind, 0)
                for _ in range(cnt):
                    sensor = make_sensor(kind, **params)
                    sid = f"{kind}-{idx[kind]}"
                    instances.append((did, sid, kind, sensor, prio, rate_ind))
                    idx[kind] += 1
    else:
        # fallback: current string spec (no params/priority/rate per sensor)
        devices = parse_spec(spec_str)
        for d in devices:
            idx: Dict[str, int] = {}
            for s in d.sensors:
                idx.setdefault(s.kind, 0)
                for _ in range(s.count):
                    sensor = make_sensor(s.kind, **s.params)
                    sid = f"{s.kind}-{idx[s.kind]}"
                    prio = _sensor_priority(s.kind, None)
                    instances.append((d.id, sid, s.kind, sensor, prio, None))
                    idx[s.kind] += 1

    # sort by priority (lower first)
    instances.sort(key=lambda it: it[4])

    # 2) Writers (partition cache)
    default_writer = writer_for_type.get(
        "*", lambda x: (sys.stdout.write(json.dumps(x) + "\n"), None)[1]
    )
    cache: Dict[str, Callable[[dict], None]] = {}

    def _key(rec: dict) -> str:
        if partition_by == "device":
            return rec["device_id"]
        if partition_by == "type":
            return rec["type"]
        return "*"

    def _writer_for(rec: dict) -> Callable[[dict], None]:
        k = _key(rec)
        if k not in cache:
            cache[k] = writer_for_type.get(k, default_writer)
        return cache[k]

    # 3) Main loop
    t0 = time.perf_counter()
    n = total_count if total_count is not None else int(max(0.0, (duration_s or 0)) * rate_hz)

    # per-sensor next due time (for per-sensor rate)
    next_due: Dict[Tuple[str, str], float] = {}  # (dev, sid) -> abs time
    for dev, sid, kind, *_ in instances:
        next_due[(dev, sid)] = t0  # schedule now

    for i in range(n):
        now = time.perf_counter()
        t_s = now - t0

        # per-device context for this tick
        device_ctx: Dict[str, Dict[str, float]] = {}

        for dev, sid, kind, sensor, _prio, rate_ind in instances:
            # honor per-sensor rate if provided
            per = (1.0 / rate_ind) if (rate_ind and rate_ind > 0) else period_global
            due = next_due[(dev, sid)]
            if per > 0 and now < due:
                continue  # not yet time for this sensor

            device_ctx.setdefault(dev, {})
            ctx = device_ctx[dev]

            # dependency-aware branches
            if kind == "pv_power":
                irr = ctx.get("irradiance", 0.0)
                val = sensor.read(t_s, irradiance=irr) # type: ignore[attr-defined]
            elif kind == "soc":
                load = ctx.get("load", 0.0)
                pv   = ctx.get("pv_power", 0.0)
                net = load - pv
                val = sensor.step(t_s, net) # type: ignore[attr-defined]
            else:
                val = sensor.read(t_s) # type: ignore[attr-defined]

            ctx[kind] = float(val)

            rec = {
                "ts_ms": int(t_s * 1000),
                "device_id": dev,
                "sensor_id": sid,
                "type": kind,
                "value": float(val),
            }
            _writer_for(rec)(rec)

            # schedule next due time for this sensor
            next_due[(dev, sid)] = now + (per if per > 0 else 0)

        # global pacing (keeps rough global rate even with per-sensor rates)
        if period_global > 0:
            t_next = t0 + (i + 1) * period_global
            while True:
                now2 = time.perf_counter()
                if now2 >= t_next:
                    break
                time.sleep(min(0.002, t_next - now2))