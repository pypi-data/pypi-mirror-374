from __future__ import annotations
import logging
from typing import Sequence
from .step import Step
from .models import PipelineContext
from .enums import PipelineSignal

log = logging.getLogger(__name__)


class Pipeline:
    """Holds an ordered list of Step instances and runs them sequentially."""

    def __init__(
        self, steps: Sequence[Step], name: str = "pipeline", max_passes: int = 3
    ):
        self.steps = list(steps)
        self.name = name
        self.max_passes = max_passes

    def _once(self, ctx: PipelineContext) -> PipelineContext:
        log.info("▶️  %s pass", self.name)
        ctx.signal = PipelineSignal.CONTINUE

        for step in self.steps:
            ctx = step.run(ctx)
            if ctx.signal in (PipelineSignal.ABORT_PIPELINE, PipelineSignal.ABORT_PASS):
                break
        return ctx

    def run(self, ctx: PipelineContext) -> PipelineContext:
        pass_idx = 0
        while True:
            ctx = self._once(ctx)
            pass_idx += 1

            if ctx.signal is PipelineSignal.ABORT_PIPELINE:
                log.info("🛑  %s aborted after %d pass(es)", self.name, pass_idx)
                break

            if ctx.signal is PipelineSignal.ABORT_PASS:
                if pass_idx >= self.max_passes:
                    raise RuntimeError(
                        f"{self.name}: exceeded {self.max_passes} passes"
                    )
                log.info("🔄  Re-running %s (pass %d)", self.name, pass_idx + 1)
                continue

            log.info("✅  %s finished after %d pass(es)", self.name, pass_idx)
            break

        return ctx
