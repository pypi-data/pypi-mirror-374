import argparse
from . import __version__

def main():
    p = argparse.ArgumentParser(prog="hybrid-vul", description="Hybrid-Vul CLI")
    p.add_argument("--version", action="store_true", help="show version and exit")
    args = p.parse_args()
    if args.version:
        print(__version__)
    else:
        print("Hybrid-Vul installed. Try: hybrid-vul --version")
