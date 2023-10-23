import requests
import logging
from typing import Optional, Dict


class GitHubClient:
    """
    A base client for interacting with the GitHub API.

    Args:
    - token (str): The GitHub personal access token.
    - owner (str): The GitHub repository owner/organization.
    - repo (str): The name of the GitHub repository.

    Usage:
    > github_client = GitHubClient("your_token", "owner", "repo")
    """

    def __init__(self, token: str, owner: str, repo: str):
        if not all([token, owner, repo]):
            raise ValueError("GitHub token, owner, and repository name are required.")

        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _make_request(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Dict:
        """
        Helper method to make requests to the GitHub API.
        Raises an exception for HTTP errors and returns the JSON response.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Request to {url} failed: {e}")
            raise Exception(f"Request failed: {str(e)}")