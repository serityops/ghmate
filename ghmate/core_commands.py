from typing import Optional, Any
from ghmate.github_client import GitHubClient  # Import the GitHubClient class


class CoreCommands(GitHubClient):
    """
    Handles GitHub core commands.

    Inherits from GitHubClient for shared attributes and methods.
    """

    def __init__(self, token: str, owner: str, repo: str):
        super().__init__(token, owner, repo)

    def auth(self):
        url = "https://api.github.com/user"
        return self._make_request(method="GET", endpoint=url)

    def browse(self):
        url = f"{self.base_url}/topics"
        return self._make_request(method="GET", endpoint=url)

    def codespace(self):
        url = f"{self.base_url}/codespaces"
        return self._make_request(method="GET", endpoint=url)

    def gist(self):
        url = "https://api.github.com/gists"
        return self._make_request(method="GET", endpoint=url)

    def issue(self, action: str, *args: Optional[Any]) -> Any:
        if action == 'create':
            title, body = args
            url = f"{self.base_url}/issues"
            payload = {
                "title": title,
                "body": body,
            }
            return self._make_request(
                method="POST",
                endpoint=url,
                payload=payload
            )

        elif action == 'list':
            url = f"{self.base_url}/issues"
            return self._make_request(method="GET", endpoint=url)

    def org(self, action: str, *args: Optional[Any]) -> Any:
        if action == 'create':
            org_name = args[0]
            url = "https://api.github.com/orgs"
            payload = {
                "login": org_name,
            }
            return self._make_request(
                method="POST",
                endpoint=url,
                payload=payload
            )

        elif action == 'list':
            url = "https://api.github.com/organizations"
            return self._make_request(method="GET", endpoint=url)

    def pr(self, action: str, *args: Optional[Any]) -> Any:
        if action == 'checkout':
            pr_number = args[0]
            url = f"{self.base_url}/pulls/{pr_number}"
            return self._make_request(method="GET", endpoint=url)

        elif action == 'list':
            url = f"{self.base_url}/pulls"
            return self._make_request(method="GET", endpoint=url)

    def project(self, action: str, *args: Optional[Any]) -> Any:
        if action == 'create':
            project_name = args[0]
            url = f"{self.base_url}/projects"
            payload = {
                "name": project_name,
            }
            return self._make_request(
                method="POST",
                endpoint=url,
                payload=payload
            )

        elif action == 'list':
            url = f"{self.base_url}/projects"
            return self._make_request(method="GET", endpoint=url)

    def release(self, action: str, *args: Optional[Any]) -> Any:
        if action == 'create':
            tag_name, target_commitish = args
            url = f"{self.base_url}/releases"
            payload = {
                "tag_name": tag_name,
                "target_commitish": target_commitish,
            }
            return self._make_request(
                method="POST",
                endpoint=url,
                payload=payload
            )

        elif action == 'list':
            url = f"{self.base_url}/releases"
            return self._make_request(method="GET", endpoint=url)

    def get_repo_clone_url(self, repo_name: str) -> str:
        """
        Get the clone URL for a repository.
        Args:
        - repo_name (str): The name of the repository.
        Returns:
        - str: The clone URL for the repository.
        """
        return f"https://github.com/{self.owner}/{repo_name}.git"

    def create_repo(self, repo_name: str) -> dict:
        """
        Create a new repository.
        Args:
        - repo_name (str): The name of the repository to create.
        Returns:
        - dict: The response JSON containing repository information.
        """
        url = "https://api.github.com/user/repos"
        payload = {
            "name": repo_name,
        }
        return self._make_request(method="POST", endpoint=url, payload=payload)

    def set_secret(self, secret_name: str, secret_value: str):
        url = f"{self.base_url}/actions/secrets/{secret_name}"
        payload = {
            "encrypted_value": secret_value
        }
        return self._make_request(
            method="PUT",
            endpoint=url,
            payload=payload
        )

    def get_secret(self, secret_name: str):
        url = f"{self.base_url}/actions/secrets/{secret_name}"
        response = self._make_request(method="GET", endpoint=url)
        return response.get("value") if response else None

    def delete_secret(self, secret_name: str):
        url = f"{self.base_url}/actions/secrets/{secret_name}"
        self._make_request(method="DELETE", endpoint=url)
