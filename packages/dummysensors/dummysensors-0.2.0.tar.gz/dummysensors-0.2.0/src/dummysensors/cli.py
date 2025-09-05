from __future__ import annotations
import argparse 
import time
from .sensors import TemperatureSensor
from .orchestrator import run_stream
from .io import jsonl_writer, csv_writer

def _stdout_writer():
    return jsonl_writer(None)

def _jsonl_file_writer(path: str):
    return jsonl_writer(path)

def _csv_file_writer(path: str):
    return csv_writer(path)

def _make_writer_map(out_args: list[str] | None):
    """
    out args format: ["temp=out/temp.jsonl", "vibration=out/vib.csv", "*=stdout"]
    wybór formatu po rozszerzeniu pliku: .jsonl -> JSONL, .csv -> CSV
    """
    mapping = {}
    if not out_args:
        return mapping
    for s in out_args:
        key, dest = s.split("=", 1)
        key = key.strip()
        dest = dest.strip()
        if dest == "stdout":
            mapping[key] = _stdout_writer()
        else:
            if dest.lower().endswith(".csv"):
                mapping[key] = _csv_file_writer(dest)
            else:
                mapping[key] = _jsonl_file_writer(dest)
    return mapping

def main(argv=None):
    p = argparse.ArgumentParser(prog="dummy-sensors")
    sub = p.add_subparsers(dest="cmd", required=True)

    gen = sub.add_parser("generate", help="single temperature stream to stdout/file")
    gen.add_argument("--rate", type=float, default=5.0)
    gen.add_argument("--duration", type=float, default=5.0)
    gen.add_argument("--count", type=int, default=None)
    gen.add_argument("--min", dest="min_val", type=float, default=15.0)
    gen.add_argument("--max", dest="max_val", type=float, default=30.0)
    gen.add_argument("--noise", type=float, default=0.5)
    gen.add_argument("--jsonl", type=str, default=None)

    run = sub.add_parser("run", help="multi-device/multi-sensor run via spec or config")
    run.add_argument("--rate", type=float, default=5.0)
    run.add_argument("--duration", type=float, default=None)
    run.add_argument("--count", type=int, default=None)
    run.add_argument("--spec", type=str, help='e.g. "device=A: temp*2,vibration*1"')
    run.add_argument("--out", action="append", help='mapping like "temp=out/temp.jsonl", "*=stdout"', default=None)
    run.add_argument("--partition-by", choices=["none","type","device"], default="none")
    run.add_argument("--config", type=str, help="YAML config path (overrides --spec/--out)")

    args = p.parse_args(argv)

    if args.cmd == "generate":
        writer = _jsonl_file_writer(args.jsonl) if args.jsonl else _stdout_writer()
        s = TemperatureSensor(min_val=args.min_val, max_val=args.max_val, noise=args.noise)
        period = 1.0 / args.rate if args.rate > 0 else 0.0
        total = args.count if args.count is not None else int(args.duration * args.rate)
        t0 = time.perf_counter()
        for i in range(total):
            t_s = time.perf_counter() - t0
            val = s.read()
            writer({"ts_ms": int(t_s*1000), "device_id": "dev-0", "sensor_id": "temp-0", "type": "temp", "value": float(val)})
            if period > 0:
                t_next = t0 + (i + 1) * period
                while time.perf_counter() < t_next:
                    time.sleep(min(0.002, t_next - time.perf_counter()))
    else:
        # jeśli podano --config, jedziemy konfiguracją YAML (sekcja 4)
        if args.config:
            from .config import run_from_config
            run_from_config(args.config)
            return

        # spec + out
        writers = _make_writer_map(args.out)
        if not args.spec:
            p.error("Provide --spec or --config")
        run_stream(args.spec, rate_hz=args.rate, duration_s=args.duration, total_count=args.count,
                   writer_for_type=writers, partition_by=args.partition_by)