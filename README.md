# ghmate

`ghmate` is a Python package for interacting with the GitHub API, providing a convenient way to access various GitHub features programmatically.

## Installation

### Prerequisites

- Python 3.8 or higher
- `pip` for installing packages
- A GitHub account and [Personal Access Token](https://github.com/settings/tokens) for authentication

### Install ghmate

Clone the repository and install the package using `pip`.

```bash
git clone https://github.com/yourusername/ghmate.git
cd ghmate
pip install .
```

Or install directly from GitHub.

```bash
pip install git+https://github.com/yourusername/ghmate.git
```

## Usage

### Environment Variables

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

### GitHub Client

Create an instance of the GitHub client.

```python
from ghmate.github_client import GitHubClient

github_client = GitHubClient(token, owner, repo)
```

### Actions Commands

Use the `ActionsCommands` class to interact with GitHub Actions.

```python
from ghmate.actions_commands import ActionsCommands

actions = ActionsCommands(github_client, token, owner, repo)
print(actions.cache('list'))  # Example method call
```

### Core Commands

Use the `CoreCommands` class for various core features.

```python
from ghmate.core_commands import CoreCommands

core = CoreCommands(token, owner, repo)
print(core.auth())  # Example method call
```

## Tests

Run tests to ensure the package is working as expected.

```bash
python -m unittest discover
```

## Examples

See the `example_project` directory for a sample project setup, usage examples, and tests.

```plaintext
example_project/
├── .env                 # Storing environment variables
├── example_usage.py     # Example script utilizing the ghmate package
├── tests/               # Directory containing test scripts
│   ├── __init__.py
│   ├── test_actions.py  # Test script for ActionsCommands
│   └── test_core.py     # Test script for CoreCommands
└── requirements.txt     # Required packages
```
## Contributing

Contributions are welcome! Please read our [contributing guidelines](CONTRIBUTING.md) to get started.

## License

`ghmate` is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

