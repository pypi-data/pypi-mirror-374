"""Format code review results for Bitbucket PR comments."""

from typing import Any

from ..core.models import CodeReviewResult, Severity


def format_review_output(review_result: CodeReviewResult) -> list[dict[str, Any]]:
    """Format a code review result into Bitbucket PR comments.

    Args:
        review_result: The structured code review result

    Returns:
        List of comment dictionaries ready for Bitbucket API
    """
    comments = []

    # Add summary comment
    summary_comment = _format_summary_comment(review_result)
    comments.append(summary_comment)

    # Add individual change comments
    for change in review_result.changes:
        change_comment = _format_change_comment(change)
        comments.append(change_comment)

    # Add positives comment if there are positives
    if review_result.positives:
        positives_comment = _format_positives_comment(review_result.positives)
        comments.append(positives_comment)

    # Add recommendations comment if there are recommendations
    if review_result.recommendations:
        recommendations_comment = _format_recommendations_comment(
            review_result.recommendations
        )
        comments.append(recommendations_comment)

    return comments


def _format_summary_comment(review_result: CodeReviewResult) -> dict[str, Any]:
    """Format the summary as a general PR comment.

    Args:
        review_result: The review result

    Returns:
        Comment dictionary for Bitbucket API
    """
    severity_summary = _get_severity_summary(review_result)

    content_lines = [
        "## 🤖 Automated Code Review Summary",
        "",
        review_result.summary,
        "",
        "### 📊 Issue Summary",
        severity_summary,
        "",
        "_This review was generated automatically using AI-powered code analysis._",
    ]

    return {
        "content": "\n".join(content_lines),
        "file_path": None,
        "line": None,
    }


def _format_change_comment(change) -> dict[str, Any]:
    """Format a code change as an inline comment.

    Args:
        change: The code change object

    Returns:
        Comment dictionary for Bitbucket API
    """
    severity_emoji = {
        Severity.CRITICAL: "🚨",
        Severity.MAJOR: "⚠️",
        Severity.MINOR: "ℹ️",
        Severity.INFO: "💡",
    }.get(change.severity, "❓")

    content_lines = [
        f"## {severity_emoji} {change.title}",
        "",
        f"**Severity:** {change.severity.value.title()}",
        f"**Category:** {change.category.value.title()}",
        "",
        "### Issue Description",
        change.description,
        "",
        "### Suggested Solution",
        change.suggestion,
        "",
        "### Code Context",
        "```",
        change.code_snippet.strip(),
        "```",
        "",
        "### Improved Code",
        "```",
        change.suggested_code.strip(),
        "```",
        "",
        "### Rationale",
        change.rationale,
    ]

    return {
        "content": "\n".join(content_lines),
        "file_path": change.file_path,
        "line": change.start_line,
    }


def _format_positives_comment(positives) -> dict[str, Any]:
    """Format positive aspects as a general comment.

    Args:
        positives: List of positive aspects

    Returns:
        Comment dictionary for Bitbucket API
    """
    content_lines = [
        "## ✅ Positive Aspects",
        "",
        "Great work on these areas:",
        "",
    ]

    for positive in positives:
        content_lines.append(f"✓ {positive.description}")

    return {
        "content": "\n".join(content_lines),
        "file_path": None,
        "line": None,
    }


def _format_recommendations_comment(recommendations) -> dict[str, Any]:
    """Format recommendations as a general comment.

    Args:
        recommendations: List of recommendations

    Returns:
        Comment dictionary for Bitbucket API
    """
    content_lines = [
        "## 🚀 Future Recommendations",
        "",
        "Consider these suggestions for future improvements:",
        "",
    ]

    for recommendation in recommendations:
        content_lines.append(f"• {recommendation}")

    return {
        "content": "\n".join(content_lines),
        "file_path": None,
        "line": None,
    }


def _get_severity_summary(review_result: CodeReviewResult) -> str:
    """Generate a summary of issues by severity.

    Args:
        review_result: The review result

    Returns:
        Formatted severity summary string
    """
    counts = review_result.severity_counts

    summary_parts = []
    if counts[Severity.CRITICAL] > 0:
        summary_parts.append(f"🚨 **{counts[Severity.CRITICAL]}** critical")
    if counts[Severity.MAJOR] > 0:
        summary_parts.append(f"⚠️ **{counts[Severity.MAJOR]}** major")
    if counts[Severity.MINOR] > 0:
        summary_parts.append(f"ℹ️ **{counts[Severity.MINOR]}** minor")
    if counts[Severity.INFO] > 0:
        summary_parts.append(f"💡 **{counts[Severity.INFO]}** informational")

    if not summary_parts:
        return "✅ **No issues found** - Great job!"

    return " | ".join(summary_parts)


def print_review_summary(review_result: CodeReviewResult) -> None:
    """Print a human-readable summary of the review result.

    Args:
        review_result: The review result to print
    """
    print("\n" + "=" * 60)
    print("🤖 CODE REVIEW SUMMARY")
    print("=" * 60)

    print(f"\n📝 Summary: {review_result.summary}")

    print("\n📊 Issue Breakdown:")
    counts = review_result.severity_counts
    for severity in [Severity.CRITICAL, Severity.MAJOR, Severity.MINOR, Severity.INFO]:
        if counts[severity] > 0:
            print(f"  {severity.value.title()}: {counts[severity]}")

    if review_result.changes:
        print("\n🔧 Key Changes:")
        for i, change in enumerate(review_result.changes[:5], 1):  # Show first 5
            print(f"  {i}. {change.title} ({change.file_path}:{change.start_line})")

        if len(review_result.changes) > 5:
            print(f"  ... and {len(review_result.changes) - 5} more")

    if review_result.positives:
        print("\n✅ Positives:")
        for positive in review_result.positives:
            print(f"  ✓ {positive.description}")

    if review_result.recommendations:
        print("\n🚀 Recommendations:")
        for rec in review_result.recommendations:
            print(f"  • {rec}")

    print("\n" + "=" * 60)
