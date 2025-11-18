from google.adk.agents import Agent

from .prompt import agent_instruction
from .tools.tools import get_current_date, search_tool, mcp_tools


# Build tools list, filtering out empty/None values
tools = [get_current_date, search_tool]
if mcp_tools is not None:  # Only add if not None
    tools.append(mcp_tools)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="jira_assistant",
    instruction=agent_instruction,
    tools=tools,
)
