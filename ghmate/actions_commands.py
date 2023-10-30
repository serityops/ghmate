import json
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
        if action == "list":
            endpoint = "actions/cache"
            return self._make_request(method="GET", endpoint=endpoint)

        elif action == "restore":
            key = args[0]
            endpoint = f"actions/cache/{key}/restore"
            return self._make_request(method="POST", endpoint=endpoint)

        else:
            raise ValueError(f"Unsupported action: {action}")

    def run(self, action: str, *args: Optional[Any]) -> Any:
        if action == "list":
            endpoint = "actions/runs"
            return self._make_request(method="GET", endpoint=endpoint)
        else:
            raise ValueError(f"Unsupported action: {action}")

    # Get the artifacts for the repository
    def get_artifacts(self):
        endpoint = "actions/artifacts"
        payload = {}

        # Using inherited _make_request method
        try:
            response = self._make_request(method="GET", endpoint=endpoint, payload=payload)
            artifacts = response.get('artifacts', [])
            if not artifacts:
                no_artifacts = f"No artifacts found for repository {self.repo}"
                return no_artifacts
            else:
                return artifacts
        except Exception as error:
            print(f"Failed to get artifacts for repository {self.repo}: {error}")
            raise

    # List out all artifacts with name, uploaded date, and file type
    def list_artifacts(self):
        artifacts = self.get_artifacts()
        for artifact in artifacts:
            print(f"Artifact name: {artifact['name']}")
            print(f"Created date: {artifact['created_at']}")
            print(f"Location: {artifact['archive_download_url']}")

    def get_all_workflow_runs(self):
        runs = []
        try:
            url = "/actions/runs"
            while url:
                response = self._make_request(method="GET", endpoint=url)
                runs.extend(response.get('workflow_runs', []))
                url = response.links.get('next', {}).get('url', None)
            return runs
        except Exception as error:
            print(f"Error retrieving workflow runs: {error}")
            return []

    def delete_workflow_run(self, run_id):
        try:
            url = f"{self.base_url}/actions/runs/{run_id}"
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            print(f"Successfully deleted run ID {run_id}")
        except requests.exceptions.HTTPError as err:
            print(f"Error deleting workflow run {run_id}: {err}")

    def delete_all_workflow_runs(self):
        all_runs = self.get_all_workflow_runs()
        print(f"Total workflow runs found: {len(all_runs)}")

        for run in all_runs:
            self.delete_workflow_run(run['id'])

        print("\nAll workflow runs deletion process completed.")
