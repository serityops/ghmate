from typing import Optional, Any

from ghmate.github_client import GitHubClient


class ActionsCommands(GitHubClient):
    """
    Handles GitHub Actions commands.

    Inherits from GitHubClient for shared attributes and methods.
    """

    def __init__(self, token: str, owner: str, repo: str):
        super().__init__(token, owner, repo)

    def cache(self, action: str, *args: Optional[Any]) -> Any:
        if action == 'list':
            endpoint = "actions/cache"
            return self._make_request("GET", endpoint)  # Using inherited _make_request method

        elif action == 'restore':
            key = args[0]
            endpoint = f"actions/cache/{key}/restore"
            return self._make_request("POST", endpoint)  # Using inherited _make_request method

        else:
            raise ValueError(f"Unsupported action: {action}")

    def run(self, action: str, *args: Optional[Any]) -> Any:
        if action == 'list':
            endpoint = "actions/runs"
            return self._make_request("GET", endpoint)  # Using inherited _make_request method

        else:
            raise ValueError(f"Unsupported action: {action}")
