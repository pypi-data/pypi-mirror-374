from __future__ import annotations

from pydantic import Field
from wexample_helpers.classes.extended_base_model import ExtendedBaseModel
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.enums.choice import ChoiceValue


class Choice(ExtendedBaseModel):
    title: str = Field(description="The title of the choice")
    value: str | int | ChoiceValue = Field(description="The value of the choice")
    line: PromptResponseLine = Field(description="The line that renders the choice")
