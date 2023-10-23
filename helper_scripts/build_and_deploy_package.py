import os
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv


class Deployer:
    def __init__(self):
        self.log_dir = self.create_log_directory()
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file_path = os.path.join(self.log_dir, f"deployment_log_{self.timestamp}.json")
        self.log_data = {"timestamp": self.timestamp, "logs": []}

    def create_log_directory(self):
        log_dir = "bin/log"
        os.makedirs(log_dir, exist_ok=True)
        return log_dir

    def mask_sensitive_info(self, string, sensitive_info):
        return string.replace(sensitive_info, '***')

    def execute_command(self, command):
        return subprocess.run(command, text=True, capture_output=True)

    def log_command(self, command, result, sensitive_info):
        log_entry = {
            "command": self.mask_sensitive_info(' '.join(command), sensitive_info),
            "stdout": self.mask_sensitive_info(result.stdout, sensitive_info),
            "stderr": self.mask_sensitive_info(result.stderr, sensitive_info),
            "return_code": result.returncode
        }
        self.log_data["logs"].append(log_entry)

    def execute_and_log(self, command, sensitive_info):
        print(f"Executing: {' '.join(command)}")
        result = self.execute_command(command)
        self.log_command(command, result, sensitive_info)
        return result.returncode

    def write_log_to_file(self):
        with open(self.log_file_path, "w") as log_file:
            log_file.write(json.dumps(self.log_data, indent=4))

    def install_dependencies(self, token):
        dependencies = ["python-dotenv", "wheel", "build", "twine"]
        for dep in dependencies:
            return_code = self.execute_and_log(["pip", "install", dep], token)
            if return_code != 0:
                self.write_log_to_file()
                print(f"Failed to install {dep}. Check the log file for details.")
                exit(return_code)

    def build_project(self, token):
        return_code = self.execute_and_log(["python", "-m", "build", "--outdir", "package"], token)
        if return_code != 0:
            self.write_log_to_file()
            print("Failed to build the project. Check the log file for details.")
            exit(return_code)

    def upload_to_testpypi(self, token):
        return_code = self.execute_and_log([
            "twine", "upload",
            "--repository-url", "https://test.pypi.org/legacy/",
            "--username", "__token__",
            "--password", token,
            "package/*"
        ], token)

        if return_code != 0:
            self.write_log_to_file()
            print("Failed to upload the package to TestPyPI. Check the log file for details.")
            exit(return_code)
        print("Package uploaded successfully to TestPyPI.")

    def deploy(self, token):
        self.install_dependencies(token)
        self.build_project(token)
        self.upload_to_testpypi(token)
        self.write_log_to_file()


# Load and validate the environment variables
load_dotenv()
test_pypi_token = os.getenv("TEST_PYPI_TOKEN")

if test_pypi_token and test_pypi_token.startswith('pypi-'):
    deployer = Deployer()
    deployer.deploy(test_pypi_token)
else:
    print("Invalid TestPyPI token.")
    exit(1)
