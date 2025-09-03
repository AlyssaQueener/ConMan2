import argparse

from version_timeline.VersionTimeline import VersionTimeline

from command_line_interface.Add import add
from command_line_interface.Get import get
from command_line_interface.Commit import commit
from command_line_interface.Fetch import fetch
from command_line_interface.Pull import pull
from command_line_interface.Push import push
from command_line_interface.Remove import remove
from command_line_interface.Checkout import checkout
from command_line_interface.Reset import reset
from command_line_interface.Branch import branch
from command_line_interface.Log import log_timeline

parser = argparse.ArgumentParser(description='ConMan')
subparsers = parser.add_subparsers(dest='command', help='Available commands.')

# "add" command parser
add_parser = subparsers.add_parser('add', help='Adds a file to the database.')
add_parser.add_argument('-p', '--path', type=str, required=True, help='Path to the file to add.')
add_parser.add_argument('-t', '--timestamp', type=str, required=False, help='OPTIONAL: Manually create a timestamp as a custom graph identifier.')

# "get" command parser
get_parser = subparsers.add_parser('get', help='Parses a file back from the database.')
get_parser.add_argument('-p', '--path', type=str, required=True, help='Path the file is parsed to.')
get_parser.add_argument('-t', '--timestamp', type=str, required=True, help='Timestamp of the graph model to get.')

# "commit" command parser
commit_parser = subparsers.add_parser('commit', help='Creates diff and patch from two graphs.')
commit_parser.add_argument('-b', '--branch', type=str, required=True, help='Branch name to commit to.')
commit_parser.add_argument('-p', '--project_id', type=str, required=True, help='IfcProject GUID of the project to commit to.')
commit_parser.add_argument('-m', '--message', type=str, required=False, help='OPTIONAL: Commit message.')

# "checkout" command parser
checkout_parser = subparsers.add_parser('checkout', help='Checks out a specific timestamp version of the model.')
checkout_parser.add_argument('-p', '--project_id', type=str, required=True, help='Branch name to checkout from.')
checkout_parser.add_argument('-bi', '--branch_init', type=str, required=True, help='Branch name to checkout from.')
checkout_parser.add_argument('-bu', '--branch_updt', type=str, required=True, help='Branch name to checkout to.')
checkout_parser.add_argument('-tu', '--timestamp_updt', type=str, required=True, help='Timestamp of the updated graph model.')

# "branch" command parser
branch_parser = subparsers.add_parser('branch', help='Creates a new branch in the version timeline.')
branch_parser.add_argument('-n', '--name', type=str, required=True, help='Name of the new branch.')
branch_parser.add_argument('-p', '--project_id', type=str, required=True, help='IfcProject GUID of the project to create the branch in.')

# "remove" command parser
remove_parser = subparsers.add_parser('remove', help='Removes all nodes and relationships with the given timestamp from the database.')
remove_parser.add_argument('-t', '--timestamp', type=str, required=True, help='Timestamp of the graph model to remove.')

# "reset" command parser
reset_parser = subparsers.add_parser('reset', help='Removes all nodes and relationships from the database.')

# "fetch" command parser
fetch_parser = subparsers.add_parser('fetch', help='Fetches updates from the remote repository.')

# "pull" command parser
pull_parser = subparsers.add_parser('pull', help='Fetches updates from the remote repository. And merges them into the local repository.')

# "push" command parser
push_parser = subparsers.add_parser('push', help='Pushes local commits to the remote repository.')

# "log" command parser
log_parser = subparsers.add_parser('log', help='Displays the commit graph for a project.')
log_parser.add_argument('-p', '--project_id', type=str, required=True, help='IfcProject GUID of the project to display the commit graph for.')

args = parser.parse_args()

if args.command == 'add':
    path = args.path
    if args.timestamp is not None:
        timestamp = args.timestamp
    else:
        timestamp = VersionTimeline.create_timestamp()
    add(path, timestamp)
elif args.command == 'get':
    path = args.path
    timestamp = args.timestamp
    print(f"Parsing file to path: {path}")
    get(path, timestamp)
elif args.command == 'commit':
    project_id = args.project_id
    branch_name = args.branch
    message = args.message
    if message is None:
        message = ""
    commit(project_id=project_id, branch=branch_name, message=message)
elif args.command == 'checkout':
    project_id = args.project_id
    b_init = args.branch_init
    b_updt = args.branch_updt
    ts_updt = args.timestamp_updt
    checkout(project_id, b_init, b_updt, ts_updt)
elif args.command == 'branch':
    name = args.name
    project_id = args.project_id
    branch(project_id, name)
elif args.command == 'remove':
    timestamp = args.timestamp
    remove(timestamp)
elif args.command == 'reset':
    reset()
elif args.command == 'fetch':
    fetch()
elif args.command == 'pull':
    pull()
elif args.command == 'push':
    push()
elif args.command == 'log':
    project_id = args.project_id
    log_timeline(project_id)
else:
    print("No command specified.")