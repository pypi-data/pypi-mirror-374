"""Performance tests for set_chat_history functionality."""

import time

from lite_agent.agent import Agent
from lite_agent.runner import Runner
from lite_agent.types import (
    AssistantTextContent,
    AssistantToolCall,
    AssistantToolCallResult,
    NewAssistantMessage,
    NewUserMessage,
    UserTextContent,
)


def test_set_chat_history_performance():
    """Test performance with large chat history."""
    print("Running performance test for set_chat_history...")

    # Create agents
    parent = Agent(
        model="gpt-4.1",
        name="ParentAgent",
        instructions="You are a helpful parent agent.",
    )

    child1 = Agent(
        model="gpt-4.1",
        name="Child1Agent",
        instructions="You are child agent 1.",
    )

    child2 = Agent(
        model="gpt-4.1",
        name="Child2Agent",
        instructions="You are child agent 2.",
    )

    parent.add_handoff(child1)
    parent.add_handoff(child2)

    runner = Runner(parent)

    # Create a large chat history with many transfers
    large_chat_history = []
    num_cycles = 100  # 100 cycles of transfers

    print(f"Creating chat history with {num_cycles} transfer cycles...")

    for i in range(num_cycles):
        cycle_messages = [
            NewUserMessage(content=[UserTextContent(text=f"Request {i}")]),
            NewAssistantMessage(content=[AssistantTextContent(text=f"Response {i}")]),
            NewAssistantMessage(
                content=[
                    AssistantToolCall(
                        call_id=f"call_{i}_1",
                        name="transfer_to_agent",
                        arguments='{"name": "Child1Agent"}',
                    ),
                    AssistantToolCallResult(
                        call_id=f"call_{i}_1",
                        output="Transferring to agent: Child1Agent",
                    ),
                ],
            ),
            NewAssistantMessage(content=[AssistantTextContent(text=f"Child1 response {i}")]),
            NewAssistantMessage(
                content=[
                    AssistantToolCall(
                        call_id=f"call_{i}_2",
                        name="transfer_to_parent",
                        arguments="{}",
                    ),
                    AssistantToolCallResult(
                        call_id=f"call_{i}_2",
                        output="Transferring back to parent",
                    ),
                ],
            ),
            NewAssistantMessage(
                content=[
                    AssistantToolCall(
                        call_id=f"call_{i}_3",
                        name="transfer_to_agent",
                        arguments='{"name": "Child2Agent"}',
                    ),
                    AssistantToolCallResult(
                        call_id=f"call_{i}_3",
                        output="Transferring to agent: Child2Agent",
                    ),
                ],
            ),
            NewAssistantMessage(content=[AssistantTextContent(text=f"Child2 response {i}")]),
            NewAssistantMessage(
                content=[
                    AssistantToolCall(
                        call_id=f"call_{i}_4",
                        name="transfer_to_parent",
                        arguments="{}",
                    ),
                    AssistantToolCallResult(
                        call_id=f"call_{i}_4",
                        output="Transferring back to parent",
                    ),
                ],
            ),
        ]
        large_chat_history.extend(cycle_messages)

    total_messages = len(large_chat_history)
    print(f"Total messages: {total_messages}")

    # Measure performance
    start_time = time.time()
    runner.set_chat_history(large_chat_history, root_agent=parent)
    end_time = time.time()

    processing_time = end_time - start_time
    messages_per_second = total_messages / processing_time

    print(f"Processing time: {processing_time:.4f} seconds")
    print(f"Messages per second: {messages_per_second:.2f}")
    print(f"Final agent: {runner.agent.name}")
    print(f"Final message count: {len(runner.messages)}")

    # Verify correctness - messages are now preserved in original format
    # Each cycle: 8 NewMessages (user + 7 assistant messages with tool calls and responses)
    expected_messages = num_cycles * 8  # 8 NewMessage objects per cycle
    assert len(runner.messages) == expected_messages
    assert runner.agent.name == "ParentAgent"  # Should end at parent after all transfers

    # Performance expectations (these are reasonable thresholds)
    assert processing_time < 5.0, f"Processing took too long: {processing_time:.4f}s"
    assert messages_per_second > 100, f"Too slow: {messages_per_second:.2f} messages/second"

    print("✅ Performance test passed!")


if __name__ == "__main__":
    test_set_chat_history_performance()
