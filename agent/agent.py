from google.adk.agents import Agent

from .prompt import agent_instruction
from .tools.tools import get_current_date, search_tool, jira_mcp_toolset


# Build tools list, filtering out empty/None values
tools = [get_current_date, search_tool]
if jira_mcp_toolset is not None:  # Only add if not None
    tools.append(jira_mcp_toolset)

root_agent = Agent(
    model="gemini-2.5-flash",
    name="agent",
    instruction=agent_instruction,
    tools=tools,
)
