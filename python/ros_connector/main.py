"""
Launch point for the kernel-server.
Options:
    -i                          [Launch Interpreter ]
    -s                          [Launch Server]
    -r                          [Launch ROS subscriber]
    -da                         [Dummy Architecture]
    -dy                         [Dummy Yumi]
Example:
    python main.py -isr --data=lego/Lego_DB1_shuffle1.csv
"""
import sys
from src.kernel import Kernel


def _read_command_line(commands, arg):
    if "-" in arg:
        if "i" in arg:
            commands["interpreter"] = True
        if "s" in arg:
            commands["server"] = True
        if "r" in arg:
            commands["subscriber"] = True
        if "da" in arg:
            commands["architecture_dummy"] = True
        if "dy" in arg:
            commands["yumi_dummy"] = True
    return commands

if __name__ == "__main__":
    if len(sys.argv) > 1:
        commands = {"server":False,
                    "subscriber":False,
                    "interpreter":False,
                    "architecture_dummy":False,
                    "yumi_dummy":False}
        for arg in sys.argv:
            commands = _read_command_line(commands, arg)
        kernel = Kernel(commands)
        kernel.run()
    else:
        print(__doc__)