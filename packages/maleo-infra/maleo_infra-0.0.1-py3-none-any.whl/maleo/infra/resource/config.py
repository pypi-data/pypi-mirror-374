from pydantic import BaseModel, Field


class MeasurementConfig(BaseModel):
    interval: float = Field(5.0, ge=5.0, description="Monitor interval")
    window: int = Field(5, ge=5, description="Smoothing window")


DEFAULT_MEASUREMENT_CONFIG = MeasurementConfig(interval=5.0, window=5)


class ThresholdConfig(BaseModel):
    low: float = Field(10.0, ge=0.0, description="Low threshold")
    normal: float = Field(75.0, ge=0.0, description="Normal threshold")
    high: float = Field(85.0, ge=0.0, description="High threshold")
    critical: float = Field(95.0, ge=0.0, description="Critical threshold")


DEFAULT_THRESHOLD = ThresholdConfig(low=10.0, normal=75.0, high=85.0, critical=95.0)


class CPUUsageConfig(BaseModel):
    threshold: ThresholdConfig = Field(DEFAULT_THRESHOLD, description="Threshold")


DEFAULT_CPU_USAGE_CONFIG = CPUUsageConfig(threshold=DEFAULT_THRESHOLD)


class MemoryUsageConfig(BaseModel):
    limit: float = Field(
        1024.0,
        ge=0.0,
        description="Memory limit (MB) applied to raw memory value",
    )
    threshold: ThresholdConfig = Field(DEFAULT_THRESHOLD, description="Threshold")


DEFAULT_MEMORY_USAGE_CONFIG = MemoryUsageConfig(
    limit=1024.0, threshold=DEFAULT_THRESHOLD
)


class UsageConfig(BaseModel):
    cpu: CPUUsageConfig = Field(DEFAULT_CPU_USAGE_CONFIG, description="CPU Usage")
    memory: MemoryUsageConfig = Field(
        DEFAULT_MEMORY_USAGE_CONFIG, description="Memory Usage"
    )


DEFAULT_USAGE_CONFIG = UsageConfig(
    cpu=DEFAULT_CPU_USAGE_CONFIG, memory=DEFAULT_MEMORY_USAGE_CONFIG
)


class Config(BaseModel):
    measurement: MeasurementConfig = Field(
        DEFAULT_MEASUREMENT_CONFIG, description="Resource usage configuration"
    )
    retention: int = Field(
        3600, ge=60, le=7200, multiple_of=60, description="Monitor data retention (s)"
    )
    usage: UsageConfig = Field(DEFAULT_USAGE_CONFIG, description="Usage config")


DEFAULT_CONFIG = Config(
    measurement=DEFAULT_MEASUREMENT_CONFIG, retention=3600, usage=DEFAULT_USAGE_CONFIG
)


class ConfigMixin(BaseModel):
    resource: Config = Field(DEFAULT_CONFIG, description="Resource config")
