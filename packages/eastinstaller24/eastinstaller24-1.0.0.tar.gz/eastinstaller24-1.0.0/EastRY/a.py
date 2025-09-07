import argparse
import subprocess
import sys
import site

def run_cmd(cmd, success_msg=None, error_msg=None):
    """Run a system command with feedback"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stdout:
            print(result.stdout.strip())
        if success_msg:
            print(success_msg)
    except subprocess.CalledProcessError as e:
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)
        if error_msg:
            print(error_msg)

def main():
    parser = argparse.ArgumentParser(prog="ea", description="EastInstaller24 CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Core package commands
    install = subparsers.add_parser("install", help="Install a package")
    install.add_argument("package")

    remove = subparsers.add_parser("remove", help="Remove a package")
    remove.add_argument("package")

    update = subparsers.add_parser("update", help="Update a package")
    update.add_argument("package")

    show = subparsers.add_parser("show", help="Show details about a package")
    show.add_argument("package")

    freeze = subparsers.add_parser("freeze", help="Output installed packages in requirements.txt format")

    subparsers.add_parser("list", help="List installed packages")
    subparsers.add_parser("check", help="Verify installed packages")
    search = subparsers.add_parser("search", help="Search PyPI for a package")
    search.add_argument("term")

    subparsers.add_parser("outdated", help="List outdated packages")
    subparsers.add_parser("upgrade-all", help="Upgrade all outdated packages")
    subparsers.add_parser("config", help="Show pip configuration")
    subparsers.add_parser("cache", help="Show pip cache info")
    subparsers.add_parser("check-env", help="Show Python environment details")
    subparsers.add_parser("where", help="Show pip executable path")
    subparsers.add_parser("path", help="Show Python executable path")
    subparsers.add_parser("pip-version", help="Show pip version")
    subparsers.add_parser("python-version", help="Show Python version")
    subparsers.add_parser("site-packages", help="Show site-packages paths")
    subparsers.add_parser("check-updates", help="Check for EastInstaller updates")
    subparsers.add_parser("upgrade-pip", help="Upgrade pip itself")
    subparsers.add_parser("list-files", help="List installed files for all packages")
    files = subparsers.add_parser("files", help="List installed files for a package")
    files.add_argument("package")

    subparsers.add_parser("help", help="Show help menu")

    args = parser.parse_args()

    # Core
    if args.command == "install":
        run_cmd([sys.executable, "-m", "pip", "install", args.package],
                f"Installed {args.package}!", f"Failed to install {args.package}")
    elif args.command == "remove":
        run_cmd([sys.executable, "-m", "pip", "uninstall", "-y", args.package],
                f"Removed {args.package}.", f"Failed to remove {args.package}")
    elif args.command == "update":
        run_cmd([sys.executable, "-m", "pip", "install", "--upgrade", args.package],
                f"Updated {args.package}!", f"Failed to update {args.package}")
    elif args.command == "list":
        run_cmd([sys.executable, "-m", "pip", "list"])
    elif args.command == "freeze":
        run_cmd([sys.executable, "-m", "pip", "freeze"])
    elif args.command == "show":
        run_cmd([sys.executable, "-m", "pip", "show", args.package])
    elif args.command == "check":
        run_cmd([sys.executable, "-m", "pip", "check"])
    elif args.command == "search":
        run_cmd([sys.executable, "-m", "pip", "search", args.term])

    # Extra
    elif args.command == "outdated":
        run_cmd([sys.executable, "-m", "pip", "list", "--outdated"])
    elif args.command == "upgrade-all":
        run_cmd([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        run_cmd([sys.executable, "-m", "pip", "list", "--outdated"])
    elif args.command == "config":
        run_cmd([sys.executable, "-m", "pip", "config", "list"])
    elif args.command == "cache":
        run_cmd([sys.executable, "-m", "pip", "cache", "info"])
    elif args.command == "check-env":
        print(sys.version)
    elif args.command == "where":
        run_cmd([sys.executable, "-m", "pip", "--version"])
    elif args.command == "path":
        print(sys.executable)
    elif args.command == "pip-version":
        run_cmd([sys.executable, "-m", "pip", "--version"])
    elif args.command == "python-version":
        print(sys.version)
    elif args.command == "site-packages":
        print(site.getsitepackages())
    elif args.command == "check-updates":
        print("EastInstaller24 is up-to-date!")  # custom msg
    elif args.command == "upgrade-pip":
        run_cmd([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    elif args.command == "list-files":
        run_cmd([sys.executable, "-m", "pip", "show", "-f"])
    elif args.command == "files":
        run_cmd([sys.executable, "-m", "pip", "show", "-f", args.package])

    elif args.command == "help" or args.command is None:
        print("""EastInstaller24 CLI - Commands:
  ea install <pkg>       Install a package
  ea remove <pkg>        Remove a package
  ea update <pkg>        Update a package
  ea list                List installed packages
  ea freeze              Show requirements.txt format
  ea show <pkg>          Show package details
  ea check               Verify installed packages
  ea search <term>       Search PyPI
  ea outdated            List outdated packages
  ea upgrade-all         Upgrade all outdated packages
  ea config              Show pip config
  ea cache               Show pip cache info
  ea check-env           Show environment details
  ea where               Show pip executable path
  ea path                Show Python executable path
  ea pip-version         Show pip version
  ea python-version      Show Python version
  ea site-packages       Show site-packages directory
  ea check-updates       Check for EastInstaller updates
  ea upgrade-pip         Upgrade pip itself
  ea list-files          List installed files for all packages
  ea files <pkg>         Show installed files of a package
""")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


