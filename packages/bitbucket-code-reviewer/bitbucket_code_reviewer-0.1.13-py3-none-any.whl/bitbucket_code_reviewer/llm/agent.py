"""LangChain agent for code review with tool-calling capabilities."""

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from ..core.models import PullRequestDiff, ReviewConfig
from ..prompts import get_system_prompt
from .tools import create_code_review_tools


class CodeReviewAgent:
    """LangChain agent for performing code reviews."""

    def __init__(
        self,
        llm: BaseLanguageModel,
        config: ReviewConfig,
        pr_diff: PullRequestDiff,
    ):
        """Initialize the code review agent.

        Args:
            llm: Configured language model
            config: Review configuration
            pr_diff: Pull request diff information
        """
        self.llm = llm
        self.config = config
        self.pr_diff = pr_diff

        # Create tools with working directory
        self.tools = create_code_review_tools(config.working_directory)

        # Create the agent
        self.agent_executor = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        """Create the LangChain agent with tools.

        Returns:
            Configured agent executor
        """
        # Get the system prompt
        system_prompt = get_system_prompt(language=self.config.language)

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", self._create_initial_message()),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Create the agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )

        # Create the agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=self.config.max_tool_iterations,
            handle_parsing_errors=True,
        )

    def _create_initial_message(self) -> str:
        """Create the initial human message with PR context.

        Returns:
            Initial message for the agent
        """
        pr_info = self.pr_diff.pull_request

        message_parts = [
            "Please review this pull request:",
            f"Title: {pr_info.title}",
            f"Author: {pr_info.author}",
            f"Source Branch: {pr_info.source_branch}",
            f"Target Branch: {pr_info.target_branch}",
            "",
            "Files changed:",
        ]

        for file_change in self.pr_diff.files[:10]:  # Limit to first 10 files
            status_emoji = {
                "added": "➕",
                "modified": "✏️",
                "removed": "➖",
                "renamed": "📝",
            }.get(file_change.status, "❓")

            message_parts.append(
                f"{status_emoji} {file_change.filename} "
                f"(+{file_change.additions}, -{file_change.deletions})"
            )

        if len(self.pr_diff.files) > 10:
            message_parts.append(f"... and {len(self.pr_diff.files) - 10} more files")

        message_parts.extend(
            [
                "",
                "Please analyze the code changes and provide a comprehensive review. "
                "Use the available tools to examine files and directories as needed. "
                "Focus on code quality, security, performance, and maintainability.",
            ]
        )

        return "\n".join(message_parts)

    async def run_review(self) -> str:
        """Run the code review process.

        Returns:
            Review result as JSON string
        """
        try:
            result = await self.agent_executor.ainvoke({})
            return result["output"]
        except Exception as e:
            return f'{{"error": "Review failed: {str(e)}"}}'

    def run_review_sync(self) -> str:
        """Run the code review process synchronously.

        Returns:
            Review result as JSON string
        """
        try:
            result = self.agent_executor.invoke({})
            return result["output"]
        except Exception as e:
            return f'{{"error": "Review failed: {str(e)}"}}'


def create_code_review_agent(
    llm: BaseLanguageModel,
    config: ReviewConfig,
    pr_diff: PullRequestDiff,
) -> CodeReviewAgent:
    """Create a code review agent instance.

    Args:
        llm: Configured language model
        config: Review configuration
        pr_diff: Pull request diff information

    Returns:
        Configured code review agent
    """
    return CodeReviewAgent(llm, config, pr_diff)
