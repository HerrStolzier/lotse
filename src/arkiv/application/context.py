"""Runtime context shared across UI and transport layers."""

from __future__ import annotations

from dataclasses import dataclass, field

from arkiv.core.config import ArkivConfig
from arkiv.core.engine import Engine


@dataclass
class AppContext:
    """Application runtime context with lazy Engine construction."""

    config: ArkivConfig
    _engine: Engine | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.config.ensure_dirs()

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = Engine(self.config)
        return self._engine
