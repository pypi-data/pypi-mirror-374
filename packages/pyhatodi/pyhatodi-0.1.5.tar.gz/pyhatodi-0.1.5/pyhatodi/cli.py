import sys
import importlib

def main():
    if len(sys.argv) < 2:
        print("Usage: pyhatodi <command_module>")
        sys.exit(1)

    command_module_name = sys.argv[1]

    try:
        command_module = importlib.import_module(f'pyhatodi.commands.{command_module_name}')
    except ModuleNotFoundError:
        print(f"Error: Command module '{command_module_name}' not found.")
        sys.exit(1)

    if hasattr(command_module, 'run'):
        args = []
        if len(sys.argv) > 2:
            args = sys.argv[2:]
        command_module.run(*args)
    else:
        print(f"Error: Command module '{command_module_name}' does not have a 'run' function.")
        sys.exit(1)

if __name__ == "__main__":
    main()