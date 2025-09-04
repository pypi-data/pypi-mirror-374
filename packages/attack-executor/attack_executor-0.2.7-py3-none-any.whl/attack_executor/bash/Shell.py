import subprocess

class ShellExecutor:
    def __init__(self):
        """
        It sets up the initial state by assigning values to instance attributes.
        """
        pass

    def execute_command(self,
                        command):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)

        # # result.stdout
        # print("Standard Output:")
        # print(result.stdout)

        # # result.stderr
        # print("Standard Error:")
        # print(result.stderr)

        # # result.returncode Usually 0 means successful execution
        # print("Return Code", result.returncode)

        return result.stdout, result.stderr, result.returncode

if __name__ == "__main__":
    se = ShellExecutor()
    se.execute_command(command = "sudo nmap -sS -sV -O -A -p 1-1000 10.129.202.170")


