from typing import Callable, Any
from .sensors import TemperatureSensor, VibrationSensor

SENSOR_REGISTRY: dict[str, Callable[..., Any]] = {
    "temp": TemperatureSensor,
    "vibration": VibrationSensor,
}

def make_sensor(kind: str, **params):
    cls = SENSOR_REGISTRY.get(kind)
    if not cls:
        raise ValueError(f"Unknown sensor kind: {kind}")
    return cls(**params)
