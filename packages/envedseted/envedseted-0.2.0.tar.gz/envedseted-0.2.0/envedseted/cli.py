import argparse
from . import set_var, get_var, delete_var, list_vars, path

def main():
    parser = argparse.ArgumentParser(description="EnvSet - Manage environment variables and PATH")
    subparsers = parser.add_subparsers(dest="command")

    # General env commands
    env_parser = subparsers.add_parser("env")
    env_parser.add_argument("action", choices=["set", "get", "delete", "list"])
    env_parser.add_argument("name", nargs="?")
    env_parser.add_argument("value", nargs="?")
    env_parser.add_argument("--scope", choices=["user", "system"], default="user")

    # PATH commands
    path_parser = subparsers.add_parser("path")
    path_parser.add_argument("action", choices=["add", "remove", "list", "backup", "restore"])
    path_parser.add_argument("dir_path", nargs="?")
    path_parser.add_argument("--scope", choices=["user", "system"], default="user")
    path_parser.add_argument("--position", choices=["start", "end"], default="end")

    args = parser.parse_args()

    if args.command == "env":
        if args.action == "set":
            set_var(args.name, args.value, args.scope)
        elif args.action == "get":
            val = get_var(args.name)
            print(f"{args.name}={val}" if val else f"{args.name} not found")
        elif args.action == "delete":
            delete_var(args.name, args.scope)
        elif args.action == "list":
            list_vars(args.scope)
    elif args.command == "path":
        if args.action == "add":
            path.add(args.dir_path, args.scope, args.position)
        elif args.action == "remove":
            path.remove(args.dir_path, args.scope)
        elif args.action == "list":
            path.list(args.scope)
        elif args.action == "backup":
            path.backup()
        elif args.action == "restore":
            path.restore()

if __name__ == "__main__":
    main()
