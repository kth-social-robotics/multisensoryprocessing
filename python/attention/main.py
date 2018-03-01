# python3 main.py -s -i

"""
Launch point for the kernel-server.
Options:
    -s                          [Launch Server]
    -i                          [Launch Interpreter ]
    -da                         [Dummy Architecture]
Example:
    python3 main.py -i
    python3 main.py -s
    python3 main.py -da
"""
import sys
from src.kernel import Kernel

def _read_command_line(commands, arg):
    if "-" in arg:
        if "i" in arg:
            commands["interpreter"] = True
        if "s" in arg:
            commands["server"] = True
        if "da" in arg:
            commands["architecture_dummy"] = True
    return commands

if __name__ == "__main__":
    if len(sys.argv) > 1:
        commands = {"server":False,
                    "interpreter":False,
                    "architecture_dummy":False}
        for arg in sys.argv:
            commands = _read_command_line(commands, arg)
        kernel = Kernel(commands)
        kernel.run()
    else:
        print(__doc__)
