#!/usr/bin/env python3
"""
Nessus Scanner Example Script

This script demonstrates various ways to use the NessusExecutor class
for vulnerability scanning and analysis.

Usage:
    python nessus_example.py <target_ip>

Example:
    python nessus_example.py 192.168.1.100
"""

import sys
import time
import argparse
from datetime import datetime
from attack_executor.scan.nessus import NessusExecutor


def example_quick_scan(target_ip):
    """
    Example 1: Simple quick scan
    """
    print(f"\n=== Example 1: Quick Scan of {target_ip} ===")
    
    # Initialize scanner
    nessus = NessusExecutor()
    
    # Perform quick scan
    results = nessus.quick_scan(target_ip, wait_for_completion=True, generate_report=True)
    
    if results:
        print(f"\n✓ Scan completed successfully!")
        print(f"  - Hosts scanned: {results['host_count']}")
        print(f"  - Total vulnerabilities: {results['vulnerability_count']}")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = f"nessus_scan_{target_ip}_{timestamp}.json"
        report_file = f"nessus_report_{target_ip}_{timestamp}.txt"
        
        if nessus.last_scan_results:
            nessus.save_results_to_file(json_file, nessus.last_scan_results, "json")
        
        report = nessus.generate_summary_report(results)
        nessus.save_results_to_file(report_file, report, "txt")
        
        print(f"  - Results saved to: {json_file}")
        print(f"  - Report saved to: {report_file}")
    else:
        print("✗ Scan failed or incomplete")


def example_step_by_step_scan(target_ip):
    """
    Example 2: Step-by-step scan with monitoring
    """
    print(f"\n=== Example 2: Step-by-Step Scan of {target_ip} ===")
    
    nessus = NessusExecutor()
    
    # Step 1: Launch scan
    print("Step 1: Launching scan...")
    scan_id = nessus.scan_target(target_ip, scan_name=f"Example_Scan_{target_ip}")
    
    if not scan_id:
        print("✗ Failed to launch scan")
        return
    
    print(f"✓ Scan launched with ID: {scan_id}")
    
    # Step 2: Monitor progress
    print("Step 2: Monitoring scan progress...")
    start_time = time.time()
    
    while True:
        status = nessus.get_scan_status(scan_id)
        elapsed = int(time.time() - start_time)
        
        if status and "completed" in status.lower():
            print(f"✓ Scan completed after {elapsed} seconds")
            break
        elif status and "failed" in status.lower():
            print(f"✗ Scan failed after {elapsed} seconds")
            return
        else:
            print(f"  Status: {status} (elapsed: {elapsed}s)")
            time.sleep(30)  # Check every 30 seconds
        
        # Safety timeout
        if elapsed > 3600:  # 1 hour
            print("✗ Scan timeout after 1 hour")
            return
    
    # Step 3: Get results
    print("Step 3: Retrieving scan results...")
    results = nessus.get_scan_results(scan_id, format_type="json")
    
    if not results:
        print("✗ Failed to retrieve results")
        return
    
    print("✓ Results retrieved successfully")
    
    # Step 4: Parse and analyze
    print("Step 4: Parsing and analyzing results...")
    parsed_results = nessus.parse_json_results(results)
    
    if parsed_results:
        print("✓ Results parsed successfully")
        analyze_vulnerabilities(parsed_results)
    else:
        print("✗ Failed to parse results")


def example_policy_management(target_ip):
    """
    Example 3: Policy management and custom scanning
    """
    print(f"\n=== Example 3: Policy Management ===")
    
    nessus = NessusExecutor()
    
    # List existing policies
    print("Current scan policies:")
    policies = nessus.list_policies()
    
    if policies:
        for policy in policies:
            print(f"  - {policy['name']} (ID: {policy['id']})")
    else:
        print("  No policies found or unable to retrieve")
    
    # Create a custom policy
    custom_policy = "Custom_Web_Scan_Policy"
    print(f"\nCreating custom policy: {custom_policy}")
    
    if nessus.create_basic_scan_policy(custom_policy):
        print("✓ Custom policy created successfully")
        
        # Use custom policy for scanning
        print(f"Scanning {target_ip} with custom policy...")
        scan_id = nessus.scan_target(target_ip, policy_name=custom_policy)
        
        if scan_id:
            print(f"✓ Scan launched with custom policy (ID: {scan_id})")
        else:
            print("✗ Failed to launch scan with custom policy")
    else:
        print("✗ Failed to create custom policy")


