import asyncio
import logging

from funcall import Context
from pydantic import BaseModel
from rich.logging import RichHandler

from lite_agent.agent import Agent
from lite_agent.context import HistoryContext
from lite_agent.runner import Runner


class WeatherContext(BaseModel):
    city: str


weather_context = Context(WeatherContext(city="New York"))


logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger("lite_agent")
logger.setLevel(logging.DEBUG)


async def get_current_city_temperature(context: Context[HistoryContext[WeatherContext]]) -> str:
    """Get the temperature for the current city specified in the context."""
    await asyncio.sleep(1)

    # Access user data
    if not context.value.data:
        msg = "City must be specified in the context."
        raise ValueError(msg)
    city = context.value.data.city

    # Access conversation history
    messages = context.value.history_messages
    previous_questions = sum(1 for msg in messages if hasattr(msg, "role") and getattr(msg, "role", None) == "user")

    return f"The temperature in {city} is 25°C. (This is your {previous_questions + 1} question today.)"


agent = Agent(
    model="gpt-4.1-nano",
    name="Weather Assistant",
    instructions="You are a weather assistant. Use the tools provided to answer questions about the weather.",
    tools=[get_current_city_temperature],
)


async def main():
    runner = Runner(agent)
    resp = runner.run(
        "What is the temperature in current city?",
        includes=["assistant_message", "usage", "function_call", "function_call_output"],
        record_to="tests/mocks/context/1.jsonl",
        context=weather_context,
    )
    async for chunk in resp:
        logger.info(chunk)
    print(runner.messages)


if __name__ == "__main__":
    asyncio.run(main())
