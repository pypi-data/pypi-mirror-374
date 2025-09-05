from typing import Optional

from ...utils.from_camel_case_base_model import FromCamelCaseBaseModel


class GenerateNextTurnRequest(FromCamelCaseBaseModel):
    session_id: str
    max_turns: Optional[int]


class GenerateNextTurnResponse(FromCamelCaseBaseModel):
    next_message: str
    finished: bool
    stopping_reason: Optional[str] = None
