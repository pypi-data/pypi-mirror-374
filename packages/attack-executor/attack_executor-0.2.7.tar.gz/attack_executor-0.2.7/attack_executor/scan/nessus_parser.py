#!/usr/bin/env python3
"""
Nessus Parser - Exploit Framework Analysis
==========================================
This program analyzes raw Nessus scan data and extracts vulnerabilities that have
available exploit frameworks, sorted by CVSS v3.0 Base Score.

Features:
- Parse raw Nessus scan data from JSON files
- Extract vulnerabilities with exploit frameworks (Metasploit, CANVAS, Core Impact, etc.)
- Sort by CVSS v3.0 Base Score (highest first)
- Generate detailed exploit framework reports
- Create Metasploit resource scripts
- Export results in multiple formats
"""

import json
import os
import argparse
import re
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime


class NessusExploitParser:
    """
    Parser for raw Nessus scan data that identifies vulnerabilities with exploit frameworks.
    """
    
    def __init__(self, raw_data_file: str):
        """
        Initialize the Nessus exploit parser.
        
        Args:
            raw_data_file: Path to raw Nessus scan data JSON file
        """
        self.raw_data_file = raw_data_file
        self.raw_data = {}
        self.exploitable_vulns = []
        
        # Load raw data
        if not self.load_raw_data():
            raise Exception(f"Failed to load raw data from {raw_data_file}")
    
    def load_raw_data(self) -> bool:
        """Load raw scan data from JSON file."""
        try:
            with open(self.raw_data_file, 'r', encoding='utf-8') as f:
                self.raw_data = json.load(f)
            print(f"[+] Successfully loaded raw data from {self.raw_data_file}")
            return True
        except Exception as e:
            print(f"[!] Error loading raw data: {e}")
            return False
    
    def extract_exploit_frameworks(self, plugin_details: Dict) -> List[Dict]:
        """
        Extract exploit framework information from plugin details.
        
        Args:
            plugin_details: Detailed plugin information
            
        Returns:
            List of exploit framework dictionaries
        """
        frameworks = []
        
        try:
            # Navigate to exploit frameworks section
            plugin_output = plugin_details.get('info', {}).get('plugindescription', {})
            plugin_attributes = plugin_output.get('pluginattributes', {})
            
            # Check for exploit_frameworks in vuln_information section (this is the correct location)
            vuln_info = plugin_attributes.get('vuln_information', {})
            if 'exploit_frameworks' in vuln_info:
                exploit_frameworks = vuln_info['exploit_frameworks']
                
                # Handle different structures
                if isinstance(exploit_frameworks, dict):
                    # Check for exploit_framework array
                    if 'exploit_framework' in exploit_frameworks:
                        framework_list = exploit_frameworks['exploit_framework']
                        
                        # Ensure it's a list
                        if not isinstance(framework_list, list):
                            framework_list = [framework_list]
                        
                        for framework in framework_list:
                            framework_info = {
                                'name': framework.get('name', 'Unknown'),
                                'exploits': []
                            }
                            
                            # Extract exploit details
                            if 'exploits' in framework and 'exploit' in framework['exploits']:
                                exploits = framework['exploits']['exploit']
                                
                                # Ensure it's a list
                                if not isinstance(exploits, list):
                                    exploits = [exploits]
                                
                                for exploit in exploits:
                                    exploit_info = {
                                        'name': exploit.get('name', 'Unknown'),
                                        'url': exploit.get('url', '')
                                    }
                                    framework_info['exploits'].append(exploit_info)
                            
                            # Handle frameworks without specific exploit details (like CANVAS, Core Impact)
                            elif 'packages' in framework:
                                # Some frameworks like CANVAS have package info instead of exploit details
                                packages = framework.get('packages', {}).get('package', [])
                                if packages:
                                    framework_info['exploits'] = [{'name': f"Package: {pkg}", 'url': ''} for pkg in packages]
                                else:
                                    framework_info['exploits'] = [{'name': 'Available', 'url': ''}]
                            else:
                                # Framework available but no specific exploit details
                                framework_info['exploits'] = [{'name': 'Available', 'url': ''}]
                            
                            frameworks.append(framework_info)
            
            # Also check for exploit_frameworks section directly in plugin attributes (fallback)
            if not frameworks and 'exploit_frameworks' in plugin_attributes:
                exploit_frameworks = plugin_attributes['exploit_frameworks']
                
                # Handle different structures
                if isinstance(exploit_frameworks, dict):
                    # Check for exploit_framework array
                    if 'exploit_framework' in exploit_frameworks:
                        framework_list = exploit_frameworks['exploit_framework']
                        
                        # Ensure it's a list
                        if not isinstance(framework_list, list):
                            framework_list = [framework_list]
                        
                        for framework in framework_list:
                            framework_info = {
                                'name': framework.get('name', 'Unknown'),
                                'exploits': []
                            }
                            
                            # Extract exploit details
                            if 'exploits' in framework and 'exploit' in framework['exploits']:
                                exploits = framework['exploits']['exploit']
                                
                                # Ensure it's a list
                                if not isinstance(exploits, list):
                                    exploits = [exploits]
                                
                                for exploit in exploits:
                                    exploit_info = {
                                        'name': exploit.get('name', 'Unknown'),
                                        'url': exploit.get('url', '')
                                    }
                                    framework_info['exploits'].append(exploit_info)
                            
                            frameworks.append(framework_info)
            
            # Also check for individual framework flags in plugin attributes
            framework_flags = [
                'exploit_framework_metasploit',
                'exploit_framework_canvas', 
                'exploit_framework_core',
                'exploit_framework_exploithub',
                'exploit_framework_d2_elliot',
                'exploit_framework_saint'
            ]
            
            for flag in framework_flags:
                if flag in plugin_attributes:
                    flag_value = plugin_attributes[flag]
                    if isinstance(flag_value, str) and flag_value.lower() == 'true':
                        framework_name = flag.replace('exploit_framework_', '').title()
                        
                        # Check if we already have this framework from detailed section
                        existing = next((f for f in frameworks if f['name'].lower() == framework_name.lower()), None)
                        if not existing:
                            frameworks.append({
                                'name': framework_name,
                                'exploits': [{'name': 'Available', 'url': ''}]
                            })
                        
        except Exception as e:
            print(f"[!] Error extracting exploit frameworks: {e}")
        
        return frameworks
    
    def extract_vulnerability_info(self, host_data: Dict, vuln: Dict, plugin_details: Dict) -> Optional[Dict]:
        """
        Extract comprehensive vulnerability information from plugin details.
        
        Args:
            host_data: Host information
            vuln: Basic vulnerability info
            plugin_details: Detailed plugin information
            
        Returns:
            Comprehensive vulnerability information dictionary
        """
        try:
            # Extract plugin output and attributes
            plugin_output = plugin_details.get('info', {}).get('plugindescription', {})
            plugin_attributes = plugin_output.get('pluginattributes', {})
            
            # Initialize vulnerability info structure
            vuln_info = {
                'host': host_data.get('host_info', {}).get('hostname', 'Unknown'),
                'host_id': host_data.get('host_info', {}).get('host_id', ''),
                'plugin_id': vuln.get('plugin_id', ''),
                'plugin_name': vuln.get('plugin_name', ''),
                'severity': vuln.get('severity', 0),
                'severity_name': self._get_severity_name(vuln.get('severity', 0)),
                'exploit_frameworks': [],
                'cve_ids': [],
                'cpe': [],
                'patch_date': '',
                'vuln_pub_date': '',
                'description': '',
                'solution': '',
                'risk_factor': '',
                'cvss_v2_score': '',
                'cvss_v3_score': '',
                'cvss_v2_vector': '',
                'cvss_v3_vector': '',
                'exploit_available': False,
                'exploit_ease': '',
                'in_the_news': False,
                'unsupported_by_vendor': False,
                'plugin_output': ''
            }
            
            # Extract exploit frameworks
            vuln_info['exploit_frameworks'] = self.extract_exploit_frameworks(plugin_details)
            
            # Set exploit_available flag if we have exploit frameworks
            if vuln_info['exploit_frameworks']:
                vuln_info['exploit_available'] = True
            
            # Extract information from vuln_information section
            plugin_vuln_info = plugin_attributes.get('vuln_information', {})
            
            # Check for explicit exploit availability
            if 'exploit_available' in plugin_vuln_info:
                exploit_available = plugin_vuln_info['exploit_available']
                if isinstance(exploit_available, str):
                    vuln_info['exploit_available'] = exploit_available.lower() == 'true'
                else:
                    vuln_info['exploit_available'] = bool(exploit_available)
            
            # Extract exploitability ease
            if 'exploitability_ease' in plugin_vuln_info:
                vuln_info['exploit_ease'] = plugin_vuln_info['exploitability_ease']
            
            # Check if in the news
            if 'in_the_news' in plugin_vuln_info:
                in_news = plugin_vuln_info['in_the_news']
                if isinstance(in_news, str):
                    vuln_info['in_the_news'] = in_news.lower() == 'true'
                else:
                    vuln_info['in_the_news'] = bool(in_news)
            
            # Check if unsupported by vendor
            if 'unsupported_by_vendor' in plugin_vuln_info:
                unsupported = plugin_vuln_info['unsupported_by_vendor']
                if isinstance(unsupported, str):
                    vuln_info['unsupported_by_vendor'] = unsupported.lower() == 'true'
                else:
                    vuln_info['unsupported_by_vendor'] = bool(unsupported)
            
            # Extract vulnerability publication date
            if 'vuln_publication_date' in plugin_vuln_info:
                vuln_info['vuln_pub_date'] = plugin_vuln_info['vuln_publication_date']
            
            # Extract patch publication date
            if 'patch_publication_date' in plugin_vuln_info:
                vuln_info['patch_date'] = plugin_vuln_info['patch_publication_date']
            
            # Extract CPE from vuln_information
            if 'cpe' in plugin_vuln_info:
                cpe_data = plugin_vuln_info['cpe']
                if isinstance(cpe_data, list):
                    vuln_info['cpe'] = cpe_data
                elif isinstance(cpe_data, str):
                    vuln_info['cpe'] = [cpe_data]
            
            # Extract CPE information from main plugin attributes (fallback)
            if not vuln_info['cpe'] and 'cpe' in plugin_attributes:
                cpe_data = plugin_attributes['cpe']
                if isinstance(cpe_data, list):
                    vuln_info['cpe'] = cpe_data
                elif isinstance(cpe_data, str):
                    vuln_info['cpe'] = [cpe_data]
            
            # Extract risk information
            if 'risk_information' in plugin_attributes:
                risk_info = plugin_attributes['risk_information']
                
                # Extract CVSS v2 information
                if 'cvss_base_score' in risk_info:
                    vuln_info['cvss_v2_score'] = risk_info['cvss_base_score']
                
                if 'cvss_vector' in risk_info:
                    vuln_info['cvss_v2_vector'] = risk_info['cvss_vector']
                
                # Extract risk factor
                if 'risk_factor' in risk_info:
                    vuln_info['risk_factor'] = risk_info['risk_factor']
            
            # Extract CVSS v3 information
            if 'cvss3_base_score' in plugin_attributes:
                vuln_info['cvss_v3_score'] = plugin_attributes['cvss3_base_score']
            
            if 'cvss3_vector' in plugin_attributes:
                vuln_info['cvss_v3_vector'] = plugin_attributes['cvss3_vector']
            
            # Extract CVE information
            if 'cve' in plugin_attributes:
                cve_data = plugin_attributes['cve']
                if isinstance(cve_data, list):
                    vuln_info['cve_ids'] = cve_data
                elif isinstance(cve_data, str):
                    vuln_info['cve_ids'] = [cve_data]
            
            # Extract description and solution
            if 'description' in plugin_output:
                description = plugin_output['description']
                if isinstance(description, str):
                    vuln_info['description'] = description[:500] + "..." if len(description) > 500 else description
            
            if 'solution' in plugin_output:
                solution = plugin_output['solution']
                if isinstance(solution, str):
                    vuln_info['solution'] = solution[:300] + "..." if len(solution) > 300 else solution
            
            # Extract plugin output
            if 'plugin_output' in plugin_output:
                vuln_info['plugin_output'] = plugin_output['plugin_output'][:1000] + "..." if len(plugin_output.get('plugin_output', '')) > 1000 else plugin_output.get('plugin_output', '')
            
            return vuln_info
            
        except Exception as e:
            print(f"[!] Error extracting vulnerability info for plugin {vuln.get('plugin_id', 'unknown')}: {e}")
            return None
    
    def _get_severity_name(self, severity: int) -> str:
        """Convert severity number to name."""
        severity_map = {
            0: "INFO",
            1: "LOW", 
            2: "MEDIUM",
            3: "HIGH",
            4: "CRITICAL"
        }
        return severity_map.get(severity, "UNKNOWN")
    
    def _get_cvss_v3_score_float(self, vuln: Dict) -> float:
        """
        Get CVSS v3 score as float for sorting.
        
        Args:
            vuln: Vulnerability dictionary
            
        Returns:
            CVSS v3 score as float, falls back to CVSS v2, then severity
        """
        try:
            # Try CVSS v3 first
            if vuln.get('cvss_v3_score'):
                return float(vuln['cvss_v3_score'])
            
            # Fall back to CVSS v2
            if vuln.get('cvss_v2_score'):
                return float(vuln['cvss_v2_score'])
            
            # Fall back to severity level (map to rough CVSS equivalent)
            severity_to_cvss = {
                4: 9.0,   # CRITICAL
                3: 7.0,   # HIGH
                2: 5.0,   # MEDIUM
                1: 3.0,   # LOW
                0: 0.0    # INFO
            }
            return severity_to_cvss.get(vuln.get('severity', 0), 0.0)
            
        except (ValueError, TypeError):
            # If conversion fails, fall back to severity
            severity_to_cvss = {
                4: 9.0,   # CRITICAL
                3: 7.0,   # HIGH
                2: 5.0,   # MEDIUM
                1: 3.0,   # LOW
                0: 0.0    # INFO
            }
            return severity_to_cvss.get(vuln.get('severity', 0), 0.0)
    
    def filter_vulnerabilities_with_exploits(self) -> List[Dict]:
        """
        Filter scan data to find vulnerabilities with exploit frameworks.
        
        Returns:
            List of vulnerabilities with exploit frameworks
        """
        exploitable_vulns = []
        
        print("[*] Analyzing raw scan data for vulnerabilities with exploit frameworks...")
        
        hosts = self.raw_data.get('hosts', [])
        print(f"[*] Processing {len(hosts)} hosts...")
        
        for host_data in hosts:
            host_info = host_data.get('host_info', {})
            hostname = host_info.get('hostname', 'Unknown')
            
            # Get vulnerabilities for this host
            detailed_vulns = host_data.get('detailed_vulnerabilities', {})
            vulnerabilities = detailed_vulns.get('vulnerabilities', [])
            plugin_details = host_data.get('plugin_details', {})
            
            print(f"[*] Processing host {hostname}: {len(vulnerabilities)} vulnerabilities")
            
            for vuln in vulnerabilities:
                plugin_id = str(vuln.get('plugin_id', ''))
                
                # Get detailed plugin information
                if plugin_id in plugin_details:
                    plugin_detail = plugin_details[plugin_id]
                    vuln_info = self.extract_vulnerability_info(host_data, vuln, plugin_detail)
                    
                    # Only include vulnerabilities that have exploit frameworks
                    if vuln_info and vuln_info.get('exploit_frameworks'):
                        exploitable_vulns.append(vuln_info)
        
        # Sort by CVSS v3.0 Base Score (highest first)
        exploitable_vulns.sort(key=self._get_cvss_v3_score_float, reverse=True)
        
        self.exploitable_vulns = exploitable_vulns
        print(f"[+] Found {len(exploitable_vulns)} vulnerabilities with exploit frameworks")
        
        return exploitable_vulns
    
    def generate_exploit_framework_report(self, exploitable_vulns: Optional[List[Dict]] = None) -> str:
        """
        Generate a detailed report of vulnerabilities with exploit frameworks.
        
        Args:
            exploitable_vulns: List of vulnerabilities with exploit frameworks
            
        Returns:
            Formatted report string
        """
        if not exploitable_vulns:
            exploitable_vulns = self.exploitable_vulns
            
        if not exploitable_vulns:
            return "No vulnerabilities with exploit frameworks found."
        
        report = []
        report.append("=" * 80)
        report.append("VULNERABILITIES WITH EXPLOIT FRAMEWORKS REPORT")
        report.append("Sorted by CVSS v3.0 Base Score (Highest First)")
        report.append("=" * 80)
        report.append("")
        
        # Scan information
        scan_info = self.raw_data.get('scan_info', {})
        report.append("SCAN INFORMATION")
        report.append("-" * 20)
        report.append(f"Scan Name: {scan_info.get('name', 'Unknown')}")
        report.append(f"Target: {scan_info.get('targets', 'Unknown')}")
        report.append(f"Scan Start: {scan_info.get('scan_start', 'Unknown')}")
        report.append(f"Scan End: {scan_info.get('scan_end', 'Unknown')}")
        report.append(f"Data Collection: {self.raw_data.get('collection_timestamp', 'Unknown')}")
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 20)
        report.append(f"Total Vulnerabilities with Exploit Frameworks: {len(exploitable_vulns)}")
        
        # Count by severity
        severity_counts = {}
        framework_counts = {}
        total_cves = set()
        cvss_v3_count = 0
        cvss_v2_count = 0
        
        for vuln in exploitable_vulns:
            severity = vuln['severity_name']
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Count CVSS versions
            if vuln.get('cvss_v3_score'):
                cvss_v3_count += 1
            elif vuln.get('cvss_v2_score'):
                cvss_v2_count += 1
            
            # Count frameworks
            for framework in vuln.get('exploit_frameworks', []):
                framework_name = framework.get('name', 'Unknown')
                framework_counts[framework_name] = framework_counts.get(framework_name, 0) + 1
            
            # Collect all CVEs
            for cve in vuln.get('cve_ids', []):
                total_cves.add(cve)
        
        for severity, count in sorted(severity_counts.items(), key=lambda x: ['INFO', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].index(x[0]), reverse=True):
            report.append(f"{severity}: {count}")
        
        report.append(f"With CVSS v3.0 Scores: {cvss_v3_count}")
        report.append(f"With CVSS v2.0 Scores: {cvss_v2_count}")
        report.append(f"Total Unique CVEs: {len(total_cves)}")
        report.append("")
        
        # Exploit frameworks summary
        if framework_counts:
            report.append("EXPLOIT FRAMEWORKS AVAILABLE")
            report.append("-" * 30)
            for framework, count in sorted(framework_counts.items(), key=lambda x: x[1], reverse=True):
                report.append(f"{framework}: {count} vulnerabilities")
            report.append("")
        
        # CVE information
        if total_cves:
            report.append("ASSOCIATED CVEs")
            report.append("-" * 15)
            sorted_cves = sorted(list(total_cves), reverse=True)
            for cve in sorted_cves[:15]:
                report.append(f"  * {cve}")
            if len(total_cves) > 15:
                report.append(f"  ... and {len(total_cves) - 15} more CVEs")
            report.append("")
        
        # Detailed vulnerabilities
        report.append("VULNERABILITIES WITH EXPLOIT FRAMEWORKS")
        report.append("=" * 60)
        
        for i, vuln in enumerate(exploitable_vulns, 1):
            # Header with CVSS score prominently displayed
            cvss_display = ""
            if vuln.get('cvss_v3_score'):
                cvss_display = f" | CVSS v3.0: {vuln['cvss_v3_score']}"
            elif vuln.get('cvss_v2_score'):
                cvss_display = f" | CVSS v2.0: {vuln['cvss_v2_score']}"
            
            cve_display = ""
            if vuln['cve_ids']:
                cve_display = f" | CVEs: {', '.join(vuln['cve_ids'])}"
            
            report.append(f"\n[{i}] {vuln['severity_name']} - {vuln['plugin_name']}{cvss_display}{cve_display}")
            report.append(f"Host: {vuln['host']} | Plugin ID: {vuln['plugin_id']}")
            
            # CVSS information
            if vuln.get('cvss_v3_score'):
                report.append(f"[CVSS v3.0] Score: {vuln['cvss_v3_score']}")
                if vuln.get('cvss_v3_vector'):
                    report.append(f"[CVSS v3.0] Vector: {vuln['cvss_v3_vector']}")
            elif vuln.get('cvss_v2_score'):
                report.append(f"[CVSS v2.0] Score: {vuln['cvss_v2_score']}")
                if vuln.get('cvss_v2_vector'):
                    report.append(f"[CVSS v2.0] Vector: {vuln['cvss_v2_vector']}")
            
            # CVE information
            if vuln['cve_ids']:
                report.append(f"[CVE] CVE IDs: {', '.join(vuln['cve_ids'])}")
                cve_links = []
                for cve in vuln['cve_ids']:
                    cve_links.append(f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve}")
                report.append(f"[INFO] CVE Details: {' | '.join(cve_links)}")
            
            # CPE Information
            if vuln.get('cpe'):
                report.append(f"[CPE] CPE: {', '.join(vuln['cpe'])}")
            
            # Exploit frameworks - detailed
            if vuln['exploit_frameworks']:
                report.append("[EXPLOIT FRAMEWORKS] Available frameworks:")
                for framework in vuln['exploit_frameworks']:
                    framework_name = framework.get('name', 'Unknown')
                    exploits = framework.get('exploits', [])
                    
                    if exploits:
                        report.append(f"  + {framework_name}:")
                        for exploit in exploits:
                            exploit_name = exploit.get('name', 'Unknown')
                            report.append(f"    - {exploit_name}")
                    else:
                        report.append(f"  + {framework_name}: Available")
            
            # Additional information
            if vuln.get('exploit_ease'):
                report.append(f"[EXPLOIT] Exploit Ease: {vuln['exploit_ease']}")
            
            if vuln.get('risk_factor'):
                report.append(f"[RISK] Risk Factor: {vuln['risk_factor']}")
            
            if vuln.get('unsupported_by_vendor'):
                report.append("[VENDOR] Unsupported by vendor: true")
            
            if vuln['in_the_news']:
                report.append("[NEWS] In the news: true")
            
            # Timeline information
            date_info = []
            if vuln['vuln_pub_date']:
                date_info.append(f"Vuln Published: {vuln['vuln_pub_date']}")
            if vuln['patch_date']:
                date_info.append(f"Patch Available: {vuln['patch_date']}")
            
            if date_info:
                report.append(f"[TIMELINE] Timeline: {' | '.join(date_info)}")
            
            if vuln['description']:
                report.append(f"[DESC] Description: {vuln['description']}")
            
            if vuln['solution']:
                report.append(f"[SOLUTION] Solution: {vuln['solution']}")
            
            report.append("-" * 60)
        
        # Metasploit specific section
        metasploit_vulns = [v for v in exploitable_vulns 
                           if any(f.get('name', '').lower() == 'metasploit' for f in v.get('exploit_frameworks', []))]
        if metasploit_vulns:
            report.append("\nMETASPLOIT EXPLOITATION TARGETS")
            report.append("=" * 40)
            for vuln in metasploit_vulns:
                cvss_info = f" (CVSS: {vuln.get('cvss_v3_score') or vuln.get('cvss_v2_score', 'N/A')})"
                cve_info = f" | CVEs: {', '.join(vuln['cve_ids'])}" if vuln['cve_ids'] else ""
                
                report.append(f"Target: {vuln['host']} - {vuln['plugin_name']}{cvss_info}{cve_info}")
                
                # Show specific Metasploit exploits
                for framework in vuln.get('exploit_frameworks', []):
                    if framework.get('name', '').lower() == 'metasploit':
                        for exploit in framework.get('exploits', []):
                            exploit_name = exploit.get('name', '')
                            if exploit_name and exploit_name != 'Available':
                                report.append(f"  Metasploit Exploit: {exploit_name}")
                                # Generate search commands
                                search_terms = exploit_name.split()[:3]
                                report.append(f"  # search {' '.join(search_terms)}")
                
                # Generic search commands
                search_terms = vuln['plugin_name'].split()[:3]
                report.append(f"  # search {' '.join(search_terms)}")
                report.append(f"  # set RHOSTS {vuln['host']}")
                if vuln['cve_ids']:
                    report.append(f"  # search cve:{vuln['cve_ids'][0]}")
                report.append("")
        
        return "\n".join(report)
    
    def generate_metasploit_resource_script(self, exploitable_vulns: Optional[List[Dict]] = None, filename: str = None) -> str:
        """
        Generate Metasploit resource script for vulnerabilities with exploit frameworks.
        
        Args:
            exploitable_vulns: List of vulnerabilities with exploit frameworks
            filename: Output filename (if None, will generate default name)
            
        Returns:
            Resource script content
        """
        if not exploitable_vulns:
            exploitable_vulns = self.exploitable_vulns
            
        if not exploitable_vulns:
            return "# No vulnerabilities with exploit frameworks found"
        
        # Get Metasploit specific vulnerabilities
        metasploit_vulns = [v for v in exploitable_vulns 
                           if any(f.get('name', '').lower() == 'metasploit' for f in v.get('exploit_frameworks', []))]
        
        # Get unique hosts and CVEs
        hosts = list(set([vuln['host'] for vuln in metasploit_vulns]))
        all_cves = set()
        for vuln in metasploit_vulns:
            all_cves.update(vuln.get('cve_ids', []))
        
        script_lines = [
            "# Metasploit Resource Script for Exploit Framework Vulnerabilities",
            "# Generated from Nessus raw scan data",
            f"# Total vulnerabilities with Metasploit exploits: {len(metasploit_vulns)}",
            f"# Target hosts: {', '.join(hosts)}",
            f"# Associated CVEs: {', '.join(sorted(all_cves, reverse=True)[:10])}{'...' if len(all_cves) > 10 else ''}",
            "",
            "# Set global options",
            "setg VERBOSE true",
            ""
        ]
        
        for vuln in metasploit_vulns:
            cvss_score = vuln.get('cvss_v3_score') or vuln.get('cvss_v2_score', 'N/A')
            cve_info = f" | CVEs: {', '.join(vuln['cve_ids'])}" if vuln['cve_ids'] else ""
            
            script_lines.extend([
                f"# {vuln['severity_name']} - {vuln['plugin_name']}{cve_info}",
                f"# Host: {vuln['host']} | Plugin ID: {vuln['plugin_id']}",
                f"# CVSS Score: {cvss_score}",
                ""
            ])
            
            # Add specific Metasploit exploit information
            for framework in vuln.get('exploit_frameworks', []):
                if framework.get('name', '').lower() == 'metasploit':
                    for exploit in framework.get('exploits', []):
                        exploit_name = exploit.get('name', '')
                        if exploit_name and exploit_name != 'Available':
                            script_lines.extend([
                                f"# Specific Metasploit Exploit: {exploit_name}",
                                f"search {' '.join(exploit_name.split()[:3])}",
                                ""
                            ])
            
            # Add CVE research links
            if vuln['cve_ids']:
                script_lines.extend([
                    "# CVE Research Links:",
                ])
                for cve in vuln['cve_ids']:
                    script_lines.extend([
                        f"# {cve}: https://cve.mitre.org/cgi-bin/cvename.cgi?name={cve}",
                        f"# {cve}: https://nvd.nist.gov/vuln/detail/{cve}",
                    ])
                script_lines.append("")
            
            # Generate search commands
            search_terms = vuln['plugin_name'].split()[:3]
            script_lines.extend([
                f"search {' '.join(search_terms)}",
                "# Review search results and select appropriate module",
                f"# search cve:{vuln['cve_ids'][0]}" if vuln['cve_ids'] else "# search type:exploit",
                "# use <module_path>",
                f"# set RHOSTS {vuln['host']}",
                "# set LHOST <your_ip>",
                "# exploit",
                ""
            ])
        
        script_content = "\n".join(script_lines)
        
        # Save to file if filename provided
        if filename:
            try:
                with open(filename, 'w') as f:
                    f.write(script_content)
                print(f"[+] Metasploit resource script saved to {filename}")
            except Exception as e:
                print(f"[!] Error saving Metasploit script: {e}")
        
        return script_content
    
    def save_results(self, report: str, target_identifier: str, output_dir: str = "nessus_analysis") -> Dict[str, str]:
        """
        Save analysis results to files organized by host.
        
        Args:
            report: Report content
            target_identifier: Target identifier for filenames
            output_dir: Output directory
            
        Returns:
            Dictionary of saved file paths
        """
        try:
            # Create main output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Group vulnerabilities by host
            hosts_data = {}
            for vuln in self.exploitable_vulns:
                host_ip = vuln.get('host', 'unknown')
                if host_ip not in hosts_data:
                    hosts_data[host_ip] = []
                hosts_data[host_ip].append(vuln)
            
            saved_files = {}
            
            # Create separate files for each host
            for host_ip, host_vulns in hosts_data.items():
                # Extract box name from the raw data filename
                box_name = self.extract_computer_name(None)
                host_output_dir = os.path.join(output_dir, box_name)
                os.makedirs(host_output_dir, exist_ok=True)
                
                # Generate host-specific report
                host_report = self.generate_exploit_framework_report(host_vulns)
                
                # Extract box name from filename and use it in file naming
                file_identifier = f"{box_name}_{host_ip.replace('.', '_')}_{timestamp}"
                
                # Save host-specific files with box name in filename
                report_filename = f"{file_identifier}.txt"
                report_filepath = os.path.join(host_output_dir, report_filename)
                
                with open(report_filepath, 'w', encoding='utf-8') as f:
                    f.write(host_report)
                
                # Save Metasploit script for this host
                msf_filename = f"{file_identifier}.rc"
                msf_filepath = os.path.join(host_output_dir, msf_filename)
                
                msf_script = self.generate_metasploit_resource_script(host_vulns, msf_filepath)
                
                # Save exploit framework vulnerabilities as JSON for this host
                json_filename = f"{file_identifier}.json"
                json_filepath = os.path.join(host_output_dir, json_filename)
                
                with open(json_filepath, 'w', encoding='utf-8') as f:
                    json.dump(host_vulns, f, indent=2, ensure_ascii=False)
                
                # Store file paths
                saved_files[host_ip] = {
                    'report': report_filepath,
                    'metasploit': msf_filepath,
                    'json': json_filepath,
                    'folder': host_output_dir
                }
                
                print(f"[+] Analysis results for {host_ip} saved to {host_output_dir}/")
            
            # Also save a combined report in the main directory for overview
            if len(hosts_data) > 1:
                combined_file_identifier = f"combined_{timestamp}"
                combined_report_filename = f"{combined_file_identifier}.txt"
                combined_report_filepath = os.path.join(output_dir, combined_report_filename)
                
                with open(combined_report_filepath, 'w', encoding='utf-8') as f:
                    f.write(report)
                
                saved_files['combined'] = {
                    'report': combined_report_filepath
                }
                print(f"[+] Combined analysis report saved to {combined_report_filepath}")
            
            return saved_files
            
        except Exception as e:
            print(f"[!] Error saving results: {e}")
            return {}
    
    def analyze_raw_data(self, output_dir: str = "nessus_analysis") -> Dict[str, str]:
        """
        Complete analysis workflow: filter vulnerabilities and generate reports.
        
        Args:
            output_dir: Output directory for analysis results
            
        Returns:
            Dictionary of saved file paths
        """
        print("[ANALYSIS] Starting exploit framework vulnerability analysis...")
        
        # Filter for vulnerabilities with exploit frameworks
        exploitable_vulns = self.filter_vulnerabilities_with_exploits()
        
        if exploitable_vulns:
            # Generate report
            report = self.generate_exploit_framework_report(exploitable_vulns)
            print("\n" + report)
            
            # Extract target identifier from scan info
            scan_info = self.raw_data.get('scan_info', {})
            target = scan_info.get('targets', 'unknown').replace('.', '_').replace(',', '_')
            
            # Save results
            saved_files = self.save_results(report, target, output_dir)
            
            return saved_files
        else:
            print("\n[SUCCESS] ANALYSIS COMPLETED - No vulnerabilities with exploit frameworks found")
            print("This could indicate that the target is well-patched or the scan didn't find exploitable services.")
            return {}

    def extract_computer_name(self, host_data: Dict) -> str:
        """
        Extract the box name from the raw data filename.
        
        Args:
            host_data: Host information from raw scan data (not used in this implementation)
            
        Returns:
            Box name extracted from the raw data filename
        """
        try:
            # Extract box name from the raw data filename
            # Format: boxname_ip_timestamp.json -> extract "boxname"
            filename = os.path.basename(self.raw_data_file)
            
            # Remove .json extension
            if filename.endswith('.json'):
                filename = filename[:-5]
            
            # Split by underscore and take the first part as box name
            parts = filename.split('_')
            if len(parts) > 0:
                box_name = parts[0]
                return box_name
            
            # Fallback to 'unknown' if parsing fails
            return 'unknown'
            
        except Exception as e:
            print(f"[!] Error extracting box name from filename: {e}")
            return 'unknown'


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Nessus Exploit Framework Analysis - Find vulnerabilities with exploit frameworks sorted by CVSS v3.0")
    parser.add_argument("raw_data_file", help="Path to raw Nessus scan data JSON file")
    parser.add_argument("--output-dir", default="nessus_analysis", 
                       help="Output directory for analysis results (default: nessus_analysis)")
    
    args = parser.parse_args()
    
    print("Nessus Exploit Framework Parser")
    print("=" * 40)
    print(f"Input File: {args.raw_data_file}")
    print(f"Output Directory: {args.output_dir}")
    print("=" * 40)
    
    try:
        # Initialize parser
        parser = NessusExploitParser(args.raw_data_file)
        
        # Perform analysis
        saved_files = parser.analyze_raw_data(args.output_dir)
        
        if saved_files:
            print(f"\n[SUCCESS] Analysis completed successfully!")
            print(f"[FILES] Generated files:")
            for file_type, filepath in saved_files.items():
                print(f"  - {file_type.title()}: {filepath}")
        else:
            print(f"\n[INFO] No vulnerabilities with exploit frameworks found in the scan data.")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 