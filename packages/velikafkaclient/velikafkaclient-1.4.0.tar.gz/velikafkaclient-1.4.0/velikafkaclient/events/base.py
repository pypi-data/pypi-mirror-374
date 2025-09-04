from typing import Optional

from pydantic import BaseModel


class KafkaEvent(BaseModel):

    tracing_id: Optional[str]

    def to_str(self) -> str:
        pass