def example_batch_scanning():
    """
    Example 4: Batch scanning multiple targets
    """
    print(f"\n=== Example 4: Batch Scanning ===")
    
    # Example targets (use your own targets)
    targets = ["192.168.1.100", "192.168.1.101", "192.168.1.102"]
    
    nessus = NessusExecutor()
    scan_jobs = []
    
    print(f"Launching scans for {len(targets)} targets...")
    
    # Launch all scans
    for target in targets:
        scan_id = nessus.scan_target(target, scan_name=f"Batch_Scan_{target}")
        if scan_id:
            scan_jobs.append((target, scan_id))
            print(f"✓ Scan launched for {target} (ID: {scan_id})")
        else:
            print(f"✗ Failed to launch scan for {target}")
    
    if not scan_jobs:
        print("No scans were launched successfully")
        return
    
    # Monitor all scans
    print(f"\nMonitoring {len(scan_jobs)} scans...")
    completed_scans = []
    
    while scan_jobs:
        for target, scan_id in scan_jobs[:]:  # Copy list to avoid modification during iteration
            status = nessus.get_scan_status(scan_id)
            
            if status and "completed" in status.lower():
                print(f"✓ Scan completed for {target}")
                completed_scans.append((target, scan_id))
                scan_jobs.remove((target, scan_id))
            elif status and "failed" in status.lower():
                print(f"✗ Scan failed for {target}")
                scan_jobs.remove((target, scan_id))
        
        if scan_jobs:
            print(f"  Still waiting for {len(scan_jobs)} scans...")
            time.sleep(60)  # Check every minute
    
    # Process completed scans
    print(f"\nProcessing {len(completed_scans)} completed scans...")
    
    for target, scan_id in completed_scans:
        results = nessus.get_scan_results(scan_id)
        if results:
            filename = f"batch_scan_{target}.json"
            nessus.save_results_to_file(filename, results)
            print(f"✓ Results saved for {target}: {filename}")


def analyze_vulnerabilities(parsed_results):
    """
    Analyze and display vulnerability statistics
    """
    print("\n--- Vulnerability Analysis ---")
    
    if not parsed_results or not parsed_results.get('vulnerabilities'):
        print("No vulnerabilities to analyze")
        return
    
    vulnerabilities = parsed_results['vulnerabilities']
    
    # Count by severity
    severity_counts = {4: 0, 3: 0, 2: 0, 1: 0, 0: 0}
    severity_names = {4: "Critical", 3: "High", 2: "Medium", 1: "Low", 0: "Info"}
    
    for vuln in vulnerabilities:
        severity = vuln.get('severity', 0)
        severity_counts[severity] += 1
    
    print("Vulnerability counts by severity:")
    for severity, count in severity_counts.items():
        if count > 0:
            print(f"  {severity_names[severity]}: {count}")
    
    # Show top critical and high vulnerabilities
    critical_and_high = [v for v in vulnerabilities if v.get('severity', 0) >= 3]
    
    if critical_and_high:
        print(f"\nTop Critical/High vulnerabilities:")
        for vuln in critical_and_high[:5]:  # Show top 5
            severity_name = severity_names.get(vuln.get('severity', 0), "Unknown")
            print(f"  [{severity_name}] {vuln.get('plugin_name', 'Unknown')}")
            print(f"    Host: {vuln.get('host', 'Unknown')}")
            print(f"    Plugin ID: {vuln.get('plugin_id', 'Unknown')}")
    
    # Host analysis
    hosts = parsed_results.get('hosts', [])
    if hosts:
        print(f"\nHost analysis:")
        for host in hosts:
            total_vulns = (host.get('critical_vulns', 0) + 
                          host.get('high_vulns', 0) + 
                          host.get('medium_vulns', 0) + 
                          host.get('low_vulns', 0))
            print(f"  {host.get('ip', 'Unknown')}: {total_vulns} total vulnerabilities")
            print(f"    Critical: {host.get('critical_vulns', 0)}, "
                  f"High: {host.get('high_vulns', 0)}, "
                  f"Medium: {host.get('medium_vulns', 0)}, "
                  f"Low: {host.get('low_vulns', 0)}")


def main():
    """
    Main function with argument parsing
    """
    parser = argparse.ArgumentParser(description="Nessus Scanner Examples")
    parser.add_argument("target", help="Target IP address to scan")
    parser.add_argument("--example", "-e", type=int, choices=[1, 2, 3, 4], 
                       help="Run specific example (1-4)")
    parser.add_argument("--all", "-a", action="store_true", 
                       help="Run all examples")
    
    args = parser.parse_args()
    
    target_ip = args.target
    
    print(f"Nessus Scanner Examples - Target: {target_ip}")
    print("=" * 50)
    
    # Validate target format (basic check)
    if not target_ip.replace('.', '').replace(':', '').replace('-', '').replace('_', '').isalnum():
        print("Warning: Target IP format might be invalid")
    
    try:
        if args.all:
            # Run all examples
            example_quick_scan(target_ip)
            example_step_by_step_scan(target_ip)
            example_policy_management(target_ip)
            example_batch_scanning()
        elif args.example:
            # Run specific example
            if args.example == 1:
                example_quick_scan(target_ip)
            elif args.example == 2:
                example_step_by_step_scan(target_ip)
            elif args.example == 3:
                example_policy_management(target_ip)
            elif args.example == 4:
                example_batch_scanning()
        else:
            # Default: run quick scan
            example_quick_scan(target_ip)
    
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    print("\n" + "=" * 50)
    print("Examples completed")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 