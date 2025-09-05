"""Review orchestrator that coordinates the entire code review process."""

import json
from typing import Optional

from ..bitbucket.client import create_bitbucket_client
from ..core.config import LLMProvider, create_review_config
from ..core.models import CodeReviewResult, PullRequestDiff, ReviewConfig
from ..llm.agent import create_code_review_agent
from ..llm.providers import get_language_model
from .output_formatter import format_review_output


class CodeReviewOrchestrator:
    """Orchestrates the complete code review process."""

    def __init__(
        self,
        workspace: str,
        repo_slug: str,
        pr_id: int,
        config: ReviewConfig,
        bitbucket_token: Optional[str] = None,
        bitbucket_auth_username: Optional[str] = None,
    ):
        """Initialize the review orchestrator.

        Args:
            workspace: Bitbucket workspace
            repo_slug: Repository slug
            pr_id: Pull request ID
            config: Review configuration
            bitbucket_token: Optional Bitbucket API token
            bitbucket_auth_username: Optional Bitbucket username for App Password auth
        """
        self.workspace = workspace
        self.repo_slug = repo_slug
        self.pr_id = pr_id
        self.config = config

        # Initialize clients
        self.bitbucket_client = create_bitbucket_client(
            workspace, bitbucket_token, bitbucket_auth_username
        )
        self.llm = get_language_model(config)

    async def run_review(self) -> CodeReviewResult:
        """Run the complete code review process.

        Returns:
            Structured code review result
        """
        # Step 1: Get PR diff from Bitbucket
        pr_diff = await self._get_pr_diff()

        # Step 2: Create and run the LLM agent
        agent = create_code_review_agent(self.llm, self.config, pr_diff)
        review_json = await agent.run_review()

        # Step 3: Parse and format the review result
        review_result = self._parse_review_result(review_json)

        return review_result

    def run_review_sync(self) -> CodeReviewResult:
        """Run the complete code review process synchronously.

        Returns:
            Structured code review result
        """
        # Step 1: Get PR diff from Bitbucket
        pr_diff = self._get_pr_diff_sync()

        # Step 2: Create and run the LLM agent
        agent = create_code_review_agent(self.llm, self.config, pr_diff)
        review_json = agent.run_review_sync()

        # Step 3: Parse and format the review result
        review_result = self._parse_review_result(review_json)

        return review_result

    async def _get_pr_diff(self) -> PullRequestDiff:
        """Get the PR diff from Bitbucket API.

        Returns:
            Pull request diff information
        """
        # First validate the token works for basic operations
        print(f"🔍 Validating token for repository: {self.workspace}/{self.repo_slug}")
        if not self.bitbucket_client.validate_token():
            raise ValueError(
                f"Token validation failed for {self.workspace}/{self.repo_slug}. "
                "Please check:\n"
                "1. Token has 'Repositories: Read' permission\n"
                "2. Token is for the correct repository\n"
                "3. Token hasn't expired\n"
                "4. Repository name and workspace are correct"
            )

        print(f"📋 Fetching PR #{self.pr_id} information...")
        return self.bitbucket_client.get_pull_request_diff(self.repo_slug, self.pr_id)

    def _get_pr_diff_sync(self) -> PullRequestDiff:
        """Get the PR diff from Bitbucket API (synchronous).

        Returns:
            Pull request diff information
        """
        return self.bitbucket_client.get_pull_request_diff(self.repo_slug, self.pr_id)

    def _parse_review_result(self, review_json: str) -> CodeReviewResult:
        """Parse the LLM review output into a structured result.

        Args:
            review_json: JSON string from the LLM

        Returns:
            Structured code review result
        """
        try:
            review_data = json.loads(review_json)

            # Handle error responses
            if "error" in review_data:
                raise ValueError(review_data["error"])

            return CodeReviewResult(**review_data)

        except (json.JSONDecodeError, ValueError) as e:
            # Return a basic error result if parsing fails
            return CodeReviewResult(
                summary=f"Failed to parse review result: {str(e)}",
                changes=[],
                positives=[],
                recommendations=["Please check the LLM output manually"],
            )

    async def submit_review_comments(self, review_result: CodeReviewResult) -> None:
        """Submit review comments to Bitbucket.

        Args:
            review_result: The review result to submit
        """
        # Format the review for Bitbucket comments
        comments = format_review_output(review_result)

        for comment in comments:
            await self.bitbucket_client.add_pull_request_comment(
                repo_slug=self.repo_slug,
                pr_id=self.pr_id,
                content=comment["content"],
                file_path=comment.get("file_path"),
                line=comment.get("line"),
            )


def create_review_orchestrator(
    workspace: str,
    repo_slug: str,
    pr_id: int,
    llm_provider: Optional[LLMProvider] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    language: Optional[str] = None,
    bitbucket_token: Optional[str] = None,
    bitbucket_auth_username: Optional[str] = None,
    working_directory: Optional[str] = None,
) -> CodeReviewOrchestrator:
    """Create a review orchestrator with the specified configuration.

    Args:
        workspace: Bitbucket workspace
        repo_slug: Repository slug
        pr_id: Pull request ID
        llm_provider: LLM provider to use
        model_name: Model name to use
        temperature: Temperature for LLM
        language: Programming language for guidelines
        bitbucket_token: Bitbucket API token
        bitbucket_auth_username: Optional Bitbucket username for App Password auth
        working_directory: Working directory for repo operations

    Returns:
        Configured review orchestrator
    """
    config = create_review_config(
        llm_provider=llm_provider,
        model_name=model_name,
        temperature=temperature,
        language=language,
        working_directory=working_directory,
    )

    return CodeReviewOrchestrator(
        workspace=workspace,
        repo_slug=repo_slug,
        pr_id=pr_id,
        config=config,
        bitbucket_token=bitbucket_token,
        bitbucket_auth_username=bitbucket_auth_username,
    )
