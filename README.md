# ghmate

A comprehensive Python package for interacting with the GitHub API. This package simplifies GitHub API calls by providing a set of high-level commands encapsulated in easy-to-use classes.

### Prerequisites

### Prerequisites

- Python 3.8 or higher (specify other supported versions if applicable)
- `pip` for installing packages
- A GitHub account and [Personal Access Token](https://github.com/settings/tokens) (required for making authenticated API requests)

## Installation

To install `ghmate`, ensure you have Python 3.8 or higher and pip installed. Run the following command:
```bash
pip install ghmate
```

## Setup

Before using `ghmate`, set up your environment with your GitHub personal access token:
```bash
export GITHUB_TOKEN='your_personal_access_token'
```

(Optional) Use a .env file with python-dotenv to load environment variables.
Create a `.env` file in your project directory and add your GitHub Personal Access Token, repository owner, and repository name.

```plaintext
GITHUB_TOKEN=your_personal_access_token_here
OWNER=repository_owner_here
REPO=repository_name_here
```

Load environment variables using `python-dotenv`.

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables
token = os.getenv('GITHUB_TOKEN')
owner = os.getenv('OWNER')
repo = os.getenv('REPO')
```

## Usage
Initialize the GitHubClient with your repository owner, name, and token. 
Replace owner_name, repository_name, and your_token with your actual GitHub information.


To start using `ghmate`, initialize the `GitHubClient`:

```python
from ghmate.github_client import GitHubClient

github_client = GitHubClient(
    owner="owner_name",
    repo="repository_name",
    token="your_token"
)
```
Use CoreCommands for basic operations and ActionsCommands for GitHub Actions-related tasks. 
Here are some examples:

### Core Commands
`CoreCommands` provides essential GitHub operations:

```python
from ghmate.core_commands import CoreCommands

core_commands = CoreCommands(
    token="your_token",
    owner="owner_name",
    repo="repository_name"
)

# Authenticate and get user information
user_info = core_commands.auth()

# Browse topics
topics = core_commands.browse()

# Create an issue
issue = core_commands.issue(action='create', title='Issue Title', body='Issue description')

```

### Actions Commands
`ActionsCommands` focuses on GitHub Actions-related tasks:

```python
from ghmate.actions_commands import ActionsCommands

actions_commands = ActionsCommands(owner="owner_name", repo="repository_name", token="your_token")

# List artifacts
artifacts = actions_commands.list_artifacts()

# Cache management
cache_list = actions_commands.cache(action='list')
cache_restore = actions_commands.cache(action='restore', key='cache_key')

```

Handle exceptions that may occur during API calls.

## Tests

### Unit Test

Run tests to ensure the package is working as expected.

```bash
python -m unittest discover -s tests/unit
# OR
python3 -m unittest discover -s tests/unit

```
Mock external API calls when writing unit tests. 
Integration tests will make actual API calls, so ensure you have the correct setup.
When writing unit tests, use the `unittest.mock` module to mock external API calls. 

For example:

```python
from unittest import TestCase
from unittest.mock import patch
from ghmate.actions_commands import ActionsCommands

class TestActionsCommandsUnit(TestCase):
    @patch.object(ActionsCommands, '_make_request')
    def test_list_artifacts(self, mock_request):
        # Your test code here
        pass

```

### Integration Tests
For integration tests, ensure your .env file contains the necessary environment variables and run:

```bash
python -m unittest discover -s tests/integration
```

## Examples
Examples
The `examples` directory contains a sample project setup and usage examples.

```plaintext
example/
├── .env                 # Storing environment variables
├── using_dotenv.py     # Example script utilizing the ghmate package
└── requirements.txt     # Required packages
```
## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) to get started.

## License

`ghmate` is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

