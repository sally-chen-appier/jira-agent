from datetime import datetime
import logging
import os
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_toolset import StdioConnectionParams, StdioServerParameters

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
# Read-only tools only - filtering out all write operations
# Write operations that are excluded:
# - createConfluencePage, updateConfluencePage
# - createConfluenceFooterComment, createConfluenceInlineComment
# - editJiraIssue, createJiraIssue
# - transitionJiraIssue, addCommentToJiraIssue
READ_ONLY_TOOLS = [
    'atlassianUserInfo',
    'getAccessibleAtlassianResources',
    # 'getConfluenceSpaces', 
    # (this tool is not available in the Google ADK)
    'getConfluencePage',
    'getPagesInConfluenceSpace',
    'getConfluencePageFooterComments',
    'getConfluencePageInlineComments',
    'getConfluencePageDescendants',
    'searchConfluenceUsingCql',
    'getJiraIssue',
    'getTransitionsForJiraIssue',
    'lookupJiraAccountId',
    'searchJiraIssuesUsingJql',
    'getJiraIssueRemoteIssueLinks',
    'getVisibleJiraProjects',
    'getJiraProjectIssueTypesMetadata',
    'getJiraIssueTypeMetaWithFields',
    'search',
    'fetch',
]

try: 
    jira_mcp_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=[
                        '-y',  # Auto-confirm npx install
                        'mcp-remote',
                        'https://mcp.atlassian.com/v1/sse',
                        "--jira-url=https://appier.atlassian.net/",
                        "--jira-token={JIRA_TOKEN}"
                    ],
                ),
                timeout=300 
            ),
            tool_filter=READ_ONLY_TOOLS  # Only allow read-only operations
        )

except Exception as e:
    jira_mcp_toolset = None
    logging.error("Failed to initialize Jira MCP tools: %s", e)