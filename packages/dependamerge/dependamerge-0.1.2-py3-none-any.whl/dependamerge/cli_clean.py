# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2025 The Linux Foundation

from typing import Any, List, Optional, Tuple

import requests
import typer
import urllib3.exceptions

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .github_client import GitHubClient
from .models import ComparisonResult, PullRequestInfo
from .pr_comparator import PRComparator

app = typer.Typer(
    help="Automatically merge pull requests created by automation tools across GitHub organizations"
)
console = Console(markup=False)


@app.command()
def merge(
    pr_url: str = typer.Argument(..., help="GitHub pull request URL"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what changes will apply without making them"
    ),
    similarity_threshold: float = typer.Option(
        0.8, "--threshold", help="Similarity threshold for matching PRs (0.0-1.0)"
    ),
    merge_method: str = typer.Option(
        "merge", "--merge-method", help="Merge method: merge, squash, or rebase"
    ),
    token: Optional[str] = typer.Option(
        None, "--token", help="GitHub token (or set GITHUB_TOKEN env var)"
    ),
    fix: bool = typer.Option(
        False, "--fix", help="Automatically fix out-of-date branches before merging"
    ),
):
    """
    Merge automation pull requests across an organization.

    This command will:
    1. Analyze the provided PR
    2. Find similar PRs in the organization
    3. Approve and merge matching PRs
    """
    try:
        # Initialize clients
        github_client = GitHubClient(token)
        comparator = PRComparator(similarity_threshold)

        console.print(f"Analyzing PR: {pr_url}")

        # Parse PR URL and get info
        owner, repo_name, pr_number = github_client.parse_pr_url(pr_url)

        try:
            source_pr: PullRequestInfo = github_client.get_pull_request_info(
                owner, repo_name, pr_number
            )
        except (
            urllib3.exceptions.NameResolutionError,
            urllib3.exceptions.MaxRetryError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
        ) as e:
            console.print(
                "Network Error: Failed to connect to GitHub API while fetching source PR."
            )
            console.print(f"Details: {e}")
            console.print("Please check your internet connection and try again.")
            raise typer.Exit(1) from e

        # Display source PR info
        _display_pr_info(source_pr, "Source PR", github_client)

        # Check if source PR is from automation
        if not github_client.is_automation_author(source_pr.author):
            console.print("Error: Source PR is not from a recognized automation tool")
            raise typer.Exit(1)

        # Get organization repositories
        console.print(f"\nChecking organization: {owner}")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching repositories...", total=None)
            try:
                repositories: List[Any] = (
                    github_client.get_organization_repositories(owner)
                )
            except (
                urllib3.exceptions.NameResolutionError,
                urllib3.exceptions.MaxRetryError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.RequestException,
            ) as e:
                console.print(
                    "Network Error: Failed to connect to GitHub API while fetching organization repositories."
                )
                console.print(f"Details: {e}")
                console.print("Please check your internet connection and try again.")
                raise typer.Exit(1) from e
            progress.update(task, description=f"Found {len(repositories)} repositories")

        # Find similar PRs
        similar_prs: List[Tuple[PullRequestInfo, ComparisonResult]] = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing PRs...", total=len(repositories))

            for repo in repositories:
                if repo.full_name == source_pr.repository_full_name:
                    progress.advance(task)
                    continue

                open_prs = github_client.get_open_pull_requests(repo)

                for pr in open_prs:
                    if not github_client.is_automation_author(pr.user.login):
                        continue

                    try:
                        target_pr = github_client.get_pull_request_info(
                            repo.owner.login, repo.name, pr.number
                        )

                        comparison = comparator.compare_pull_requests(
                            source_pr, target_pr
                        )

                        if comparison.is_similar:
                            similar_prs.append((target_pr, comparison))

                    except (
                        urllib3.exceptions.NameResolutionError,
                        urllib3.exceptions.MaxRetryError,
                        requests.exceptions.ConnectionError,
                        requests.exceptions.Timeout,
                        requests.exceptions.RequestException,
                    ) as e:
                        console.print(
                            "Network Error: Failed to connect to GitHub API while analyzing PRs."
                        )
                        console.print(f"Details: {e}")
                        console.print(
                            "Please check your internet connection and try again."
                        )
                        raise typer.Exit(1) from e
                    except Exception as e:
                        console.print(
                            f"Warning: Failed to analyze PR {pr.number} in {repo.full_name}: {e}",
                            style="yellow",
                        )

                progress.advance(task)

        # Display results
        if not similar_prs:
            console.print("\nNo similar PRs found in the organization")
        else:
            console.print(f"\nFound {len(similar_prs)} similar PR(s)")

            # Display similar PRs table
            table = Table(title="Similar Pull Requests")
            table.add_column("Repository", style="cyan")
            table.add_column("PR #", style="magenta")
            table.add_column("Title", style="green")
            table.add_column("Confidence", style="yellow")
            table.add_column("Status", style="blue")

            for pr_info, comparison in similar_prs:
                # Strip organization name from repository full name
                repo_name = pr_info.repository_full_name.split("/")[-1]

                # Get detailed status information
                status = github_client.get_pr_status_details(pr_info)

                table.add_row(
                    repo_name,
                    str(pr_info.number),
                    pr_info.title[:50] + "..."
                    if len(pr_info.title) > 50
                    else pr_info.title,
                    f"{comparison.confidence_score:.2f}",
                    status,
                )

            console.print(table)

        # Merge PRs
        if dry_run:
            console.print("\nDry run mode - no changes will be made")
            return

        success_count = 0
        # Merge similar PRs if any were found
        for pr_info, _comparison in similar_prs:
            if _merge_single_pr(pr_info, github_client, merge_method, fix, console):
                success_count += 1

        # Always merge source PR (whether similar PRs were found or not)
        console.print(f"\nMerging source PR {source_pr.number}")
        source_pr_merged = _merge_single_pr(
            source_pr, github_client, merge_method, fix, console
        )
        if source_pr_merged:
            success_count += 1

        total_prs = len(similar_prs) + 1  # similar PRs + source PR
        console.print(
            f"\nSuccessfully merged {success_count}/{total_prs} PRs (including source PR)"
        )

    except Exception as e:
        console.print(f"Error: {e}")
        raise typer.Exit(1) from e


