import argparse
import subprocess
import xml.etree.ElementTree as ET
import json
import sys
# from penetrationPlanner.parser.searchsploit import get_searchsploit_queries


class SearchsploitExecutor:
    """
    Class to execute searchsploit commands and process the results.
    Similar to how NmapExecutor works but for searchsploit.
    """
    
    def __init__(self):
        """
        Initialize the SearchsploitExecutor.
        """
        pass
    
    def search_exploits(self, query):
        """
        Run searchsploit with a query and return the exploits found.
        
        Args:
            query: The search query for searchsploit
            
        Returns:
            List of exploit dictionaries
        """
        cmd = ["searchsploit", "--json", query]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        if res.returncode != 0 or not res.stdout:
            return []
        try:
            data = json.loads(res.stdout)
            return data.get("RESULTS_EXPLOIT", [])
        except json.JSONDecodeError:
            return []
    
    def filter_and_index_exploits(self, results):
        """
        Given the output from searchsploit(), return a dict indexed by CVE numbers.
        
        Args:
            results: List of dictionaries from searchsploit()
            
        Returns:
            Dict where keys are CVE numbers and values are dicts with service and exploit info
        """
        cve_index = {}
        for service in results:
            if not service.get('exploits'):
                continue
            
            for exploit in service['exploits']:
                codes = exploit.get('Codes', '')
                
                # Extract all CVE numbers from the Codes field
                cves = [code.strip() for code in codes.split(';') if code.strip().startswith('CVE-')]
                
                # If there are no CVEs, skip this exploit
                if not cves:
                    continue
                    
                # Add each CVE to the index
                for cve in cves:
                    cve_index[cve] = {
                        'service': service['name'],
                        'address': service['address'],
                        'exploit_title': exploit.get('Title', 'Unknown exploit'),
                        'exploit_path': exploit.get('Path', ''),
                        'exploit_id': exploit.get('EDB-ID', ''),
                        'port': exploit.get('Port', ''),
                        'type': exploit.get('Type', ''),
                        'platform': exploit.get('Platform', '')
                    }
        
        return cve_index
    
    def search(self, target, predicates):
        """
        Search for exploits based on predicates and return results.
        
        Args:
            target: The target host IP
            predicates: List of PDDL predicates from nmap parser
            
        Returns:
            List of dictionaries containing services and their exploits
        """
        # Get search queries from predicates using our parser
        search_queries = get_searchsploit_queries(predicates)
        
        # List to store results
        results = []
        
        # For each query, search for exploits
        for query in search_queries:
            # Search for exploits
            exploits = self.search_exploits(query)
            
            # Create a service entry using the query
            service = {
                "name": query,
                "product": "",
                "version": "",
                "address": target,
                "exploits": exploits
            }
            
            # Parse query to try to get product and version
            parts = query.split()
            if len(parts) > 1:
                # Try to extract version if available
                for part in reversed(parts):
                    if any(c.isdigit() for c in part):
                        service["version"] = part
                        service["product"] = " ".join(parts[:-1])
                        break
            
            results.append(service)
        
        return results
    
    def search_with_cve_index(self, target, predicates):
        """
        Search for exploits and return both full results and a CVE-indexed dictionary.
        
        Args:
            target: The target host IP
            predicates: List of PDDL predicates from nmap parser
            
        Returns:
            Tuple with (results, cve_index)
        """
        results = self.search(target, predicates)
        cve_index = self.filter_and_index_exploits(results)
        return results, cve_index


# Legacy functions for backwards compatibility
def search_exploits(query):
    """Legacy function for backwards compatibility"""
    executor = SearchsploitExecutor()
    return executor.search_exploits(query)

def filter_and_index_exploits(results):
    """Legacy function for backwards compatibility"""
    executor = SearchsploitExecutor()
    return executor.filter_and_index_exploits(results)

def searchsploit(target, predicates):
    """Legacy function for backwards compatibility"""
    executor = SearchsploitExecutor()
    return executor.search(target, predicates)

def searchsploit_with_cve_index(target, predicates):
    """Legacy function for backwards compatibility"""
    executor = SearchsploitExecutor()
    return executor.search_with_cve_index(target, predicates)


# Example usage
if __name__ == "__main__":
    predicates = [
        '(microsoft_dns_6_1_7601_running 10.129.17.237)', 
        '(kerberos_running 10.129.17.237)',
        '(msrpc_running 10.129.17.237)',
        '(netbios_ssn_running 10.129.17.237)',
        '(ad_ldap_running 10.129.17.237)',
        '(microsoft_ds_running 10.129.17.237)',
        '(msrpc_over_http_running 10.129.17.237)',
        '(mc_nmf_running 10.129.17.237)',
        '(microsoft_httpapi_2_0_running 10.129.17.237)'
    ]
    
    # Create an instance of the executor
    executor = SearchsploitExecutor()
    
    # Search for exploits
    results, cve_index = executor.search_with_cve_index("10.129.17.237", predicates)
    
    print("Services with exploits:")
    for service in results:
        if service['exploits']:
            print(f"  {service['name']}: {len(service['exploits'])} exploits found")
            
    print("\nExploits by CVE:")
    for cve, info in cve_index.items():
        print(f"  {cve}: {info['exploit_title']} (for {info['service']})")








