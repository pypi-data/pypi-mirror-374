from typing import Optional

from pydantic import BaseModel

from galileo_core.schemas.shared.scorers.scorer_configuration import ScorerConfiguration


class ProjectSettings(BaseModel):
    scorers_config: Optional[ScorerConfiguration] = None
