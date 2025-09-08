from datetime import datetime
from pydantic import BaseModel, Field
from .config import CPUUsageConfig, MemoryUsageConfig
from .enums import Status


class CPUUsage(BaseModel):
    raw: float = Field(..., ge=0.0, le=100.0, description="Raw CPU Usage (%)")
    smooth: float = Field(..., ge=0.0, le=100.0, description="Smooth CPU Usage (%)")
    status: Status = Field(Status.NORMAL, description="Usage status")

    @classmethod
    def calculate_new(
        cls,
        *,
        raw: float,
        smooth: float,
        config: CPUUsageConfig,
    ) -> "CPUUsage":
        if smooth < config.threshold.low:
            status = Status.LOW
        elif smooth < config.threshold.normal:
            status = Status.NORMAL
        elif smooth < config.threshold.high:
            status = Status.HIGH
        elif smooth < config.threshold.critical:
            status = Status.CRITICAL
        else:
            status = Status.OVERLOAD

        return cls(raw=raw, smooth=smooth, status=status)


class MemoryUsage(BaseModel):
    raw: float = Field(..., ge=0.0, description="Raw memory usage (MB)")
    percentage: float = Field(..., ge=0.0, description="Percentage of limit")
    status: Status = Field(Status.NORMAL, description="Usage status")

    @classmethod
    def calculate_new(cls, raw: float, config: MemoryUsageConfig) -> "MemoryUsage":
        percentage = (raw / config.limit) * 100
        if percentage < config.threshold.low:
            status = Status.LOW
        elif percentage < config.threshold.normal:
            status = Status.NORMAL
        elif percentage < config.threshold.high:
            status = Status.HIGH
        elif percentage < config.threshold.critical:
            status = Status.CRITICAL
        else:
            status = Status.OVERLOAD

        return cls(raw=raw, percentage=percentage, status=status)


class Usage(BaseModel):
    cpu: CPUUsage = Field(..., description="CPU Usage")
    memory: MemoryUsage = Field(..., description="Memory Usage")


class AverageOrPeakUsage(Usage):
    interval: int = Field(..., description="Measurement interval")


class Measurement(BaseModel):
    measured_at: datetime = Field(..., description="Measured at timestamp")
    usage: Usage = Field(..., description="Resource usage")
