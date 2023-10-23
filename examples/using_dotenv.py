import os

from dotenv import load_dotenv

from ghmate.actions_commands import ActionsCommands
from ghmate.core_commands import CoreCommands

# Load environment variables from .env file
load_dotenv()

# Get environment variables
token = os.getenv('GITHUB_TOKEN')
owner = os.getenv('OWNER')
repo = os.getenv('REPO')

# Create instances
actions = ActionsCommands(token=token, owner=owner, repo=repo)
core = CoreCommands(token=token, owner=owner, repo=repo)

# ActionsCommands
# Replace 'list' with the actual methods and parameters as per your implementation
print(actions.cache('list'))

# CoreCommands
# Replace 'auth' with the actual methods and parameters as per your implementation
print(core.auth())
