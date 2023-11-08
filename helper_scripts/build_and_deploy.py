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
    def __init__(self, log_dir: Optional[str] = "bin/log", log_name: Optional[str] = "deploy-log"):
        self.log_dir = log_dir
        self.log_name = log_name
        self.current_commit_sha = self.get_current_commit_sha()
        self.previous_commit_sha = self.get_previous_commit_sha()
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
        subprocess.run("pwd")
        directories_to_clean = [
            "build",
            "dist",
            "__pycache__",
            ".pytest_cache",
            "ghmate.egg-info",
            "package"
        ]
        files_to_clean = ["*.tar.gz", "*.whl"]

        print("\n [INFO] Starting Cleanup Tasks")

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
        print("======= Cleanup Complete =========\n")

    @staticmethod
    def execute_command(command):
        """Execute a shell command."""
        command_str = ' '.join(map(str, command))  # Convert the command parts to strings and join them
        return subprocess.run(command_str, text=True, capture_output=True, shell=True)

    @staticmethod
    def parse_stdout(stdout):
        # Split the stdout into lines
        lines = stdout.strip().split('\n')
        json_objects = []

        for line in lines:
            # Split each line into key and value using the colon-space delimiter
            parts = line.split(': ')
            if len(parts) == 2:
                key, value = parts
                # Create a JSON object from the key-value pair and append it to the list
                json_objects.append({key: value})

        return json_objects

    @staticmethod
    def get_current_git_branch():
        return subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()

    @staticmethod
    def determine_pypi_repository(current_branch):
        return "https://pypi.org/" if current_branch in ["main", "develop", "master"] else "https://test.pypi.org/"

    @staticmethod
    def get_package_name_from_config(config_file_path):
        with open(config_file_path, 'r') as cfg_file:
            config_data = cfg_file.read()
            match = re.search(r'name\s*=\s*(\S+)', config_data)
            return match.group(1) if match else None

    @staticmethod
    def fetch_version_info_from_pypi(package_name, pypi_repository):
        response = requests.get(f'{pypi_repository}pypi/{package_name}/json')
        if response.status_code == 200:
            pypi_data = response.json()
            return pypi_data['info']['version']
        return None

    @staticmethod
    def parse_current_version(current_version):
        match = re.search(r'\d+\.\d+\.\d+', current_version)
        if match:
            current_version_parts = match.group(0).split('.')
            next_bugfix_version = int(current_version_parts[2]) + 1
            return f"{current_version_parts[0]}.{current_version_parts[1]}.{next_bugfix_version}"
        return None

    @staticmethod
    def update_version_in_config(config_file_path, current_version, new_version):
        with open(config_file_path, 'r') as cfg_file:
            config_data = cfg_file.read()
        if f'version = {current_version}' in config_data:
            config_data = re.sub(
                f'version = {current_version}',
                f'version = {new_version}',
                config_data
            )
            with open(config_file_path, 'w') as cfg_file:
                cfg_file.write(config_data)
            return True
        return False

    @staticmethod
    def get_current_commit_sha():
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()

    @staticmethod
    def get_previous_commit_sha():
        return subprocess.check_output(['git', 'rev-parse', 'HEAD~1'], text=True).strip()

    def check_directory_changes(self, directory):
        diff_command = f"git diff --name-only {self.previous_commit_sha} {self.current_commit_sha} -- {directory}/*"
        result = subprocess.run(diff_command, shell=True, capture_output=True, text=True)
        return result.stdout.strip() != ""

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

    def create_log_directory(self):
        os.makedirs(self.log_dir, exist_ok=True)
        return self.log_dir

    def mask_sensitive_info(self, string):
        """Mask sensitive information in a string."""
        if isinstance(string, str):
            token = self.configure()[1]
            return string.replace(token, '***')
        return string

    def log_command(self, command, result):
        log_entry = {
            "command": self.mask_sensitive_info(' '.join(command)),
            "stdout": self.parse_stdout(result.stdout),
            "stderr": self.mask_sensitive_info(result.stderr),
            "return_code": result.returncode
        }
        self.log_data["logs"].append(log_entry)

    def write_log_to_file(self):
        with open(self.log_file_path, "w") as log_file:
            log_file.write(json.dumps(self.log_data, indent=4))

    def handle_exit(self, message, code):
        self.write_log_to_file()
        print(message)
        exit(code)

    def install_dependencies(self):
        print("\n[INFO]: INSTALLING DEPENDENCIES")
        dependencies = ["python-dotenv", "wheel", "build", "twine"]
        for dep in dependencies:
            return_code = self.execute_and_log(["pip", "install", dep])
            if return_code != 0:
                self.handle_exit(
                    message=f"Failed to install {dep}. Check the log file for details.",
                    code=return_code
                )

    def build_project(self):
        print("\n[INFO]: BUILDING PROJECT")
        return_code = ""

        try:
            return_code = self.execute_and_log(["python", "-m", "build", "--outdir", "package"])
        except Exception as error:
            print(f"Error: {error}")
            if return_code != 0:
                self.handle_exit(
                    message="Failed to build the project. Check the log file for details.",
                    code=return_code
                )

    def upload_to_pypi(self, repository_url: str, token: str):
        print("\n[INFO]: STARTING UPLOAD TO PYPI")

        """Upload the built project to TestPyPI or PyPI based on the branch."""
        command = [
            "twine", "upload",
            "--repository-url", repository_url,
            "--username", "__token__",
            "--password", token,
            "package/*",
            "--verbose"
        ]

        # Execute the command and capture the return code
        return_code = self.execute_and_log(command)

        if return_code != 0:
            # Upload failed, handle the error
            error_message = f"Failed to upload the package. Return code: {return_code}"
            self.handle_exit(
                message=error_message,
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

    def update_package_version(self):
        print("\n[INFO]: CHECKING PYPI FOR PACKAGE INFORMATION")

        current_branch = self.get_current_git_branch()
        pypi_repository = self.determine_pypi_repository(current_branch=current_branch)

        package_name = self.get_package_name_from_config(config_file_path='setup.cfg')
        if not package_name:
            print("Failed to retrieve package name from setup.cfg.")
            return

        print(f"Current package name: {package_name}")

        current_version = self.fetch_version_info_from_pypi(package_name=package_name, pypi_repository=pypi_repository)
        if not current_version:
            print(f"Failed to fetch version information from PyPI for {package_name}. No package found")
            return

        print(f"Current version on {pypi_repository} for {package_name}: {current_version}")

        new_version = self.parse_current_version(current_version)
        if not new_version:
            print("Failed to parse the current version.")
            return

        print("Comparing PyPI package version to version in config file")
        if self.update_version_in_config(
                config_file_path='setup.cfg',
                current_version=current_version,
                new_version=new_version):
            print(f"Updated package version to {new_version} in setup.cfg.")
        else:
            print(f"Version in setup config does NOT match the current version {current_version}. Skipping update.")

    def deploy(self):
        print("========== Starting Build and Deployment to PYPI ==========")
        repository_url, token = self.configure()
        api_token = os.environ.get(token)
        self.install_dependencies()
        self.update_package_version()
        self.build_project()
        self.upload_to_pypi(repository_url=repository_url, token=api_token)
        self.write_log_to_file()
        print("========== Deployment to PYPI Complete ==========")


if __name__ == "__main__":
    deployer = Deployer()
    if deployer.check_directory_changes('ghmate'):
        deployer.deploy()
    else:
        print("No changes in 'ghmate' directory, skipping build and deploy.")
