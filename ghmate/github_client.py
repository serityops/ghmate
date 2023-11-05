import logging
import os
from typing import Optional, Dict
import requests
from requests import Response


class GitHubClient:
    """
    A base client for interacting with the GitHub API.
    Provides methods for making requests to the GitHub API using a personal access token

    Args:
    - owner (str): The GitHub repository owner/organization.
    - repo (str): The name of the GitHub repository.
    - token (str, optional): The GitHub personal access token.
    If not provided, the token should be set as an environment variable named 'GITHUB_TOKEN'.

    Usage:
    github_client = GitHubClient(owner="owner", repo="repo", token="your_token")
    """

    def __init__(self, owner: str, repo: str, token: Optional[str] = None):
        if not all([owner, repo]):
            raise ValueError("GitHub owner and repository name are required.")

        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{self.owner}"

        # Retrieve the token from the parameter or environment variable
        self.token = token or os.environ.get('GITHUB_TOKEN')

        if not self.token:
            raise ValueError("GitHub token is required. Set it as a parameter or as an environment variable.")

        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _make_request(self, method: str, endpoint: str, payload: Optional[Dict] = None) -> Response:
        """
        Helper method to make requests to the GitHub API.
        Raises an exception for HTTP errors and returns the JSON response.
        """
        url = f"{self.base_url}/{self.repo}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, json=payload)
            return response
        except requests.exceptions.RequestException as error:
            logging.error(f"Request to {url} failed: {error}")
            raise Exception(f"Request failed: {str(error)}")
