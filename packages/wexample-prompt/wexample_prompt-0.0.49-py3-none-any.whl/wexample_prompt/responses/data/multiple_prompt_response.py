from __future__ import annotations

from pydantic import Field
from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.enums.verbosity_level import VerbosityLevel
from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse


class MultiplePromptResponse(AbstractPromptResponse):
    """A response that groups multiple responses and renders them in sequence.

    This class allows grouping multiple prompt responses of different types into a
    single response object. When rendered or printed, each contained response is
    processed in order.

    Attributes:
        responses: List of prompt responses to be rendered together.
    """

    responses: list[AbstractPromptResponse] = Field(
        default_factory=list,
        description="List of prompt responses to be rendered together",
    )

    @classmethod
    def get_example_class(cls) -> type:
        from wexample_prompt.example.response.data.multiple_example import (
            MultipleExample,
        )

        return MultipleExample

    @classmethod
    def create_multiple(
        cls,
        responses: list[AbstractPromptResponse] | None = None,
        verbosity: VerbosityLevel | None = None,
    ) -> MultiplePromptResponse:
        """Create a new MultiplePromptResponse from a list of responses."""
        if responses is None:
            responses = []

        # Work on deep copies to avoid mutating shared instances across calls.
        cloned_responses: list[AbstractPromptResponse] = []
        for response in responses:
            cloned = response.model_copy(deep=True)
            cloned.verbosity = verbosity
            cloned_responses.append(cloned)

        return cls(
            responses=cloned_responses,
            verbosity=verbosity,
        )

    def render(self, context: PromptContext | None = None) -> str | None:
        """Render all contained responses in sequence.

        Returns:
            The concatenated rendered string, skipping None parts.
        """

        context = PromptContext.create_if_none(context=context)

        if not self._verbosity_context_allows_display(context=context):
            return None

        rendered_parts: list[str] = []
        for response in self.responses:
            part = response.render(context=context)
            if part is not None:
                rendered_parts.append(part)

        self._rendered_content = "\n".join(rendered_parts) if rendered_parts else None
        return self._rendered_content

    def append_response(
        self, response: AbstractPromptResponse
    ) -> MultiplePromptResponse:
        """Append a single response and return self for chaining."""
        self.responses.append(response)
        return self

    def extend_responses(
        self, responses: list[AbstractPromptResponse]
    ) -> MultiplePromptResponse:
        """Extend responses with a list and return self for chaining."""
        self.responses.extend(responses)
        return self
