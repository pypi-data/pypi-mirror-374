from __future__ import annotations
import random
import math
from dataclasses import dataclass, field

@dataclass
class TemperatureSensor:
    type: str = field(default="temp", init=False)
    min_val: float = 15.0
    max_val: float = 30.0
    noise: float = 0.5
    period_s: float = 24 * 3600

    def __post_init__(self):
        # change if min > max
        if self.min_val > self.max_val:
            self.min_val, self.max_val = self.max_val, self.min_val
        # noise always positive
        if self.noise < 0:
            self.noise = abs(self.noise)

    def read(self, t_s: float | None = None) -> float:
        base = random.uniform(self.min_val, self.max_val)
        return base + random.gauss(0, self.noise)

@dataclass
class VibrationSensor:
    type: str = "vibration"
    base_hz: float = 50.0
    amp: float = 1.0
    noise: float = 0.1
    spike_prob: float = 0.0  # for tests 0

    def read(self, t_s: float | None = None) -> float:
        t_s = 0.0 if t_s is None else t_s
        sig = self.amp * math.sin(2 * math.pi * self.base_hz * t_s)
        sig += random.gauss(0, self.noise)
        return sig
