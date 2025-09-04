#!/usr/bin/env python3
"""
Nessus Scanner - Raw Data Collection
====================================
This program performs Nessus vulnerability scans and saves all raw data
collected from the Nessus API to files for later analysis.

Features:
- Connect to Nessus server via API
- Perform comprehensive vulnerability scans
- Save raw scan results in JSON format
- Export detailed vulnerability data for each host
- Store plugin details for all discovered vulnerabilities
"""

import requests
import json
import time
import urllib3
import os
from typing import Dict, List, Optional
import argparse
from datetime import datetime

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NessusScanner:
    """
    Nessus scanner that collects raw vulnerability data from targets.
    """
    
    def __init__(self, server_url: str, username: str, password: str, verify_ssl: bool = False):
        """
        Initialize the Nessus scanner.
        
        Args:
            server_url: Nessus server URL (e.g., "https://nessus.example.com:8834")
            username: Nessus username
            password: Nessus password
            verify_ssl: Whether to verify SSL certificates (default: False)
        """
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.token = None
        self.last_scan_id = None
        
        # Authenticate and get session token
        if not self._authenticate():
            raise Exception("Failed to authenticate with Nessus server")
    
    def _authenticate(self) -> bool:
        """Authenticate with the Nessus server and get session token."""
        try:
            auth_data = {
                'username': self.username,
                'password': self.password
            }
            
            response = self.session.post(
                f"{self.server_url}/session",
                json=auth_data,
                verify=self.verify_ssl
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.session.headers.update({'X-Cookie': f'token={self.token}'})
                print("[+] Successfully authenticated with Nessus server")
                return True
            else:
                print(f"[!] Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"[!] Error during authentication: {e}")
            return False
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, 
                     timeout: int = 30) -> Optional[requests.Response]:
        """
        Make an authenticated request to the Nessus API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request data (for POST/PUT)
            timeout: Request timeout in seconds
            
        Returns:
            Response object or None if error
        """
        try:
            url = f"{self.server_url}{endpoint}"
            
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=timeout)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=timeout)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=timeout)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=timeout)
            else:
                print(f"[!] Unsupported HTTP method: {method}")
                return None
            
            if response.status_code not in [200, 201, 202]:
                print(f"[!] API request failed: {response.status_code} - {response.text}")
                return None
                
            return response
            
        except Exception as e:
            print(f"[!] Error making API request: {e}")
            return None
    
    def list_scan_templates(self) -> List[Dict]:
        """List all available scan templates."""
        try:
            response = self._make_request('GET', '/editor/scan/templates')
            if response:
                data = response.json()
                templates = data.get('templates', [])
                print(f"[+] Found {len(templates)} scan templates")
                return templates
            return []
        except Exception as e:
            print(f"[!] Error listing templates: {e}")
            return []
    
    def create_scan(self, name: str, targets: str, template_uuid: str = None) -> Optional[str]:
        """
        Create a new scan.
        
        Args:
            name: Scan name
            targets: Target IP addresses or hostnames (comma-separated)
            template_uuid: Template UUID (if not using default)
            
        Returns:
            Scan ID if successful, None otherwise
        """
        try:
            # If no template specified, use basic network scan template
            if not template_uuid:
                templates = self.list_scan_templates()
                basic_template = next((t for t in templates if 'basic' in t.get('name', '').lower()), None)
                if basic_template:
                    template_uuid = basic_template.get('uuid')
                else:
                    print("[!] No suitable template found")
                    return None
            
            scan_data = {
                'uuid': template_uuid,
                'settings': {
                    'name': name,
                    'text_targets': targets,
                    'enabled': True
                }
            }
            
            response = self._make_request('POST', '/scans', scan_data)
            if response:
                data = response.json()
                scan_id = data.get('scan', {}).get('id')
                self.last_scan_id = scan_id
                print(f"[+] Scan created successfully. Scan ID: {scan_id}")
                return str(scan_id)
            return None
            
        except Exception as e:
            print(f"[!] Error creating scan: {e}")
            return None
    
    def launch_scan(self, scan_id: Optional[str] = None) -> bool:
        """Launch a scan."""
        if not scan_id:
            scan_id = self.last_scan_id
        
        if not scan_id:
            print("[!] No scan ID provided or available")
            return False
        
        try:
            response = self._make_request('POST', f'/scans/{scan_id}/launch')
            if response:
                print(f"[+] Scan {scan_id} launched successfully")
                return True
            return False
            
        except Exception as e:
            print(f"[!] Error launching scan: {e}")
            return False
    
    def get_scan_status(self, scan_id: Optional[str] = None) -> Optional[str]:
        """Get the status of a scan."""
        if not scan_id:
            scan_id = self.last_scan_id
        
        if not scan_id:
            print("[!] No scan ID provided or available")
            return None
        
        try:
            response = self._make_request('GET', f'/scans/{scan_id}')
            if response:
                data = response.json()
                status = data.get('info', {}).get('status')
                return status
            return None
            
        except Exception as e:
            print(f"[!] Error getting scan status: {e}")
            return None
    
    def wait_for_scan_completion(self, scan_id: Optional[str] = None, 
                               check_interval: int = 30, max_wait: int = 3600) -> bool:
        """Wait for a scan to complete."""
        if not scan_id:
            scan_id = self.last_scan_id
        
        if not scan_id:
            print("[!] No scan ID provided or available")
            return False
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.get_scan_status(scan_id)
            
            if status and status.lower() == 'completed':
                print(f"[+] Scan {scan_id} completed successfully")
                return True
            elif status and status.lower() in ['canceled', 'aborted']:
                print(f"[!] Scan {scan_id} was {status}")
                return False
            
            print(f"[*] Scan status: {status} - Waiting... ({int(time.time() - start_time)}s elapsed)")
            time.sleep(check_interval)
        
        print(f"[!] Scan did not complete within {max_wait} seconds")
        return False
    
    def get_raw_scan_results(self, scan_id: Optional[str] = None) -> Optional[Dict]:
        """Get complete raw scan results."""
        if not scan_id:
            scan_id = self.last_scan_id
        
        if not scan_id:
            print("[!] No scan ID provided or available")
            return None
        
        try:
            response = self._make_request('GET', f'/scans/{scan_id}')
            if response:
                print(f"[+] Successfully retrieved raw scan results")
                return response.json()
            return None
            
        except Exception as e:
            print(f"[!] Error getting scan results: {e}")
            return None
    
    def get_detailed_host_vulnerabilities(self, scan_id: str, host_id: int) -> Optional[Dict]:
        """Get detailed vulnerability information for a specific host."""
        try:
            response = self._make_request('GET', f'/scans/{scan_id}/hosts/{host_id}')
            if response:
                return response.json()
            return None
        except Exception as e:
            print(f"[!] Error getting host vulnerabilities: {e}")
            return None
    
    def get_vulnerability_plugin_details(self, scan_id: str, host_id: int, plugin_id: str) -> Optional[Dict]:
        """Get detailed plugin information for a specific vulnerability."""
        try:
            response = self._make_request('GET', f'/scans/{scan_id}/hosts/{host_id}/plugins/{plugin_id}')
            if response:
                return response.json()
            return None
        except Exception as e:
            print(f"[!] Error getting plugin details: {e}")
            return None
    
    def collect_complete_scan_data(self, scan_id: Optional[str] = None) -> Dict:
        """
        Collect all raw scan data including host details and plugin information.
        
        Returns:
            Complete scan data dictionary
        """
        if not scan_id:
            scan_id = self.last_scan_id
        
        if not scan_id:
            print("[!] No scan ID provided or available")
            return {}
        
        print("[*] Collecting complete scan data...")
        
        # Get basic scan results
        scan_data = self.get_raw_scan_results(scan_id)
        if not scan_data:
            return {}
        
        complete_data = {
            'scan_info': scan_data.get('info', {}),
            'hosts': [],
            'raw_scan_data': scan_data,
            'collection_timestamp': datetime.now().isoformat(),
            'scan_id': scan_id
        }
        
        # Process each host
        hosts = scan_data.get('hosts', [])
        print(f"[*] Processing {len(hosts)} hosts...")
        
        for i, host in enumerate(hosts, 1):
            host_id = host.get('host_id')
            hostname = host.get('hostname', 'Unknown')
            
            print(f"[*] Processing host {i}/{len(hosts)}: {hostname} (ID: {host_id})")
            
            # Get detailed host vulnerabilities
            host_details = self.get_detailed_host_vulnerabilities(scan_id, host_id)
            if host_details:
                host_data = {
                    'host_info': host,
                    'detailed_vulnerabilities': host_details,
                    'plugin_details': {}
                }
                
                # Get plugin details for each vulnerability
                vulnerabilities = host_details.get('vulnerabilities', [])
                print(f"[*] Collecting plugin details for {len(vulnerabilities)} vulnerabilities...")
                
                for vuln in vulnerabilities:
                    plugin_id = vuln.get('plugin_id')
                    if plugin_id:
                        plugin_details = self.get_vulnerability_plugin_details(scan_id, host_id, plugin_id)
                        if plugin_details:
                            host_data['plugin_details'][str(plugin_id)] = plugin_details
                
                complete_data['hosts'].append(host_data)
        
        print(f"[+] Complete scan data collection finished")
        return complete_data
    
    def save_raw_data(self, scan_data: Dict, target: str, output_dir: str = "nessus_raw_data") -> str:
        """
        Save raw scan data to files.
        
        Args:
            scan_data: Complete scan data
            target: Target identifier for filename
            boxname: Box name for filename (optional)
            output_dir: Output directory
            
        Returns:
            Path to saved file
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        
            filepath = os.path.join(output_dir, f"nessus_raw_{target.replace('.', '_')}_{timestamp}.json")
            
            # Save data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(scan_data, f, indent=2, ensure_ascii=False)
            
            print(f"[+] Raw scan data saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"[!] Error saving raw data: {e}")
            return ""
    
    def perform_complete_scan(self, target: str, scan_name: str = None, 
                            template_uuid: str = None, output_dir: str = "nessus_raw_data") -> Optional[str]:
        """
        Perform a complete scan workflow and save all raw data.
        
        Args:
            target: Target IP address or hostname
            boxname: Box name for filename generation (optional)
            scan_name: Custom scan name
            template_uuid: Scan template UUID
            output_dir: Output directory for raw data
            
        Returns:
            Path to saved raw data file
        """
        if not scan_name:
            scan_name = f"RawScan_{target}_{int(time.time())}"
        
        print(f"[SCAN] Starting complete scan of target: {target}")
        
        # Create and launch scan
        scan_id = self.create_scan(scan_name, target, template_uuid)
        if not scan_id:
            return None
        
        if not self.launch_scan(scan_id):
            return None
        
        # Wait for completion
        if not self.wait_for_scan_completion(scan_id):
            return None
        
        # Collect all raw data
        complete_data = self.collect_complete_scan_data(scan_id)
        if not complete_data:
            return None
        
        # Save raw data
        filepath = self.save_raw_data(complete_data, target, output_dir)
        
        return filepath
    
    def logout(self) -> bool:
        """Logout from the Nessus server."""
        try:
            response = self._make_request('DELETE', '/session')
            if response:
                print("[+] Successfully logged out from Nessus server")
                return True
            return False
        except Exception as e:
            print(f"[!] Error during logout: {e}")
            return False


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Nessus Raw Data Scanner")
    parser.add_argument("target", help="Target IP address or hostname")
    # parser.add_argument("--boxname", help="Box name for filename generation (e.g., htb-granny, vulnhub-kioptrix)")
    parser.add_argument("--server", default="https://localhost:15858", 
                       help="Nessus server URL (default: https://localhost:15858)")
    parser.add_argument("--username", default="root", 
                       help="Nessus username (default: root)")
    parser.add_argument("--password", default="root", 
                       help="Nessus password (default: root)")
    parser.add_argument("--output-dir", default="nessus_raw_data", 
                       help="Output directory for raw data (default: nessus_raw_data)")
    parser.add_argument("--scan-name", help="Custom scan name")
    parser.add_argument("--template", help="Scan template UUID")
    parser.add_argument("--no-ssl-verify", action="store_true", 
                       help="Disable SSL certificate verification")
    
    args = parser.parse_args()
    
    print("Nessus Raw Data Scanner")
    print("=" * 40)
    print(f"Target: {args.target}")
    print(f"Server: {args.server}")
    print(f"Output Directory: {args.output_dir}")
    print("=" * 40)
    
    try:
        # Initialize scanner
        scanner = NessusScanner(
            server_url=args.server,
            username=args.username,
            password=args.password,
            verify_ssl=not args.no_ssl_verify
        )
        
        # Perform complete scan
        output_file = scanner.perform_complete_scan(
            target=args.target,
            scan_name=args.scan_name,
            template_uuid=args.template,
            output_dir=args.output_dir
        )
        
        if output_file:
            print(f"\n[SUCCESS] Raw scan data saved to: {output_file}")
            print(f"[INFO] Use nessus_parser.py to analyze this data for exploitable vulnerabilities")
        else:
            print(f"\n[FAILED] Scan failed or no data collected")
        
        # Logout
        scanner.logout()
        
    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Example usage if run directly
    if len(os.sys.argv) == 1:
        # Default configuration for testing
        TARGET_IP = "10.129.248.28"
        NESSUS_SERVER = "https://localhost:8834"
        USERNAME = "parrot"
        PASSWORD = "parrot"
        OUTPUT_DIR = "nessus_raw_data"
        print("Nessus Raw Data Scanner")
        print("=" * 40)
        print(f"Target: {TARGET_IP}")
        print(f"Server: {NESSUS_SERVER}")
        print(f"Output Directory: {OUTPUT_DIR}")
        print("=" * 40)
        
        try:
            scanner = NessusScanner(NESSUS_SERVER, USERNAME, PASSWORD)
            output_file = scanner.perform_complete_scan(TARGET_IP, output_dir=OUTPUT_DIR)
            
            if output_file:
                print(f"\n[SUCCESS] Raw scan data saved to: {output_file}")
                print(f"[INFO] Use nessus_parser.py to analyze this data for exploitable vulnerabilities")
            
            scanner.logout()
            
        except Exception as e:
            print(f"[!] Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        main() 