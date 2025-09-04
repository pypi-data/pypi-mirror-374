'''
This script checks if you have installed the necessary tools used by attack-executor 
'''

import subprocess
from rich.console import Console
console = Console()

def check_nmap_installation():
    with console.status("Check if nmap is installed..."):
        try:
            result = subprocess.run(["nmap", "--version"], capture_output=True, text=True, check=True)
            console.print("[bold green][SUCCESS] nmap is installed![/bold green]")
            console.print(result.stdout.splitlines()[0])  # print the version info in the first line
        except FileNotFoundError:
            console.print("[bold red][FAILED] nmap is uninstalled! [/bold red]")
        except subprocess.CalledProcessError:
            console.print("[bold red][FAILED] nmap is uninstalled! [/bold red]")

def check_nuclei_installation():
    with console.status("Check if nuclei is installed..."):
        try:
            result = subprocess.run(["nuclei", "--version"], capture_output=True, text=True, check=True)
            console.print("[bold green][SUCCESS] nuclei is installed![/bold green]")
            if result.stdout:
                console.print(result.stdout.splitlines()[0])  # print the version info in the first line
        except FileNotFoundError:
            console.print("[bold red][FAILED] nuclei is uninstalled! [/bold red]")
        except subprocess.CalledProcessError:
            console.print("[bold red][FAILED] nuclei is uninstalled! [/bold red]")

def check_gobuster_installation():
    with console.status("Check if gobuster is installed..."):
        try:
            result = subprocess.run(["gobuster", "version"], capture_output=True, text=True, check=True)
            console.print("[bold green][SUCCESS] gobuster is installed![/bold green]")
            console.print(result.stdout.splitlines()[0])  # print the version info in the first line
        except FileNotFoundError:
            console.print("[bold red][FAILED] gobuster is uninstalled! [/bold red]")
        except subprocess.CalledProcessError:
            console.print("[bold red][FAILED] gobuster is uninstalled! [/bold red]")
            
def check_nessus_installation():
    with console.status("Check if Nessus is installed..."):
        try:
            # nessuscli is the command line tool for Nessus
            subprocess.run(["nessuscli", "help"], capture_output=True, text=True, check=True)
            console.print("[bold green][SUCCESS] nessus (nessuscli) is installed![/bold green]")
        except FileNotFoundError:
            console.print("[bold red][FAILED] nessus (nessuscli) is uninstalled! [/bold red]")
        except subprocess.CalledProcessError:
            console.print("[bold red][FAILED] nessus (nessuscli) is uninstalled! [/bold red]")

def check_searchsploit_installation():
    with console.status("Check if searchsploit is installed..."):
        try:
            # searchsploit does not support --version, using -h instead and checking output
            result = subprocess.run(["searchsploit", "-h"], capture_output=True, text=True)
            if "Usage: searchsploit" in result.stdout or "Usage: searchsploit" in result.stderr:
                console.print("[bold green][SUCCESS] searchsploit is installed![/bold green]")
            else:
                console.print("[bold red][FAILED] searchsploit check failed! [/bold red]")
        except FileNotFoundError:
            console.print("[bold red][FAILED] searchsploit is uninstalled! [/bold red]")

def check_whatweb_installation():
    with console.status("Check if whatweb is installed..."):
        try:
            result = subprocess.run(["whatweb", "--version"], capture_output=True, text=True, check=True)
            console.print("[bold green][SUCCESS] whatweb is installed![/bold green]")
            console.print(result.stdout.splitlines()[0])
        except FileNotFoundError:
            console.print("[bold red][FAILED] whatweb is uninstalled! [/bold red]")
        except subprocess.CalledProcessError:
            console.print("[bold red][FAILED] whatweb is uninstalled! [/bold red]")

def check_sliver_installation():
    with console.status("Check if sliver-client is installed..."):
        try:
            # Sliver does not have a --version flag, use -h to check if it's installed
            subprocess.run(["sliver-client", "-h"], capture_output=True, text=True, check=True)
            console.print("[bold green][SUCCESS] sliver-client is installed![/bold green]")
        except FileNotFoundError:
            console.print("[bold red][FAILED] sliver-client is uninstalled! [/bold red]")
        except subprocess.CalledProcessError:
            console.print("[bold red][FAILED] sliver-client is uninstalled! [/bold red]")

def check_metasploit_installation():
    with console.status("Check if metasploit is installed..."):
        try:
            result = subprocess.run(["msfconsole", "--version"], capture_output=True, text=True, check=True)
            console.print("[bold green][SUCCESS] metasploit is installed![/bold green]")
            if result.stdout:
                console.print(result.stdout.strip())
        except FileNotFoundError:
            console.print("[bold red][FAILED] metasploit is uninstalled! [/bold red]")
        except subprocess.CalledProcessError:
            console.print("[bold red][FAILED] metasploit is uninstalled! [/bold red]")

def check_owasp_zap_installation():
    with console.status("Check if OWASP ZAP is installed..."):
        try:
            # The command to check ZAP's version is zap.sh -version
            result = subprocess.run(["zap.sh", "-version"], capture_output=True, text=True, check=True)
            console.print("[bold green][SUCCESS] OWASP ZAP is installed![/bold green]")
            if result.stdout:
                console.print(result.stdout.strip())
        except FileNotFoundError:
            console.print("[bold red][FAILED] OWASP ZAP is uninstalled! [/bold red]")
        except subprocess.CalledProcessError as e:
            # ZAP returns a non-zero exit code on -version, so check stderr
            if "ZAP" in e.stderr:
                console.print("[bold green][SUCCESS] OWASP ZAP is installed![/bold green]")
                console.print(e.stderr.strip())
            else:
                console.print("[bold red][FAILED] OWASP ZAP is uninstalled! [/bold red]")

def check_installation():
    check_nmap_installation()
    check_nuclei_installation()
    check_gobuster_installation()
    # skip nessus for now
    # check_nessus_installation()
    check_searchsploit_installation()
    check_whatweb_installation()
    check_sliver_installation()
    check_metasploit_installation()
    check_owasp_zap_installation()


if __name__ == "__main__":
    check_installation()
