"""This module processes the message history for the agent, filtering messages based on the current context.
It uses the RunContext to access usage statistics and filters messages accordingly.

If message_history is set and not empty, a new system prompt is not generated — we assume the existing message history includes a system prompt.
"""

import logging

from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage


logger = logging.getLogger(__name__)


async def history_processor(
    total_tokens: int, messages: list[ModelMessage], selected_provider: str
) -> list[ModelMessage]:
    if not messages:
        return []

    from .config import summarize_config

    if (
        not summarize_config.ai_model
        or not summarize_config.token_limit
        or not selected_provider == summarize_config.model_provider
    ):
        logger.info(
            "Skipping history processing: model or token limit not set, or provider mismatch.",
            extra={"selected_provider": selected_provider, "config_model_provider": summarize_config.model_provider},
        )
        return messages

    token_limit = summarize_config.token_limit

    if total_tokens > token_limit:
        return await summarize_old_messages(messages)
    return messages


async def summarize_old_messages(messages: list[ModelMessage]) -> list[ModelMessage]:
    from .config import summarize_config

    summarize_agent = Agent(
        model=summarize_config.ai_model,
        instructions="Summarize the entire conversation so far in as few tokens as possible. Don't exceed a paragraph or 50 words",
    )

    # Only pass conversational messages to the summarizer
    summary = await summarize_agent.run(message_history=messages)

    # Extract summary content from the first TextPart of the first new message (type-correct)

    new_msgs = summary.new_messages()

    if new_msgs:
        return [new_msgs[0]]

    return []
