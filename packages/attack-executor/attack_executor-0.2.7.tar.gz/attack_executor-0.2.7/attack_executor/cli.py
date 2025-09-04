import argparse
from attack_executor.check_installation import check_installation

def main():
    parser = argparse.ArgumentParser(description="Attack Executor command line interface")
    parser.add_argument('--check_install', action='store_true', help='Check installation status.')
    args = parser.parse_args()

    if args.check_install:
        check_installation()
    else:
        print("No command specified. Use --help for usage.")