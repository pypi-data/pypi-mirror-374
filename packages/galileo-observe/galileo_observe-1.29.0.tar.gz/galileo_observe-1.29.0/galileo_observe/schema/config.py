# mypy: disable-error-code=syntax
# We need to ignore syntax errors until https://github.com/python/mypy/issues/17535 is resolved.
from typing import Any, Optional

from pydantic import UUID4

from galileo_core.schemas.base_config import GalileoConfig


class ObserveConfig(GalileoConfig):
    # Config file for this project.
    config_filename: str = "observe-config.json"

    # Observe specific configuration.
    project_id: Optional[UUID4] = None
    project_name: Optional[str] = None

    def reset(self) -> None:
        self.project_id = None
        self.project_name = None

        global _observe_config
        _observe_config = None

        super().reset()

    @classmethod
    def get(cls, **kwargs: Any) -> "ObserveConfig":
        global _observe_config
        _observe_config = cls._get(_observe_config, **kwargs)  # type: ignore[arg-type]
        return _observe_config


_observe_config: Optional[ObserveConfig] = None
