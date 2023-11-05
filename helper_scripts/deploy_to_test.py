import json
import os
import re
import shutil
import subprocess
import requests
from datetime import datetime
from typing import Optional
import fnmatch

from dotenv import load_dotenv


class Deployer:
    def __init__(self, log_dir: Optional[str] = "bin/log", log_name: Optional[str] = "deployment-log"):
        self.log_dir = log_dir
        self.log_name = log_name
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file_path = os.path.join(self.log_dir, f"{self.log_name}_{self.timestamp}.json")
        self.log_data = {"timestamp": self.timestamp, "logs": []}
        self.root_dir = self.get_git_root()
        self.clean_build_and_cache_directories(root_directory=self.root_dir)

    @staticmethod
    def get_git_root():
        root_directory = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        os.chdir(root_directory)
        return root_directory

    @staticmethod
    def clean_build_and_cache_directories(root_directory: str):
        directories_to_clean = [
            "build",
            "dist",
            "__pycache__",
            ".pytest_cache",
            "*.egg-info",  # Add .egg-info as a directory to clean
        ]
        files_to_clean = ["*.tar.gz", "*.whl"]

        for dirpath, dirnames, filenames in os.walk(root_directory, topdown=False):
            for dirname in dirnames:
                if dirname in directories_to_clean:
                    full_path = os.path.join(dirpath, dirname)
                    try:
                        shutil.rmtree(full_path)
                        print(f"Removed directory: {full_path}")
                    except Exception as e:
                        print(f"Error removing directory {full_path}. Reason: {str(e)}")

            for filename in filenames:
                for pattern in files_to_clean:
                    if fnmatch.fnmatch(filename, pattern):
                        full_path = os.path.join(dirpath, filename)
                        try:
                            os.remove(full_path)
                            print(f"Removed file: {full_path}")
                        except Exception as e:
                            print(f"Error removing file {full_path}. Reason: {str(e)}")

    def create_log_directory(self):
        os.makedirs(self.log_dir, exist_ok=True)
        return self.log_dir

    def mask_sensitive_info(self, string):
        """Mask sensitive information in a string."""
        if isinstance(string, str):
            token = self.configure()[1]
            return string.replace(token, '***')
        return string

    @staticmethod
    def execute_command(command):
        """Execute a shell command."""
        command_str = ' '.join(map(str, command))  # Convert the command parts to strings and join them
        return subprocess.run(command_str, text=True, capture_output=True, shell=True)

    def log_command(self, command, result):
        log_entry = {
            "command": self.mask_sensitive_info(' '.join(command)),
            "stdout": self.mask_sensitive_info(result.stdout),
            "stderr": self.mask_sensitive_info(result.stderr),
            "return_code": result.returncode
        }
        self.log_data["logs"].append(log_entry)

    def execute_and_log(self, command):
        """Execute a command and log its output."""
        masked_command = [str(part) for part in command]

        # Check if the command contains "--password" and remove it from the masked command
        if "--password" in masked_command:
            password_index = masked_command.index("--password") + 1
            masked_command[password_index] = "***"

        print(f"Executing: {' '.join(masked_command)}")
        result = self.execute_command(command)
        self.log_command(masked_command, result)

        return result.returncode

    def write_log_to_file(self):
        with open(self.log_file_path, "w") as log_file:
            log_file.write(json.dumps(self.log_data, indent=4))

    def handle_exit(self, message, code):
        self.write_log_to_file()
        print(message)
        exit(code)

    def install_dependencies(self):
        dependencies = ["python-dotenv", "wheel", "build", "twine"]
        for dep in dependencies:
            return_code = self.execute_and_log(["pip", "install", dep])
            if return_code != 0:
                self.handle_exit(
                    message=f"Failed to install {dep}. Check the log file for details.",
                    code=return_code
                )

    def build_project(self):
        return_code = self.execute_and_log(["python", "-m", "build", "--outdir", "package"])
        if return_code != 0:
            self.handle_exit(
                message="Failed to build the project. Check the log file for details.",
                code=return_code
            )

    def upload_to_pypi(self, repository_url: str, token: str):
        """Upload the built project to TestPyPI or PyPI based on the branch."""
        return_code = self.execute_and_log([
            "twine", "upload",
            "--repository-url", repository_url,  # Use the provided repository_url
            "--username", "__token__",
            "--password", token,
            "package/*"
        ])
        if return_code != 0:
            self.handle_exit(
                message="Failed to upload the package. Check the log file for details.",
                code=return_code
            )

    def configure(self):
        """Load and validate the environment variables and determine the repository_url and token."""
        load_dotenv()

        current_branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()

        if current_branch not in ["main", "develop", "master"]:
            repository_url = "https://test.pypi.org/legacy/"
            token_var = "TEST_PYPI_TOKEN"
        else:
            repository_url = "https://upload.pypi.org/legacy/"
            token_var = "PYPI_TOKEN"

        token = os.environ.get(token_var)

        if not token:
            self.handle_exit(message=f"Invalid or missing PyPI token: {token_var}.", code=1)

        return repository_url, token_var

    @staticmethod
    def update_package_version():
        # Determine the appropriate package name based on the branch
        current_branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
        if current_branch in ["main", "develop", "master"]:
            pypi_repository = "https://pypi.org/"
        else:
            pypi_repository = "https://test.pypi.org/"

        # Fetch the package name from setup.cfg
        package_name = None
        with open('setup.cfg', 'r') as cfg_file:
            config_data = cfg_file.read()
            match = re.search(r'name\s*=\s*(\S+)', config_data)
            if match:
                package_name = match.group(1)

        if not package_name:
            print("Failed to retrieve package name from setup.cfg.")
            return

        # Print current package name and version
        print(f"Current package name: {package_name}")

        # Fetch version information from PyPI
        response = requests.get(f'{pypi_repository}pypi/{package_name}/json')
        if response.status_code == 200:
            pypi_data = response.json()
            current_version = pypi_data['info']['version']
            print(f"Current version on {pypi_repository}: {current_version}")
        else:
            print(f"Failed to fetch version information from PyPI for {package_name}.")
            current_version = None

        if current_version:
            version_pattern = r'\d+\.\d+\.\d+'
            match = re.search(version_pattern, current_version)
            if match:
                current_version_parts = match.group(0).split('.')
                next_bugfix_version = int(current_version_parts[2]) + 1
                new_version = f"{current_version_parts[0]}.{current_version_parts[1]}.{next_bugfix_version}"

                # Check if the version in setup.cfg matches the current version
                if f'version = {current_version}' in config_data:
                    config_data = re.sub(f'version = {current_version}', f'version = {new_version}', config_data)
                    with open('setup.cfg', 'w') as cfg_file:
                        cfg_file.write(config_data)
                    print(f"Updated package version to {new_version} in setup.cfg.")
                else:
                    print(
                        f"Version in setup.cfg does not match the current version {current_version}. Skipping update.")
            else:
                print("Failed to parse the current version.")
        else:
            print("Version retrieval failed. Skipping version update.")

    def deploy(self):
        repository_url, token = self.configure()
        api_token = os.environ.get(token)
        self.install_dependencies()
        self.update_package_version()
        self.build_project()
        self.upload_to_pypi(repository_url=repository_url, token=api_token)
        self.write_log_to_file()
        print("Deployment completed successfully.")


if __name__ == "__main__":
    deployer = Deployer()
    deployer.deploy()
