# dummysensors

[![PyPI version](https://img.shields.io/pypi/v/dummysensors.svg)](https://pypi.org/project/dummysensors/)
[![CI](https://github.com/SculptTechProject/dummysensors/actions/workflows/ci.yml/badge.svg)](https://github.com/SculptTechProject/dummysensors/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A lightweight generator of dummy sensor data for IoT and ML testing.
Provides a simple Python API and CLI, supports running multiple sensors in parallel, photovoltaic domain sensors, and splitting output streams into files.

---

## Installation

From PyPI (recommended):

```bash
pip install dummysensors
```

---

## Quick Start (API)

```python
from dummysensors import TemperatureSensor, VibrationSensor

# create sensors
temp = TemperatureSensor(min_val=18, max_val=24, noise=0.2)
vib  = VibrationSensor(base_hz=50.0, amp=1.0, noise=0.05)

print(temp.read())            # e.g. 21.3
print(vib.read(t_s=0.123))    # sinusoidal signal with noise
```

---

## Config file (YAML)

Instead of passing long `--spec` strings, you can define your setup in a YAML file.
By default, `dummy-sensors run --config config.sensors.yaml` will look for a file named `config.sensors.yaml` in the current directory.

### Example `config.sensors.yaml`

```yaml
rate: 2
count: 5
partition_by: type

outputs:
  - type: jsonl
    for: temp
    path: out/temp.jsonl
  - type: csv
    for: vibration
    path: out/vibration.csv

devices:
  - id: engine-A
    sensors:
      - kind: temp
        count: 1
      - kind: vibration
        count: 1
  - id: plant-1
    sensors:
      - kind: irradiance
        count: 1
        params: {peak: 900.0, day_period_s: 10.0, sunrise: 0.0, sunset: 10.0}
      - kind: pv_power
        count: 1
        params: {stc_kw: 5.0, inverter_eff: 0.95, p_kw_max: 4.8}
      - kind: load
        count: 1
        params: {base_kw: 0.3, morning_kw: 0.8, evening_kw: 1.2}
      - kind: soc
        count: 1
        params: {capacity_kwh: 10.0, soc0: 50.0}
```

Run with:

```bash
dummy-sensors run --config config.sensors.yaml
```

---

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

> 👉 Check out a full demo with live plotting and JSONL logging here:
> [dummysensors demo (ds-test)](https://github.com/SculptTechProject/ds-test)

---

## `--spec` format

The `--spec` string describes devices and sensors:

```
device=<ID>: <type>*<count>[, <type>*<count> ...] ; device=<ID2>: ...
```

Examples:

* `device=A: temp*3` — device A with three temperature sensors
* `device=eng: temp*1,vibration*2; device=room: temp*2`

> As of `v0.3`, supported sensor types:
> `temp`, `vibration`, `irradiance`, `pv_power`, `load`, `soc`.
> You can define setups either with `--spec` (quick inline config) or using a YAML file (`--config config.sensors.yaml`) for more complex scenarios.

---

## Python API

### `TemperatureSensor`

* Parameters: `min_val=15.0`, `max_val=30.0`, `noise=0.5`, `period_s=86400`
* Methods: `read(t_s: float | None = None) -> float`

### `VibrationSensor`

* Parameters: `base_hz=50.0`, `amp=1.0`, `noise=0.1`, `spike_prob=0.0`
* Methods: `read(t_s: float | None = None) -> float`

### `IrradianceSensor`

* Simulates solar irradiance with day/night cycle.
* Parameters: `peak`, `day_period_s`, `sunrise`, `sunset`

### `PVPowerSensor`

* Converts irradiance into PV output.
* Parameters: `stc_kw`, `inverter_eff`, `p_kw_max`

### `LoadSensor`

* Simulates household/plant consumption profile.
* Parameters: `base_kw`, `morning_kw`, `evening_kw`, `day_period_s`

### `BatterySoCSensor`

* Integrates charge/discharge depending on PV vs load.
* Parameters: `capacity_kwh`, `soc0`

### Sensor Registry

* `dummysensors.registry.SENSOR_REGISTRY` — maps string `kind` → class
* `dummysensors.registry.make_sensor(kind: str, **params)`

### Orchestrator

* `dummysensors.orchestrator.run_stream(...)`

  * Creates instances based on `spec_str` or `config`, respects **priority** and **per-sensor rate\_hz**.
  * `writer_for_type` is a dict `type → callable(sample_dict)`. `*` = default writer.

---

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

Also supported: **CSV**. Planned: Kafka, Redis Stream, WebSocket.

---

## Roadmap

* `v0.2` ✅ — CSV writer, partitioning, YAML config
* `v0.3` ✅ — Smart photovoltaic sensors (`irradiance`, `pv_power`, `load`, `soc`), per-sensor `rate_hz`, priority-based orchestration
* `v0.4` 🚧 — AnomalyInjector (spike, dropout, drift), new sensors (`humidity`, `rpm`, `battery_voltage`, `gps`, `accel-3axis`)
* `v0.5` 🚧 — Outputs: Kafka, Redis Stream, WebSocket live preview

---

## Development

```bash
git clone https://github.com/SculptTechProject/dummysensors
cd dummysensors
pip install -e .
pip install -r requirements.txt
```

* Project layout: **src-layout**
* Tests: `pytest -q`
* Lint/format: `ruff check src tests` and `ruff format`

---

## License

MIT © Mateusz Dalke
