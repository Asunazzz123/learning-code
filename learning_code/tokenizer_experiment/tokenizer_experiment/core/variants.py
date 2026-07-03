from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PretokenizerMode(str, Enum):
    REGEX_COMPILED = "regex_compiled"
    NONE = "none"


class ParallelMode(str, Enum):
    SERIAL = "serial"
    PARALLEL = "parallel"


@dataclass(frozen=True)
class ExperimentVariant:
    name: str
    pretokenizer: PretokenizerMode
    parallel: ParallelMode

    @property
    def uses_pretokenizer(self) -> bool:
        return self.pretokenizer is PretokenizerMode.REGEX_COMPILED

    @property
    def uses_parallel(self) -> bool:
        return self.parallel is ParallelMode.PARALLEL


ALL_VARIANTS: tuple[ExperimentVariant, ...] = (
    ExperimentVariant(
        name="with_pretokenizer_serial",
        pretokenizer=PretokenizerMode.REGEX_COMPILED,
        parallel=ParallelMode.SERIAL,
    ),
    ExperimentVariant(
        name="without_pretokenizer_serial",
        pretokenizer=PretokenizerMode.NONE,
        parallel=ParallelMode.SERIAL,
    ),
    ExperimentVariant(
        name="with_pretokenizer_parallel",
        pretokenizer=PretokenizerMode.REGEX_COMPILED,
        parallel=ParallelMode.PARALLEL,
    ),
    ExperimentVariant(
        name="without_pretokenizer_parallel",
        pretokenizer=PretokenizerMode.NONE,
        parallel=ParallelMode.PARALLEL,
    ),
)


def variant_names() -> list[str]:
    return [variant.name for variant in ALL_VARIANTS]
