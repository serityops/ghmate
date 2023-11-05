from typing import Optional, Any

from ghmate.github_client import GitHubClient


class ActionsCommands(GitHubClient):
    """
    Handles GitHub Actions commands.

    Inherits from GitHubClient for shared attributes and methods.
    """

    LIST_ACTION = "list"
    RESTORE_ACTION = "restore"

    def __init__(self, owner: str, repo: str, token: Optional[str] = None):
        super().__init__(owner=owner, repo=repo, token=token)

    def cache(self, action: str, *args: Optional[Any]) -> Any:
        if action == ActionsCommands.LIST_ACTION:
            endpoint = "actions/cache"
            return self._make_request(method="GET", endpoint=endpoint)

        elif action == ActionsCommands.RESTORE_ACTION:
            key = args[0]
            endpoint = f"actions/cache/{key}/restore"
            return self._make_request(method="POST", endpoint=endpoint)

        else:
            raise ValueError(f"Unsupported action: {action}")

    def run(self, action: str) -> Any:
        if action == ActionsCommands.LIST_ACTION:
            endpoint = "actions/runs"
            return self._make_request(method="GET", endpoint=endpoint)
        else:
            raise ValueError(f"Unsupported action: {action}")

    # Get the artifacts for the repository
    def get_artifacts(self):
        endpoint = "actions/artifacts"
        payload = {}

        try:
            response = self._make_request(method="GET", endpoint=endpoint, payload=payload)
            artifacts = response.json().get('artifacts', [])
            if not artifacts:
                no_artifacts = f"No artifacts found for repository {self.repo}"
                return no_artifacts
            else:
                return artifacts
        except Exception as error:
            print(f"Failed to get artifacts for repository {self.repo}: {error}")
            raise

    # List out all artifacts with name, uploaded date, file type and id
    def list_artifacts(self) -> list:
        artifacts = self.get_artifacts()
        artifact_list = []

        for artifact in artifacts:
            artifact_info = {
                "Artifact name": artifact.get('name'),
                "Created date": artifact.get('created_at'),
                "Location": artifact.get('archive_download_url'),
                "Artifact ID": artifact.get('id')
            }
            artifact_list.append(artifact_info)

        print("ARTIFACT INFO:")
        for artifact_info in artifact_list:
            for key, value in artifact_info.items():
                print(f"{key}: {value}")
            print("=============================")

        return artifact_list

    def get_all_workflow_runs(self):
        runs = []
        url = "actions/runs"
        while url:
            response = self._make_request(method="GET", endpoint=url)
            runs.extend(response.json().get('workflow_runs', []))
            url = response.json().get('next_page', None)
        return runs

    def delete_workflow_run(self, run_id):
        try:
            endpoint = f"actions/runs/{run_id}"
            response = self._make_request(method="DELETE", endpoint=endpoint)

            if response.status_code == 204:
                return f"Deleted successfully: run ID {run_id}"
            else:
                return f"Failed to delete run ID {run_id}. HTTP Status Code: {response.status_code}"
        except Exception as error:
            # Log the unexpected error and return a descriptive error message
            print(f"Unexpected Error deleting workflow run {run_id}: {error}")
            return f"Unexpected Error: {error}"

    def delete_all_workflow_runs(self):
        all_runs = self.get_all_workflow_runs()
        print(f"Total workflow runs found: {len(all_runs)}")

        for run in all_runs:
            self.delete_workflow_run(run['id'])

        print("\nAll workflow runs deletion process completed.")
