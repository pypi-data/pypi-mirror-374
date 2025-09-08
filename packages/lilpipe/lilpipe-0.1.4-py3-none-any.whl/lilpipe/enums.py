from enum import Enum, auto


class PipelineSignal(Enum):
    CONTINUE = auto()  # default; you never set this
    ABORT_PASS = auto()  # stop only current pass
    ABORT_PIPELINE = auto()  # stop everything immediately
