import argparse

from version_timeline.VersionTimeline import VersionTimeline

from command_line_interface.Add import add
from command_line_interface.Get import get
from command_line_interface.Commit import commit
from command_line_interface.Fetch import fetch
from command_line_interface.Pull import pull
from command_line_interface.Push import push
from command_line_interface.Remove import remove

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
commit_parser.add_argument('-i', '--timestamp_init', type=str, required=True, help='Timestamp of the initial graph model.')
commit_parser.add_argument('-u', '--timestamp_updt', type=str, required=True, help='Timestamp of the updated graph model.')

# "remove" command parser
remove_parser = subparsers.add_parser('remove', help='Removes all nodes and relationships with the given timestamp from the database.')
remove_parser.add_argument('-t', '--timestamp', type=str, required=True, help='Timestamp of the graph model to remove.')

# "fetch" command parser
fetch_parser = subparsers.add_parser('fetch', help='Fetches updates from the remote repository.')

# "pull" command parser
pull_parser = subparsers.add_parser('pull', help='Fetches updates from the remote repository. And merges them into the local repository.')

# "push" command parser
push_parser = subparsers.add_parser('push', help='Pushes local commits to the remote repository.')

args = parser.parse_args()

if args.command == 'add':
    path = args.path
    if args.timestamp is not None:
        timestamp = args.timestamp
    else:
        timestamp = VersionTimeline.create_timestamp()
    print(f"Adding files from path {path} with timestamp: {timestamp}")
    add(path, timestamp)
elif args.command == 'get':
    path = args.path
    timestamp = args.timestamp
    print(f"Parsing file to path: {path}")
    get(path, timestamp)
elif args.command == 'commit':
    ts_init = args.timestamp_init
    ts_updt = args.timestamp_updt
    print(f"Running diff and creating patch between graph models with timestamps {ts_init} and {ts_updt}.")
    commit(ts_init, ts_updt)
elif args.command == 'remove':
    timestamp = args.timestamp
    print(f"Removing all nodes and relationships with timestamp: {timestamp}")
    remove(timestamp)
elif args.command == 'fetch':
    print("Fetching updates from remote repository.")
    fetch()
elif args.command == 'pull':
    print("Pulling updates from remote repository.")
    pull()
elif args.command == 'push':
    print("Pushing local commits to remote repository.")
    push()
else:
    print("No command specified.")