from datetime import datetime
import logging
import os
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_toolset import StdioConnectionParams, StdioServerParameters
from google.adk.tools.retrieval.vertex_ai_rag_retrieval import VertexAiRagRetrieval
from vertexai.preview import rag
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

# Initialize Jira MCP toolset if JIRA_TOKEN is available
jira_token = os.getenv("JIRA_TOKEN")
jira_url = os.getenv("JIRA_URL", "https://appier.atlassian.net/")

if jira_token:
    try: 
        jira_mcp_toolset = MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command='npx',
                        args=[
                            '-y',  # Auto-confirm npx install
                            'mcp-remote',
                            'https://mcp.atlassian.com/v1/sse',
                            f"--jira-url={jira_url}",
                            f"--jira-token={jira_token}"
                        ],
                    ),
                    timeout=300 
                ),
                tool_filter=READ_ONLY_TOOLS  # Only allow read-only operations
            )
    except Exception as e:
        jira_mcp_toolset = None
        logging.error("Failed to initialize Jira MCP tools: %s", e)
else:
    jira_mcp_toolset = None
    logging.info("JIRA_TOKEN not set, Jira MCP tools will not be available")


# ----- Vertex AI RAG Retrieval Tool -----
rag_corpus = os.environ.get("RAG_CORPUS")

if rag_corpus:
    retrieve_product_documentation = VertexAiRagRetrieval(
        name='retrieve_product_documentation',
        description=(
            'Use this tool to retrieve documentation and reference materials from the RAG corpus. '
            'Use for questions about Appier products, documentation, processes, or general knowledge in the documentation corpus. '
            'DO NOT use for JIRA questions (tickets, issues, users, projects), Confluence questions, meta-questions about capabilities, or casual conversation. '
            'The RAG corpus contains static documentation, NOT live JIRA data or ticket information.'
        ),
        rag_resources=[
            rag.RagResource(
                # please fill in your own rag corpus
                # here is a sample rag corpus for testing purpose
                # e.g. projects/123/locations/asia-northeast1/ragCorpora/456
                rag_corpus=rag_corpus
            )
        ],
        similarity_top_k=10,
        vector_distance_threshold=0.6,
    )
else:
    retrieve_product_documentation = None

rag_agent = Agent(
    model="gemini-2.5-flash",
    name="rag_agent",
    instruction="""
    You're a specialist in Appier products. 
    Use this tool to retrieve documentation and reference materials from the RAG corpus.
    """,
    tools=[retrieve_product_documentation],
)
rag_tool = AgentTool(rag_agent)