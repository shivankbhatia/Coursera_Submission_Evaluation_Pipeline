from agents.tool_schema import AgentTool

from tools.coursera_tool import verify_coursera_certificate
from tools.linkedin_tool import get_linkedin_observations
from utils.context_project_match import llm_project_context_match


VERIFY_COURSERA_TOOL = AgentTool(
    name="verify_coursera_certificate",
    description="Validates Coursera certificate and extracts project name",
    func=verify_coursera_certificate
)


LINKEDIN_OBSERVATION_TOOL = AgentTool(
    name="get_linkedin_observations",
    description="Extracts LinkedIn visibility, student identity, project match and post description",
    func=get_linkedin_observations
)


CONTEXT_MATCH_TOOL = AgentTool(
    name="llm_project_context_match",
    description="Uses LLM to check if LinkedIn post context matches project",
    func=llm_project_context_match
)


TOOL_REGISTRY = {
    VERIFY_COURSERA_TOOL.name: VERIFY_COURSERA_TOOL,
    LINKEDIN_OBSERVATION_TOOL.name: LINKEDIN_OBSERVATION_TOOL,
    CONTEXT_MATCH_TOOL.name: CONTEXT_MATCH_TOOL
}
