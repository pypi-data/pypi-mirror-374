import asyncio
import os
import traceback
import psutil
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Optional, List
from uuid import uuid4
from maleo.dtos.contexts.operation import generate_operation_context
from maleo.dtos.contexts.service import ServiceContext
from maleo.enums.operation import (
    SystemOperationType,
    Origin,
    Layer,
    Target,
)
from maleo.logging.enums import Level
from maleo.logging.logger import Application
from maleo.mixins.timestamp import OperationTimestamp
from maleo.schemas.operation.system import (
    SystemOperationAction,
    SuccessfulSystemOperation,
)
from maleo.schemas.response import SingleDataResponse
from .config import Config
from .data import CPUUsage, MemoryUsage, Usage, AverageOrPeakUsage, Measurement


class ResourceMonitor:
    def __init__(
        self,
        config: Config,
        logger: Application,
        service_context: Optional[ServiceContext] = None,
    ):
        self.service_context = (
            service_context
            if service_context is not None
            else ServiceContext.from_env()
        )
        self.config = config
        self.logger = logger
        self.process = psutil.Process(os.getpid())
        self.cpu_window = deque(maxlen=self.config.measurement.window)

        # Store historical data with timestamps
        self.measurement_history: deque[Measurement] = deque(
            maxlen=1000
        )  # Adjust max length as needed
        self.is_monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None

        # Operation context setup
        self.operation_context = generate_operation_context(
            origin=Origin.SERVICE, layer=Layer.INFRASTRUCTURE, target=Target.MONITORING
        )
        self.operation_action = SystemOperationAction(
            type=SystemOperationType.METRIC_REPORT, details={"type": "resource"}
        )

    async def start_monitoring(self) -> None:
        """Start the resource monitoring loop."""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())

    async def stop_monitoring(self) -> None:
        """Stop the resource monitoring loop."""
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
            self.monitor_task = None

    async def _monitor_loop(self) -> None:
        """Internal monitoring loop."""
        while self.is_monitoring:
            try:
                await self._measure_resource_usage()
                await asyncio.sleep(self.config.measurement.interval)
            except asyncio.CancelledError:
                break
            except Exception:
                print("Error in resource monitoring:")
                print(traceback.format_exc())
                await asyncio.sleep(self.config.measurement.interval)

    def _cleanup_old_entries(self) -> None:
        """Remove entries older than max_age_seconds (default: 1 hour)."""
        if not self.measurement_history:
            return

        cutoff_time = datetime.now(tz=timezone.utc) - timedelta(
            seconds=self.config.retention
        )

        # Remove old entries from the left
        while (
            self.measurement_history
            and self.measurement_history[0].measured_at < cutoff_time
        ):
            self.measurement_history.popleft()

    async def _measure_resource_usage(self) -> SingleDataResponse[Measurement, None]:
        """Collect current resource usage and store in history."""
        operation_id = uuid4()
        executed_at = datetime.now(tz=timezone.utc)

        # Raw CPU usage since last call
        raw_cpu = self.process.cpu_percent(interval=None)

        # Update moving window for smoothing
        self.cpu_window.append(raw_cpu)
        smooth_cpu = sum(self.cpu_window) / len(self.cpu_window)

        # Memory usage in MB
        raw_memory = self.process.memory_info().rss / (1024 * 1024)

        completed_at = datetime.now(tz=timezone.utc)

        cpu_usage = CPUUsage.calculate_new(
            raw=raw_cpu, smooth=smooth_cpu, config=self.config.usage.cpu
        )
        memory_usage = MemoryUsage.calculate_new(
            raw=raw_memory, config=self.config.usage.memory
        )
        usage = Usage(cpu=cpu_usage, memory=memory_usage)
        measurement = Measurement(measured_at=completed_at, usage=usage)

        # Store in history with timestamp
        self.measurement_history.append(measurement)

        # Clean up old entries (older than max retention period)
        self._cleanup_old_entries()

        response = SingleDataResponse[Measurement, None](
            data=measurement, metadata=None, other=None
        )

        SuccessfulSystemOperation[None, SingleDataResponse[Measurement, None]](
            service_context=self.service_context,
            id=operation_id,
            context=self.operation_context,
            timestamp=OperationTimestamp(
                executed_at=executed_at,
                completed_at=completed_at,
                duration=(completed_at - executed_at).total_seconds(),
            ),
            summary=f"Successfully calculated resource usage - CPU | Raw: {raw_cpu:.2f}% | Smooth: {smooth_cpu:.2f}% - Memory: {raw_memory:.2f}MB",
            request_context=None,
            authentication=None,
            action=self.operation_action,
            response=response,
        ).log(self.logger, Level.INFO)

        return response

    def get_last_measurement(self) -> Optional[Measurement]:
        """Get the most recent resource usage data."""
        if not self.measurement_history:
            return None
        return self.measurement_history[-1]

    def get_measurement_history(self, seconds: int = 60) -> List[Measurement]:
        """
        Get resource usage data from the last X seconds.

        Args:
            seconds: Number of seconds to look back

        Returns:
            List of dicts with 'timestamp' and 'resource_usage' keys
        """
        if not self.measurement_history:
            return []

        cutoff_time = datetime.now(tz=timezone.utc) - timedelta(seconds=seconds)

        return [
            entry
            for entry in self.measurement_history
            if entry.measured_at >= cutoff_time
        ]

    def get_average_usage(self, interval: int = 60) -> Optional[AverageOrPeakUsage]:
        """
        Calculate average resource usage over the last X seconds.

        Args:
            interval: Number of seconds to look back

        Returns:
            Measurement with averaged values, or None if no data
        """
        history = self.get_measurement_history(interval)
        if not history:
            return None

        # Calculate averages
        total_raw_cpu = sum(entry.usage.cpu.raw for entry in history)
        total_smooth_cpu = sum(entry.usage.cpu.smooth for entry in history)
        total_memory = sum(entry.usage.memory.raw for entry in history)
        count = len(history)

        avg_cpu = CPUUsage.calculate_new(
            raw=total_raw_cpu / count,
            smooth=total_smooth_cpu / count,
            config=self.config.usage.cpu,
        )

        avg_memory = MemoryUsage.calculate_new(
            raw=total_memory / count, config=self.config.usage.memory
        )

        return AverageOrPeakUsage(cpu=avg_cpu, memory=avg_memory, interval=interval)

    def get_peak_usage(self, interval: int = 60) -> Optional[AverageOrPeakUsage]:
        """
        Get peak resource usage over the last X seconds.

        Args:
            seconds: Number of seconds to look back

        Returns:
            Measurement with peak values, or None if no data
        """
        history = self.get_measurement_history(interval)
        if not history:
            return None

        # Find peaks
        peak_raw_cpu = max(entry.usage.cpu.raw for entry in history)
        peak_smooth_cpu = max(entry.usage.cpu.smooth for entry in history)
        peak_raw_memory = max(entry.usage.memory.raw for entry in history)

        peak_cpu = CPUUsage.calculate_new(
            raw=peak_raw_cpu, smooth=peak_smooth_cpu, config=self.config.usage.cpu
        )

        peak_memory = MemoryUsage.calculate_new(
            raw=peak_raw_memory, config=self.config.usage.memory
        )

        return AverageOrPeakUsage(cpu=peak_cpu, memory=peak_memory, interval=interval)

    async def get_instant_usage(self) -> Measurement:
        """
        Get an instant resource usage reading without affecting the monitoring loop.
        This doesn't store the result in history.
        """
        raw_cpu = self.process.cpu_percent(interval=None)
        raw_memory = self.process.memory_info().rss / (1024 * 1024)

        # For instant reading, use the current smooth CPU from the window
        # or raw CPU if no history exists
        smooth_cpu = (
            sum(self.cpu_window) / len(self.cpu_window) if self.cpu_window else raw_cpu
        )

        measured_at = datetime.now(tz=timezone.utc)

        cpu_usage = CPUUsage.calculate_new(
            raw=raw_cpu, smooth=smooth_cpu, config=self.config.usage.cpu
        )
        memory_usage = MemoryUsage.calculate_new(
            raw=raw_memory, config=self.config.usage.memory
        )

        usage = Usage(cpu=cpu_usage, memory=memory_usage)

        return Measurement(measured_at=measured_at, usage=usage)

    def clear_history(self) -> None:
        """Clear all stored resource usage history."""
        self.measurement_history.clear()

    def get_history_count(self) -> int:
        """Get the number of entries in history."""
        return len(self.measurement_history)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_monitoring()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_monitoring()
