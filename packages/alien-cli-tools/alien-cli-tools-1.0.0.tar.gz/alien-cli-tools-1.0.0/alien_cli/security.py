#!/usr/bin/env python3
"""
🛡️ Alien Security - Real Security Analysis Tool
==============================================

Real security analysis and monitoring tools:
- Port scanning and network analysis
- File integrity monitoring
- Password strength analysis
- System vulnerability assessment
- Security audit reports

Usage:
    alien-security scan <target>    - Network security scan
    alien-security audit           - System security audit
    alien-security password       - Password strength checker
    alien-security monitor        - File integrity monitoring
    alien-security report         - Generate security report
"""

import sys
import os
import argparse
import socket
import hashlib
import re
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class SecurityAnalyzer:
    def __init__(self):
        self.scan_results = {}
        self.audit_results = {}
    
    def port_scan(self, target: str, ports: List[int] = None) -> Dict[str, Any]:
        """Perform basic port scan on target"""
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 443, 993, 995, 3389, 5432, 3306]
        
        try:
            # Resolve hostname
            target_ip = socket.gethostbyname(target)
            
            open_ports = []
            closed_ports = []
            
            print(f"🔍 Scanning {target} ({target_ip})...")
            
            for port in ports:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                
                result = sock.connect_ex((target_ip, port))
                
                if result == 0:
                    open_ports.append(port)
                    print(f"   ✅ Port {port}: Open")
                else:
                    closed_ports.append(port)
                
                sock.close()
            
            # Analyze open ports for security risks
            security_risks = []
            for port in open_ports:
                risk = self.analyze_port_risk(port)
                if risk:
                    security_risks.append(risk)
            
            return {
                "target": target,
                "target_ip": target_ip,
                "open_ports": open_ports,
                "closed_ports": closed_ports,
                "security_risks": security_risks,
                "scan_time": datetime.now().isoformat()
            }
        
        except socket.gaierror:
            return {"error": f"Could not resolve hostname: {target}"}
        except Exception as e:
            return {"error": f"Scan error: {str(e)}"}
    
    def analyze_port_risk(self, port: int) -> Optional[Dict[str, str]]:
        """Analyze security risk for specific port"""
        port_risks = {
            21: {"service": "FTP", "risk": "High", "reason": "Unencrypted file transfer"},
            22: {"service": "SSH", "risk": "Medium", "reason": "Secure but common attack target"},
            23: {"service": "Telnet", "risk": "Critical", "reason": "Unencrypted remote access"},
            25: {"service": "SMTP", "risk": "Medium", "reason": "Email server - potential spam relay"},
            53: {"service": "DNS", "risk": "Low", "reason": "DNS service - generally safe"},
            80: {"service": "HTTP", "risk": "Medium", "reason": "Unencrypted web traffic"},
            110: {"service": "POP3", "risk": "High", "reason": "Unencrypted email retrieval"},
            443: {"service": "HTTPS", "risk": "Low", "reason": "Encrypted web traffic"},
            993: {"service": "IMAPS", "risk": "Low", "reason": "Encrypted email access"},
            995: {"service": "POP3S", "risk": "Low", "reason": "Encrypted email retrieval"},
            3389: {"service": "RDP", "risk": "High", "reason": "Remote desktop - common attack vector"},
            5432: {"service": "PostgreSQL", "risk": "High", "reason": "Database exposed to network"},
            3306: {"service": "MySQL", "risk": "High", "reason": "Database exposed to network"}
        }
        
        return port_risks.get(port)
    
    def system_audit(self) -> Dict[str, Any]:
        """Perform basic system security audit"""
        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Check file permissions
        audit_results["checks"]["file_permissions"] = self.check_file_permissions()
        
        # Check for common security files
        audit_results["checks"]["security_files"] = self.check_security_files()
        
        # Check system updates (if possible)
        audit_results["checks"]["system_updates"] = self.check_system_updates()
        
        # Check running services
        audit_results["checks"]["running_services"] = self.check_running_services()
        
        # Calculate overall security score
        audit_results["security_score"] = self.calculate_security_score(audit_results["checks"])
        
        return audit_results
    
    def check_file_permissions(self) -> Dict[str, Any]:
        """Check critical file permissions"""
        critical_files = [
            "/etc/passwd",
            "/etc/shadow",
            "/etc/sudoers",
            "~/.ssh/id_rsa",
            "~/.ssh/authorized_keys"
        ]
        
        results = {"status": "checked", "issues": []}
        
        for file_path in critical_files:
            expanded_path = os.path.expanduser(file_path)
            if os.path.exists(expanded_path):
                try:
                    stat_info = os.stat(expanded_path)
                    permissions = oct(stat_info.st_mode)[-3:]
                    
                    # Check for overly permissive permissions
                    if file_path in ["/etc/shadow", "~/.ssh/id_rsa"] and permissions != "600":
                        results["issues"].append({
                            "file": file_path,
                            "current_permissions": permissions,
                            "recommended": "600",
                            "severity": "high"
                        })
                    elif file_path == "/etc/passwd" and permissions not in ["644", "640"]:
                        results["issues"].append({
                            "file": file_path,
                            "current_permissions": permissions,
                            "recommended": "644",
                            "severity": "medium"
                        })
                except OSError:
                    results["issues"].append({
                        "file": file_path,
                        "error": "Cannot check permissions",
                        "severity": "low"
                    })
        
        return results
    
    def check_security_files(self) -> Dict[str, Any]:
        """Check for presence of security-related files"""
        security_files = {
            "~/.ssh/authorized_keys": "SSH authorized keys",
            "~/.bash_history": "Command history",
            "/etc/hosts.deny": "Host access control",
            "/etc/hosts.allow": "Host access control"
        }
        
        results = {"status": "checked", "found_files": [], "missing_files": []}
        
        for file_path, description in security_files.items():
            expanded_path = os.path.expanduser(file_path)
            if os.path.exists(expanded_path):
                results["found_files"].append({
                    "file": file_path,
                    "description": description,
                    "size": os.path.getsize(expanded_path)
                })
            else:
                results["missing_files"].append({
                    "file": file_path,
                    "description": description
                })
        
        return results
    
    def check_system_updates(self) -> Dict[str, Any]:
        """Check for available system updates"""
        results = {"status": "checked", "updates_available": False, "details": ""}
        
        try:
            # Try different package managers
            if os.path.exists("/usr/bin/apt"):
                # Debian/Ubuntu
                result = subprocess.run(["apt", "list", "--upgradable"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    upgradable = len([line for line in result.stdout.split('\\n') if 'upgradable' in line])
                    results["updates_available"] = upgradable > 1  # Exclude header
                    results["details"] = f"{upgradable-1} packages can be upgraded" if upgradable > 1 else "System up to date"
            
            elif os.path.exists("/usr/bin/yum"):
                # RedHat/CentOS
                result = subprocess.run(["yum", "check-update"], 
                                      capture_output=True, text=True, timeout=10)
                results["updates_available"] = result.returncode != 0
                results["details"] = "Updates available" if result.returncode != 0 else "System up to date"
            
            else:
                results["details"] = "Package manager not detected"
        
        except subprocess.TimeoutExpired:
            results["details"] = "Update check timed out"
        except Exception as e:
            results["details"] = f"Error checking updates: {str(e)}"
        
        return results
    
    def check_running_services(self) -> Dict[str, Any]:
        """Check running services for security implications"""
        results = {"status": "checked", "services": [], "security_concerns": []}
        
        try:
            # Try to get running services
            if os.path.exists("/bin/systemctl"):
                result = subprocess.run(["systemctl", "list-units", "--type=service", "--state=running"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.split('\\n')
                    for line in lines:
                        if '.service' in line and 'running' in line:
                            service_name = line.split()[0].replace('.service', '')
                            results["services"].append(service_name)
                            
                            # Check for potentially risky services
                            if service_name in ['telnet', 'ftp', 'rsh', 'rlogin']:
                                results["security_concerns"].append({
                                    "service": service_name,
                                    "risk": "high",
                                    "reason": "Unencrypted protocol"
                                })
        
        except Exception as e:
            results["details"] = f"Error checking services: {str(e)}"
        
        return results
    
    def calculate_security_score(self, checks: Dict[str, Any]) -> int:
        """Calculate overall security score based on audit results"""
        score = 100
        
        # Deduct points for file permission issues
        if "file_permissions" in checks:
            high_issues = len([issue for issue in checks["file_permissions"].get("issues", []) 
                             if issue.get("severity") == "high"])
            medium_issues = len([issue for issue in checks["file_permissions"].get("issues", []) 
                               if issue.get("severity") == "medium"])
            score -= (high_issues * 20 + medium_issues * 10)
        
        # Deduct points for security concerns
        if "running_services" in checks:
            security_concerns = len(checks["running_services"].get("security_concerns", []))
            score -= (security_concerns * 15)
        
        # Deduct points for missing updates
        if "system_updates" in checks:
            if checks["system_updates"].get("updates_available", False):
                score -= 10
        
        return max(0, score)
    
    def password_strength(self, password: str) -> Dict[str, Any]:
        """Analyze password strength"""
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 12:
            score += 25
        elif len(password) >= 8:
            score += 15
            feedback.append("Consider using a longer password (12+ characters)")
        else:
            feedback.append("Password too short - use at least 8 characters")
        
        # Character variety
        if re.search(r'[a-z]', password):
            score += 10
        else:
            feedback.append("Add lowercase letters")
        
        if re.search(r'[A-Z]', password):
            score += 10
        else:
            feedback.append("Add uppercase letters")
        
        if re.search(r'\\d', password):
            score += 10
        else:
            feedback.append("Add numbers")
        
        if re.search(r'[!@#$%^&*(),.?\":{}|<>]', password):
            score += 15
        else:
            feedback.append("Add special characters")
        
        # Pattern checks
        if not re.search(r'(.)\\1{2,}', password):  # No 3+ repeated characters
            score += 10
        else:
            feedback.append("Avoid repeating characters")
        
        if not re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde)', password.lower()):
            score += 10
        else:
            feedback.append("Avoid sequential characters")
        
        # Common password check
        common_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if password.lower() not in common_passwords:
            score += 10
        else:
            feedback.append("Avoid common passwords")
            score = min(score, 20)  # Cap score for common passwords
        
        # Determine strength level
        if score >= 80:
            strength = "Very Strong"
        elif score >= 60:
            strength = "Strong"
        elif score >= 40:
            strength = "Medium"
        elif score >= 20:
            strength = "Weak"
        else:
            strength = "Very Weak"
        
        return {
            "score": score,
            "strength": strength,
            "feedback": feedback,
            "length": len(password)
        }
    
    def file_integrity_check(self, directory: str) -> Dict[str, Any]:
        """Basic file integrity monitoring"""
        results = {
            "directory": directory,
            "files_checked": 0,
            "checksums": {},
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'rb') as f:
                            file_hash = hashlib.sha256(f.read()).hexdigest()
                            results["checksums"][file_path] = file_hash
                            results["files_checked"] += 1
                    except (PermissionError, OSError):
                        continue
        
        except Exception as e:
            results["error"] = str(e)
        
        return results

def main():
    parser = argparse.ArgumentParser(description="🛡️ Alien Security - Real Security Analysis Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Network security scan')
    scan_parser.add_argument('target', help='Target hostname or IP address')
    scan_parser.add_argument('--ports', nargs='+', type=int, help='Specific ports to scan')
    
    # Audit command
    audit_parser = subparsers.add_parser('audit', help='System security audit')
    
    # Password command
    password_parser = subparsers.add_parser('password', help='Password strength checker')
    password_parser.add_argument('password', nargs='?', help='Password to check (will prompt if not provided)')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='File integrity monitoring')
    monitor_parser.add_argument('directory', help='Directory to monitor')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate security report')
    report_parser.add_argument('--output', help='Output file for report')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🛡️ Alien Security - Real Security Analysis Tool")
    print("=" * 50)
    
    analyzer = SecurityAnalyzer()
    
    if args.command == 'scan':
        result = analyzer.port_scan(args.target, args.ports)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"🔍 Scan Results for {result['target']} ({result['target_ip']}):")
            print(f"   Open Ports: {', '.join(map(str, result['open_ports'])) if result['open_ports'] else 'None'}")
            
            if result['security_risks']:
                print("\\n⚠️ Security Risks:")
                for risk in result['security_risks']:
                    risk_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(risk['risk'], "❓")
                    print(f"   {risk_icon} Port {list(result['open_ports'])[result['security_risks'].index(risk)]}: {risk['service']} - {risk['reason']}")
    
    elif args.command == 'audit':
        result = analyzer.system_audit()
        print(f"🔒 System Security Audit:")
        print(f"   Security Score: {result['security_score']}/100")
        
        # File permissions
        perm_issues = result['checks']['file_permissions']['issues']
        if perm_issues:
            print(f"\\n⚠️ File Permission Issues ({len(perm_issues)}):")
            for issue in perm_issues:
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(issue.get('severity'), "❓")
                print(f"   {severity_icon} {issue['file']}: {issue.get('current_permissions', 'unknown')} (recommended: {issue.get('recommended', 'N/A')})")
        
        # Security concerns
        security_concerns = result['checks']['running_services'].get('security_concerns', [])
        if security_concerns:
            print(f"\\n🚨 Service Security Concerns ({len(security_concerns)}):")
            for concern in security_concerns:
                print(f"   🔴 {concern['service']}: {concern['reason']}")
        
        # Updates
        updates = result['checks']['system_updates']
        update_icon = "🟡" if updates.get('updates_available') else "🟢"
        print(f"\\n{update_icon} System Updates: {updates['details']}")
    
    elif args.command == 'password':
        if args.password:
            password = args.password
        else:
            import getpass
            password = getpass.getpass("Enter password to analyze: ")
        
        result = analyzer.password_strength(password)
        strength_icons = {"Very Strong": "🟢", "Strong": "🟢", "Medium": "🟡", "Weak": "🟠", "Very Weak": "🔴"}
        strength_icon = strength_icons.get(result['strength'], "❓")
        
        print(f"🔐 Password Strength Analysis:")
        print(f"   Strength: {strength_icon} {result['strength']} (Score: {result['score']}/100)")
        print(f"   Length: {result['length']} characters")
        
        if result['feedback']:
            print("\\n💡 Recommendations:")
            for feedback in result['feedback']:
                print(f"   • {feedback}")
    
    elif args.command == 'monitor':
        result = analyzer.file_integrity_check(args.directory)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"📁 File Integrity Check for {result['directory']}:")
            print(f"   Files Checked: {result['files_checked']}")
            print(f"   Checksums Generated: {len(result['checksums'])}")
            print(f"   Timestamp: {result['timestamp']}")
            print("\\n💡 Checksums saved for future comparison")
    
    elif args.command == 'report':
        # Generate comprehensive security report
        print("📊 Generating comprehensive security report...")
        
        # Perform all checks
        audit_result = analyzer.system_audit()
        
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "security_score": audit_result['security_score'],
            "audit_results": audit_result,
            "recommendations": []
        }
        
        # Generate recommendations
        if audit_result['security_score'] < 70:
            report['recommendations'].append("System security needs improvement")
        if audit_result['checks']['file_permissions']['issues']:
            report['recommendations'].append("Fix file permission issues")
        if audit_result['checks']['system_updates'].get('updates_available'):
            report['recommendations'].append("Install available system updates")
        
        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"📄 Report saved to: {args.output}")
        else:
            print("📄 Security Report:")
            print(f"   Overall Score: {report['security_score']}/100")
            print(f"   Recommendations: {len(report['recommendations'])}")
            for rec in report['recommendations']:
                print(f"   • {rec}")

if __name__ == "__main__":
    main()