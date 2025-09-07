from universal_mcp.agents.autoagent import AutoAgent
from universal_mcp.agentr import AgentrRegistry


registry = AgentrRegistry()
agent = AutoAgent(
    name="autoagent",
    instructions="You are a helpful assistant that can use tools to help the user.",
    model="anthropic/claude-4-sonnet-20250514",
    registry=registry,
)
