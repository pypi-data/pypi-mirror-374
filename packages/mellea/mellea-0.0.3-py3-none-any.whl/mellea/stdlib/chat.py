"""Chat primitives."""

from collections.abc import Mapping
from typing import Any, Literal

from mellea.helpers.fancy_logger import FancyLogger
from mellea.stdlib.base import (
    CBlock,
    Component,
    Context,
    ModelOutputThunk,
    ModelToolCall,
    TemplateRepresentation,
)


class Message(Component):
    """A single Message in a Chat history."""

    Role = Literal["system", "user", "assistant", "tool"]

    def __init__(self, role: "Message.Role", content: str):
        """Initializer for Chat messages.

        Args:
            role (str): The role that this message came from (e.g., user, assistant).
            content (str): The content of the message.
        """
        self.role = role
        self.content = content

    def parts(self):
        """Returns all of the constituent parts of an Instruction."""
        raise Exception(
            "Disallowing use of `parts` until we figure out exactly what it's supposed to be for"
        )

    def format_for_llm(self) -> TemplateRepresentation:
        """Formats the content for a Language Model.

        Returns:
            The formatted output suitable for language models.
        """
        return TemplateRepresentation(
            obj=self,
            args={"role": self.role, "content": self.content},
            template_order=["*", "Message"],
        )

    def __str__(self):
        """Pretty representation of messages, because they are a special case."""
        return f'mellea.Message(role="{self.role}", content="{self.content}")'


class ToolMessage(Message):
    """Adds the name field for function name."""

    def __init__(
        self,
        role: Message.Role,
        content: str,
        tool_output: Any,
        name: str,
        args: Mapping[str, Any],
        tool: ModelToolCall,
    ):
        """Initializer for Chat messages.

        Args:
            role: the role of this message. Most backends/models use something like tool.
            content: The content of the message; should be a stringified version of the tool_output.
            name: The name of the tool/function.
            args: The args required to call the function.
            tool_output: the output of the tool/function call.
            tool: the ModelToolCall representation.
        """
        super().__init__(role, content)
        self.name = name
        self.arguments = args
        self._tool_output = tool_output
        self._tool = tool

    def format_for_llm(self) -> TemplateRepresentation:
        """The same representation as Message with a name field added to args."""
        message_repr = super().format_for_llm()
        args = message_repr.args
        args["name"] = self.name

        return TemplateRepresentation(
            obj=self, args=args, template_order=["*", "Message"]
        )

    def __str__(self):
        """Pretty representation of messages, because they are a special case."""
        return f'mellea.Message(role="{self.role}", content="{self.content}", name="{self.name}")'


def as_chat_history(ctx: Context) -> list[Message]:
    """Returns a list of Messages corresponding to a Context."""

    def _to_msg(c: CBlock | Component | ModelOutputThunk) -> Message | None:
        match c:
            case Message():
                return c
            case ModelOutputThunk():
                match c.parsed_repr:
                    case Message():
                        return c.parsed_repr
                    case _:
                        return None
            case _:
                return None

    all_ctx_events = ctx.full_event_log()
    if all_ctx_events is None:
        raise Exception("Trying to cast a non-linear history into a chat history.")
    else:
        history = [_to_msg(c) for c in all_ctx_events]
        assert None not in history, "Could not render this context as a chat history."
        return history  # type: ignore