def _display_pr_info(pr: PullRequestInfo, title: str, github_client: GitHubClient):
    """Display pull request information in a formatted table."""
    table = Table(title=title)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    # Get proper status instead of raw mergeable field
    status = github_client.get_pr_status_details(pr)

    table.add_row("Repository", pr.repository_full_name)
    table.add_row("PR Number", str(pr.number))
    table.add_row("Title", pr.title)
    table.add_row("Author", pr.author)
    table.add_row("State", pr.state)
    table.add_row("Status", status)
    table.add_row("Files Changed", str(len(pr.files_changed)))
    table.add_row("URL", pr.html_url)

    console.print(table)


def _merge_single_pr(
    pr_info: PullRequestInfo,
    github_client: GitHubClient,
    merge_method: str,
    fix: bool,
    console: Console,
) -> bool:
    """
    Merge a single pull request.

    Returns True if successfully merged, False otherwise.
    """
    repo_owner, repo_name = pr_info.repository_full_name.split("/")

    # Check if PR needs fixing
    if not pr_info.mergeable and fix:
        status = github_client.get_pr_status_details(pr_info)
        if "Rebase required" in status:
            console.print(
                f"Fixing out-of-date PR {pr_info.number} in {pr_info.repository_full_name}"
            )
            if github_client.fix_out_of_date_pr(repo_owner, repo_name, pr_info.number):
                console.print(f"Successfully updated PR {pr_info.number} ✅")
                # Refresh PR info after fix
                try:
                    pr_info = github_client.get_pull_request_info(
                        repo_owner, repo_name, pr_info.number
                    )
                except Exception as e:
                    console.print(
                        f"Warning: Failed to refresh PR info: {e}",
                        style="yellow",
                    )
            else:
                console.print(f"Failed to update PR {pr_info.number} ❌")
                return False

    if not pr_info.mergeable:
        status = github_client.get_pr_status_details(pr_info)
        console.print(
            f"Skipping unmergeable PR {pr_info.number} in {pr_info.repository_full_name} ({status})",
            style="yellow",
        )
        return False

    # Approve PR
    console.print(f"Approving PR {pr_info.number} in {pr_info.repository_full_name}")
    if github_client.approve_pull_request(repo_owner, repo_name, pr_info.number):
        # Merge PR
        console.print(f"Merging PR {pr_info.number} in {pr_info.repository_full_name}")
        if github_client.merge_pull_request(
            repo_owner, repo_name, pr_info.number, merge_method
        ):
            console.print(f"Successfully merged PR {pr_info.number} ✅")
            return True
        else:
            console.print(f"Failed to merge PR {pr_info.number} ❌")
    else:
        console.print(f"Failed to approve PR {pr_info.number} ❌")

    return False


if __name__ == "__main__":
    app()
