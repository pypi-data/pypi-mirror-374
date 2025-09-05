# dummysensors

[![PyPI version](https://img.shields.io/pypi/v/dummysensors.svg)](https://pypi.org/project/dummysensors/)
[![CI](https://github.com/SculptTechProject/dummysensors/actions/workflows/ci.yml/badge.svg)](https://github.com/SculptTechProject/dummysensors/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight generator of dummy sensor data for IoT and ML testing.
Provides a simple Python API and CLI, supports running multiple sensors in parallel and splitting output streams into files.

## Installation

```bash
pip install -e .
# for development:
pip install -r requirements.txt
```

## Quick Start (API)

```python
from dummysensors import TemperatureSensor, VibrationSensor

# create sensors
temp = TemperatureSensor(min_val=18, max_val=24, noise=0.2)
vib  = VibrationSensor(base_hz=50.0, amp=1.0, noise=0.05)

print(temp.read())            # e.g. 21.3
print(vib.read(t_s=0.123))    # sinusoidal signal with noise
```

## Quick Start (CLI)

Generate a single temperature stream to JSONL:

```bash
dummy-sensors generate --rate 5 --duration 2 --jsonl out/temp.jsonl
```

Run multiple sensors and devices, split by **type** into separate files:

```bash
dummy-sensors run \
  --rate 5 \
  --count 30 \
  --spec "device=engine-A: temp*1,vibration*2; device=room-101: temp*2" \
  --out "temp=out/temp.jsonl" \
  --out "vibration=out/vib.jsonl" \
  --out "*=stdout"
```

Each record is a JSON line:

```json
{
  "ts_ms": 1234,
  "device_id": "engine-A",
  "sensor_id": "temp-0",
  "type": "temp",
  "value": 21.04
}
```

## `--spec` format

The `--spec` string describes devices and sensors:

```
device=<ID>: <type>*<count>[, <type>*<count> ...] ; device=<ID2>: ...
```

Examples:

- `device=A: temp*3` — device A with three temperature sensors
- `device=eng: temp*1,vibration*2; device=room: temp*2`

> As of `v0.2`, supported sensor types: `temp`, `vibration`. More sensors and YAML configs coming soon.

## Python API

### `TemperatureSensor`

- Parameters: `min_val=15.0`, `max_val=30.0`, `noise=0.5`, `period_s=86400`
- Methods:
  - `read(t_s: float | None = None) -> float` — one sample (random within range + Gaussian noise)

### `VibrationSensor`

- Parameters: `base_hz=50.0`, `amp=1.0`, `noise=0.1`, `spike_prob=0.0`
- Methods:
  - `read(t_s: float | None = None) -> float` — sinusoidal signal at `base_hz` + noise

### Sensor Registry

- `dummysensors.registry.SENSOR_REGISTRY` — maps string `kind` → class
- `dummysensors.registry.make_sensor(kind: str, **params)`

### Orchestrator

- `dummysensors.orchestrator.run_stream(spec_str, rate_hz, duration_s, total_count, writer_for_type)`
  - Creates instances based on `spec_str`, emits samples at `rate_hz`.
  - `writer_for_type` is a dict `type → callable(sample_dict)`. `*` = default writer.

## Output Format

JSON Lines (one record per line):

```json
{
  "ts_ms": 171234,
  "device_id": "engine-A",
  "sensor_id": "vibration-1",
  "type": "vibration",
  "value": -0.124
}
```

Planned: CSV, Kafka, Redis Stream, WebSocket.

## Makefile

For convenience, run with `make`:

```make
make venv        # create .venv and upgrade pip
make install     # pip install -e .
make test        # pytest
make demo        # generate demo data into demo_out/
make clean       # cleanup build and cache
```

After `make demo`, check the files:

```bash
head -n 3 demo_out/temp.jsonl
head -n 3 demo_out/vibration.jsonl
```

## Development

- Project layout: **src-layout**
- Tests: `pytest -q`
- Lint/format: `ruff check src tests` and `ruff format`

Pull Requests welcome. Guidelines:

- Simple sensor classes
- No heavy runtime dependencies
- Test each public feature

## Roadmap

- `v0.2`
  - CSV writer
  - `partition_by=device`
  - YAML config (`--config config.yaml`)
- `v0.3`
  - AnomalyInjector (spike, dropout, drift)
  - New sensors: `humidity`, `rpm`, `battery_voltage`, `gps (trajectory)`, `accel 3-axis`
- `v0.4`
  - Outputs: Kafka, Redis Stream
  - Live preview (WebSocket demo)

## Versioning and Publishing

- Semantic versioning with tags `vX.Y.Z`.
- ​**CI**​: `.github/workflows/ci.yml` (lint + tests + build).
- ​**Publish**​: `.github/workflows/publish.yml` (Trusted Publishing to PyPI on release).

## License

MIT © Mateusz Dalke
