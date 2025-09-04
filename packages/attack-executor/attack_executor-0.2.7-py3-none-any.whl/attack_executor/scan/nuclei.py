import subprocess
import sys

from attack_executor.bash.CommandExecutor import execute_command


class NucleiExecutor:
    def __init__(self):
        """
        It sets up the initial state by assigning values to instance attributes.
        """
        pass

    def scan(self, target):
        result = execute_command(f"nuclei {target}")
        return result['stdout']

if __name__ == "__main__":            
    scanner = NucleiExecutor()
    result = scanner.scan(target="http://10.129.10.68:8500")
    print(result)


