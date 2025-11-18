from datetime import datetime
import os
import logging
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.langchain_tool import LangchainTool
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import StdioConnectionParams, StdioServerParameters
from langchain_community.tools import StackExchangeTool
from langchain_community.utilities import StackExchangeAPIWrapper
from toolbox_core import ToolboxSyncClient

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ----- Function tool -----
def get_current_date() -> dict:
    """
    Get the current date in the format YYYY-MM-DD
    """
    return {"current_date": datetime.now().strftime("%Y-%m-%d")}


# ----- Built-in Tool -----
search_agent = Agent(
    model="gemini-2.5-flash",
    name="search_agent",
    instruction="""
    You're a specialist in Google Search.
    """,
    tools=[google_search],
)
search_tool = AgentTool(search_agent)

# ----- Jira MCP Tool -----
try: 
    mcp_tools = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=[
                        '-y',  # Auto-confirm npx install
                        'mcp-remote',
                        'https://mcp.atlassian.com/v1/sse',
                        "--jira-url=https://appier.atlassian.net/",
                        "--jira-username=sally.cheng@appier.com",
                        "--jira-token=ATATT3xFfGF0gq5X4ZoVMD0Aj20w7KyCNB5lhCwwtFvXbfTzEXdohraoxl6TcvcL_WA6a_fE-fjChonXYyWutqhyIzc3Pow8vYbX18UKHMDnn6Gnt7sdUoPZHANUV-iDw_mDJLaREw51BzrT4SEjTp8W62OoCzFXu8O13LmL5O5HOanWxVkJSGs=5169ABD7"
                    ],
                ),
                timeout=300 
            ),
            # tool_filter=['getConfluenceSpaces', 'getConfluencePage']
        )

except Exception as e:
    mcp_tools = None
    logging.error("Failed to initialize Jira MCP tools: %s", e)


# ----- Example of a Third Party Tool (LangChainTool) -----
# stack_exchange_tool = StackExchangeTool(api_wrapper=StackExchangeAPIWrapper())
# Convert LangChain tool to ADK tool using LangchainTool
# langchain_tool = LangchainTool(stack_exchange_tool)

'''
# ----- Example of a Google Cloud Tool (MCP Toolbox for Databases) -----
TOOLBOX_URL = os.getenv("MCP_TOOLBOX_URL", "http://127.0.0.1:5000")

# Initialize Toolbox client and load tools
# If the toolbox server is not available (e.g., in CI), set to empty list
try:
    toolbox = ToolboxSyncClient(TOOLBOX_URL)
    toolbox_tools = toolbox.load_toolset("tickets_toolset")
except Exception:
    # Toolbox server not available, set to empty list
    toolbox_tools = []
'''

'''
# ----- Example of an MCP Tool (streamable-http) -----
# If GitHub token is not available (e.g., in CI), set to None
try:
    mcp_tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="https://api.githubcopilot.com/mcp/",
            headers={
                "Authorization": "Bearer " + os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN"),
            },
        ),
        # Read only tools
        tool_filter=[
            "search_repositories",
            "search_issues",
            "list_issues",
            "get_issue",
            "list_pull_requests",
            "get_pull_request",
        ],
    )
except Exception:
    # GitHub MCP server not available or token missing
    mcp_tools = None
'''

