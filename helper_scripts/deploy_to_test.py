import json
import os
import shutil
import subprocess
from datetime import datetime
from typing import Optional
import fnmatch

from dotenv import load_dotenv


class Deployer:
    def __init__(self, token: str, log_dir: Optional[str] = "bin/log", log_name: Optional[str] = "deployment-log"):
        self.log_dir = log_dir
        self.log_name = log_name
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file_path = os.path.join(self.log_dir, f"{self.log_name}_{self.timestamp}.json")
        self.log_data = {"timestamp": self.timestamp, "logs": []}
        self.token = token
        self.root_dir = self.get_git_root()
        self.clean_build_and_cache_directories(root_directory=self.root_dir)

    @staticmethod
    def get_git_root():
        return subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).strip().decode('utf-8')

    @staticmethod
    def clean_build_and_cache_directories(root_directory: str):
        """Recursively clean up build and pytest cache directories and files from the root directory."""
        directories_to_clean = [
            "build",
            "dist",
            "__pycache__",
            ".pytest_cache",
        ]
        files_to_clean = ["*.egg-info"]

        for dirpath, dirnames, filenames in os.walk(root_directory,
                                                    topdown=False):  # topdown=False so we can remove directories without any issue
            # Remove unwanted directories
            for dirname in dirnames:
                if dirname in directories_to_clean:
                    full_path = os.path.join(dirpath, dirname)
                    try:
                        shutil.rmtree(full_path)
                        print(f"Removed directory: {full_path}")
                    except Exception as e:
                        print(f"Error removing directory {full_path}. Reason: {str(e)}")

            # Remove unwanted files
            for filename in filenames:
                for pattern in files_to_clean:
                    if fnmatch.fnmatch(filename, pattern):  # Use fnmatch to match the pattern
                        full_path = os.path.join(dirpath, filename)
                        try:
                            os.remove(full_path)
                            print(f"Removed file: {full_path}")
                        except Exception as e:
                            print(f"Error removing file {full_path}. Reason: {str(e)}")

    def create_log_directory(self):
        """Create a directory to store logs."""
        os.makedirs(self.log_dir, exist_ok=True)
        return self.log_dir

    def mask_sensitive_info(self, string):
        """Mask sensitive information in a string."""
        return string.replace(self.token, '***')

    @staticmethod
    def execute_command(command):
        """Execute a shell command."""
        return subprocess.run(command, text=True, capture_output=True)

    def log_command(self, command, result):
        """Log the executed command and its result."""
        log_entry = {
            "command": self.mask_sensitive_info(' '.join(command)),
            "stdout": self.mask_sensitive_info(result.stdout),
            "stderr": self.mask_sensitive_info(result.stderr),
            "return_code": result.returncode
        }
        self.log_data["logs"].append(log_entry)

    def execute_and_log(self, command):
        """Execute a command and log its output."""
        masked_command = [self.mask_sensitive_info(part) for part in command]
        print(f"Executing: {' '.join(masked_command)}")
        result = self.execute_command(command)
        self.log_command(command, result)
        return result.returncode

    def write_log_to_file(self):
        """Write the accumulated log data to a file."""
        with open(self.log_file_path, "w") as log_file:
            log_file.write(json.dumps(self.log_data, indent=4))

    def handle_exit(self, message, code):
        """Handle exit scenarios by logging and exiting with a specific code."""
        self.write_log_to_file()
        print(message)
        exit(code)

    def install_dependencies(self):
        """Install the necessary dependencies."""
        dependencies = ["python-dotenv", "wheel", "build", "twine"]
        for dep in dependencies:
            return_code = self.execute_and_log(["pip", "install", dep])
            if return_code != 0:
                self.handle_exit(
                    message=f"Failed to install {dep}. Check the log file for details.",
                    code=return_code
                )

    def build_project(self):
        """Build the project."""
        return_code = self.execute_and_log(["python", "-m", "build", "--outdir", "package"])
        if return_code != 0:
            self.handle_exit(
                message="Failed to build the project. Check the log file for details.",
                code=return_code
            )

    def upload_to_testpypi(self):
        """Upload the built project to TestPyPI."""
        return_code = self.execute_and_log([
            "twine", "upload",
            "--repository-url", "https://test.pypi.org/legacy/",
            "--username", "__token__",
            "--password", self.token,
            "package/*"
        ])
        if return_code != 0:
            self.handle_exit(
                message="Failed to upload the package to TestPyPI. Check the log file for details.",
                code=return_code
            )

    def configure(self):
        """Load and validate the environment variables."""
        load_dotenv()
        test_pypi_token = self.token
        if not test_pypi_token or not test_pypi_token.startswith('pypi-'):
            self.handle_exit(message="Invalid TestPyPI token.", code=1)

    def deploy(self):
        """Main deployment process."""
        self.configure()
        self.install_dependencies()
        self.build_project()
        self.upload_to_testpypi()
        self.write_log_to_file()
        print("Deployment completed successfully.")


if __name__ == "__main__":
    deployer = Deployer()
    deployer.deploy()
