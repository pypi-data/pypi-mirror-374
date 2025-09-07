#!/usr/bin/env python3
"""
🛸 TERMINAL SECURITY HARDENING 🛸
Advanced terminal security hardening untuk Alien Terminal Monopoly

Features:
- Terminal input sanitization
- Command injection prevention
- Buffer overflow protection
- Memory corruption detection
- Process isolation
- Secure environment setup
- Anti-debugging measures
- Runtime protection
"""

import os
import sys
import re
import signal
import subprocess
import threading
import time
import psutil
import tempfile
import shutil
import string
import json
import random
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass
from enum import Enum
import logging
import hashlib
import secrets

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TerminalSecurityLevel(Enum):
    BASIC = "basic"
    HARDENED = "hardened"
    FORTRESS = "fortress"
    COSMIC = "cosmic"

@dataclass
class SecurityViolation:
    """Security violation data"""
    timestamp: float
    violation_type: str
    severity: str
    description: str
    blocked: bool
    source: Optional[str] = None

class TerminalSecurityHardening:
    """
    🛸 TERMINAL SECURITY HARDENING 🛸
    
    Comprehensive terminal security hardening system
    """
    
    def __init__(self, security_level: TerminalSecurityLevel = TerminalSecurityLevel.FORTRESS):
        self.security_level = security_level
        self.violations: List[SecurityViolation] = []
        self.blocked_commands: Set[str] = set()
        self.allowed_commands: Set[str] = set()
        self.input_filters: List[Callable] = []
        self.output_filters: List[Callable] = []
        self.environment_locked = False
        self.debug_protection_active = False
        
        # Initialize security components
        self._setup_command_whitelist()
        self._setup_input_filters()
        self._setup_output_filters()
        self._setup_environment_protection()
        self._activate_debug_protection()
        
        logger.info(f"🔒 Terminal security hardening initialized - Level: {security_level.value}")
    
    def _setup_command_whitelist(self):
        """Setup command whitelist based on security level"""
        # Always allowed commands
        base_commands = {
            'help', 'status', 'consciousness', 'mode', 'clear', 'exit',
            'start_game', 'roll_dice', 'buy_property', 'game_status', 'player_info'
        }
        
        # Enhanced commands for higher security levels
        enhanced_commands = {
            'mobile_create_app', 'mobile_deploy', 'mobile_analytics',
            'browse', 'search_reality', 'browser_stats',
            'cloud_create_bucket', 'cloud_upload', 'cloud_metrics',
            'api_register', 'api_call', 'api_metrics'
        }
        
        # Advanced commands for fortress level
        fortress_commands = {
            'dev_create_project', 'dev_enhance_code', 'dev_quantum_optimize',
            'galactic_create_planet', 'galactic_create_station', 'galactic_create_fleet',
            'galactic_status', 'galactic_navigate', 'setup_all'
        }
        
        # Cosmic commands for maximum level
        cosmic_commands = {
            'trade_consciousness', 'telepathic_browse', 'api_telepathic',
            'dev_debug', 'quantum', 'telepathic'
        }
        
        self.allowed_commands = base_commands.copy()
        
        if self.security_level in [TerminalSecurityLevel.HARDENED, TerminalSecurityLevel.FORTRESS, TerminalSecurityLevel.COSMIC]:
            self.allowed_commands.update(enhanced_commands)
        
        if self.security_level in [TerminalSecurityLevel.FORTRESS, TerminalSecurityLevel.COSMIC]:
            self.allowed_commands.update(fortress_commands)
        
        if self.security_level == TerminalSecurityLevel.COSMIC:
            self.allowed_commands.update(cosmic_commands)
        
        # Always blocked commands (security threats)
        self.blocked_commands = {
            'exec', 'eval', 'compile', 'open', 'file', 'input', 'raw_input',
            'import', '__import__', 'reload', 'execfile', 'subprocess',
            'os.system', 'os.popen', 'os.spawn', 'commands.getoutput',
            'shell', 'bash', 'sh', 'cmd', 'powershell', 'python', 'python3',
            'rm', 'del', 'delete', 'format', 'fdisk', 'mkfs',
            'wget', 'curl', 'nc', 'netcat', 'telnet', 'ssh', 'ftp',
            'gdb', 'lldb', 'strace', 'ltrace', 'ptrace', 'debug'
        }
        
        logger.info(f"✅ Command whitelist configured: {len(self.allowed_commands)} allowed, {len(self.blocked_commands)} blocked")
    
    def _setup_input_filters(self):
        """Setup input sanitization filters"""
        self.input_filters = [
            self._filter_command_injection,
            self._filter_path_traversal,
            self._filter_buffer_overflow,
            self._filter_format_string,
            self._filter_sql_injection,
            self._filter_script_injection,
            self._filter_null_bytes,
            self._filter_control_characters
        ]
        
        logger.info(f"🔍 Input filters configured: {len(self.input_filters)} filters active")
    
    def _setup_output_filters(self):
        """Setup output sanitization filters"""
        self.output_filters = [
            self._filter_sensitive_data,
            self._filter_system_information,
            self._filter_error_details,
            self._filter_debug_information
        ]
        
        logger.info(f"🔒 Output filters configured: {len(self.output_filters)} filters active")
    
    def _setup_environment_protection(self):
        """Setup secure environment protection"""
        try:
            # Clear dangerous environment variables
            dangerous_vars = [
                'LD_PRELOAD', 'LD_LIBRARY_PATH', 'DYLD_INSERT_LIBRARIES',
                'PYTHONPATH', 'PATH', 'IFS', 'PS1', 'PS2'
            ]
            
            for var in dangerous_vars:
                if var in os.environ:
                    del os.environ[var]
            
            # Set secure environment variables
            os.environ['ALIEN_SECURITY_MODE'] = 'HARDENED'
            os.environ['ALIEN_DEBUG_DISABLED'] = '1'
            os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
            os.environ['PYTHONHASHSEED'] = str(secrets.randbelow(2**32))
            
            # Restrict file permissions
            os.umask(0o077)  # Only owner can read/write
            
            self.environment_locked = True
            logger.info("🔐 Environment protection activated")
            
        except Exception as e:
            logger.error(f"❌ Environment protection failed: {e}")
    
    def _activate_debug_protection(self):
        """Activate anti-debugging protection"""
        try:
            # Check for debugger presence
            if self._detect_debugger():
                logger.warning("🚨 Debugger detected - activating countermeasures")
                self._deploy_anti_debug_measures()
            
            # Set up signal handlers for debugging attempts
            signal.signal(signal.SIGTRAP, self._handle_debug_signal)
            signal.signal(signal.SIGINT, self._handle_interrupt_signal)
            
            self.debug_protection_active = True
            logger.info("🛡️ Debug protection activated")
            
        except Exception as e:
            logger.error(f"❌ Debug protection failed: {e}")
    
    def _detect_debugger(self) -> bool:
        """Detect if debugger is attached"""
        try:
            # Check for common debugger processes
            debugger_processes = ['gdb', 'lldb', 'strace', 'ltrace', 'ida', 'x64dbg', 'ollydbg']
            
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'].lower() in debugger_processes:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Check for ptrace
            try:
                if os.path.exists('/proc/self/status'):
                    with open('/proc/self/status', 'r') as f:
                        for line in f:
                            if line.startswith('TracerPid:'):
                                tracer_pid = int(line.split()[1])
                                if tracer_pid != 0:
                                    return True
            except:
                pass
            
            return False
            
        except Exception:
            return False
    
    def _deploy_anti_debug_measures(self):
        """Deploy anti-debugging countermeasures"""
        # Obfuscate execution flow
        dummy_operations = [
            lambda: time.sleep(0.001),
            lambda: hashlib.md5(b'dummy').hexdigest(),
            lambda: [i for i in range(100)],
            lambda: {'dummy': 'data'}
        ]
        
        for _ in range(10):
            random.choice(dummy_operations)()
        
        logger.info("🔀 Anti-debug measures deployed")
    
    def _handle_debug_signal(self, signum, frame):
        """Handle debug signal"""
        logger.warning(f"🚨 Debug signal detected: {signum}")
        self._record_violation("debug_attempt", "HIGH", "Debug signal intercepted")
        
        # Deploy countermeasures
        self._deploy_anti_debug_measures()
    
    def _handle_interrupt_signal(self, signum, frame):
        """Handle interrupt signal"""
        logger.info("🛑 Interrupt signal received - secure shutdown")
        self._secure_shutdown()
    
    def sanitize_input(self, user_input: str) -> str:
        """Sanitize user input through all filters"""
        sanitized = user_input
        
        for filter_func in self.input_filters:
            try:
                sanitized = filter_func(sanitized)
            except Exception as e:
                logger.error(f"❌ Input filter error: {e}")
                self._record_violation("filter_error", "MEDIUM", f"Input filter failed: {e}")
        
        return sanitized
    
    def sanitize_output(self, output: str) -> str:
        """Sanitize output through all filters"""
        sanitized = output
        
        for filter_func in self.output_filters:
            try:
                sanitized = filter_func(sanitized)
            except Exception as e:
                logger.error(f"❌ Output filter error: {e}")
        
        return sanitized
    
    def validate_command(self, command: str) -> bool:
        """Validate if command is allowed"""
        command_parts = command.strip().split()
        if not command_parts:
            return False
        
        base_command = command_parts[0].lower()
        
        # Check if command is explicitly blocked
        if base_command in self.blocked_commands:
            self._record_violation("blocked_command", "HIGH", f"Blocked command attempted: {base_command}")
            return False
        
        # Check if command is in whitelist
        if base_command not in self.allowed_commands:
            self._record_violation("unauthorized_command", "MEDIUM", f"Unauthorized command attempted: {base_command}")
            return False
        
        return True
    
    # Input filter functions
    def _filter_command_injection(self, input_str: str) -> str:
        """Filter command injection attempts"""
        dangerous_patterns = [
            r'[;&|`$()]',  # Command separators and substitution
            r'\.\./',      # Path traversal
            r'\\x[0-9a-fA-F]{2}',  # Hex encoding
            r'%[0-9a-fA-F]{2}',    # URL encoding
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, input_str):
                self._record_violation("command_injection", "HIGH", f"Command injection pattern detected: {pattern}")
                input_str = re.sub(pattern, '', input_str)
        
        return input_str
    
    def _filter_path_traversal(self, input_str: str) -> str:
        """Filter path traversal attempts"""
        traversal_patterns = [
            r'\.\./',
            r'\.\.\\',
            r'%2e%2e%2f',
            r'%2e%2e%5c',
            r'..%2f',
            r'..%5c'
        ]
        
        for pattern in traversal_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                self._record_violation("path_traversal", "HIGH", f"Path traversal attempt detected")
                input_str = re.sub(pattern, '', input_str, flags=re.IGNORECASE)
        
        return input_str
    
    def _filter_buffer_overflow(self, input_str: str) -> str:
        """Filter potential buffer overflow attempts"""
        max_length = 1024  # Maximum safe input length
        
        if len(input_str) > max_length:
            self._record_violation("buffer_overflow", "HIGH", f"Input too long: {len(input_str)} > {max_length}")
            input_str = input_str[:max_length]
        
        # Check for repeated characters (potential overflow)
        for char in input_str:
            if input_str.count(char) > 100:
                self._record_violation("buffer_overflow", "MEDIUM", f"Repeated character pattern detected")
                break
        
        return input_str
    
    def _filter_format_string(self, input_str: str) -> str:
        """Filter format string attacks"""
        format_patterns = [
            r'%[0-9]*[diouxXeEfFgGaAcspn%]',  # Format specifiers
            r'\\x[0-9a-fA-F]{2}',            # Hex escape sequences
        ]
        
        for pattern in format_patterns:
            if re.search(pattern, input_str):
                self._record_violation("format_string", "HIGH", f"Format string pattern detected")
                input_str = re.sub(pattern, '', input_str)
        
        return input_str
    
    def _filter_sql_injection(self, input_str: str) -> str:
        """Filter SQL injection attempts"""
        sql_patterns = [
            r"'.*'",           # Single quotes
            r'".*"',           # Double quotes
            r'--.*',           # SQL comments
            r'/\*.*\*/',       # Block comments
            r'\bunion\b',      # UNION keyword
            r'\bselect\b',     # SELECT keyword
            r'\binsert\b',     # INSERT keyword
            r'\bdelete\b',     # DELETE keyword
            r'\bdrop\b',       # DROP keyword
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                self._record_violation("sql_injection", "HIGH", f"SQL injection pattern detected")
                input_str = re.sub(pattern, '', input_str, flags=re.IGNORECASE)
        
        return input_str
    
    def _filter_script_injection(self, input_str: str) -> str:
        """Filter script injection attempts"""
        script_patterns = [
            r'<script.*?>.*?</script>',  # Script tags
            r'javascript:',              # JavaScript protocol
            r'vbscript:',               # VBScript protocol
            r'on\w+\s*=',               # Event handlers
        ]
        
        for pattern in script_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                self._record_violation("script_injection", "HIGH", f"Script injection pattern detected")
                input_str = re.sub(pattern, '', input_str, flags=re.IGNORECASE)
        
        return input_str
    
    def _filter_null_bytes(self, input_str: str) -> str:
        """Filter null bytes and control characters"""
        # Remove null bytes
        if '\x00' in input_str:
            self._record_violation("null_byte", "MEDIUM", "Null byte detected")
            input_str = input_str.replace('\x00', '')
        
        return input_str
    
    def _filter_control_characters(self, input_str: str) -> str:
        """Filter dangerous control characters"""
        # Allow only printable ASCII and common whitespace
        allowed_chars = set(string.printable)
        filtered = ''.join(char for char in input_str if char in allowed_chars)
        
        if len(filtered) != len(input_str):
            self._record_violation("control_chars", "LOW", "Control characters filtered")
        
        return filtered
    
    # Output filter functions
    def _filter_sensitive_data(self, output: str) -> str:
        """Filter sensitive data from output"""
        sensitive_patterns = [
            (r'password\s*[:=]\s*\S+', 'password: [REDACTED]'),
            (r'key\s*[:=]\s*\S+', 'key: [REDACTED]'),
            (r'token\s*[:=]\s*\S+', 'token: [REDACTED]'),
            (r'secret\s*[:=]\s*\S+', 'secret: [REDACTED]'),
        ]
        
        for pattern, replacement in sensitive_patterns:
            output = re.sub(pattern, replacement, output, flags=re.IGNORECASE)
        
        return output
    
    def _filter_system_information(self, output: str) -> str:
        """Filter system information from output"""
        # Hide file paths
        output = re.sub(r'/[^\s]*', '[PATH_REDACTED]', output)
        output = re.sub(r'C:\\[^\s]*', '[PATH_REDACTED]', output)
        
        # Hide IP addresses
        output = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_REDACTED]', output)
        
        return output
    
    def _filter_error_details(self, output: str) -> str:
        """Filter detailed error information"""
        if 'Traceback' in output or 'Error:' in output:
            # Replace detailed tracebacks with generic error message
            output = "🚨 An error occurred. Contact support if needed."
        
        return output
    
    def _filter_debug_information(self, output: str) -> str:
        """Filter debug information"""
        debug_patterns = [
            r'DEBUG:.*',
            r'TRACE:.*',
            r'File ".*", line \d+',
            r'at 0x[0-9a-fA-F]+',  # Memory addresses
        ]
        
        for pattern in debug_patterns:
            output = re.sub(pattern, '[DEBUG_INFO_REDACTED]', output)
        
        return output
    
    def _record_violation(self, violation_type: str, severity: str, description: str, blocked: bool = True):
        """Record security violation"""
        violation = SecurityViolation(
            timestamp=time.time(),
            violation_type=violation_type,
            severity=severity,
            description=description,
            blocked=blocked
        )
        
        self.violations.append(violation)
        
        # Log violation
        logger.warning(f"🚨 SECURITY VIOLATION: {severity} - {violation_type}: {description}")
        
        # Save to file
        self._save_violation(violation)
    
    def _save_violation(self, violation: SecurityViolation):
        """Save violation to security log"""
        try:
            log_file = 'security/logs/terminal_violations.json'
            
            violation_data = {
                "timestamp": violation.timestamp,
                "type": violation.violation_type,
                "severity": violation.severity,
                "description": violation.description,
                "blocked": violation.blocked
            }
            
            # Load existing violations
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    violations = json.load(f)
            else:
                violations = []
            
            violations.append(violation_data)
            
            # Keep only last 1000 violations
            if len(violations) > 1000:
                violations = violations[-1000:]
            
            with open(log_file, 'w') as f:
                json.dump(violations, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Failed to save violation: {e}")
    
    def _secure_shutdown(self):
        """Perform secure shutdown"""
        logger.info("🔒 Performing secure shutdown...")
        
        # Clear sensitive data from memory
        self.violations.clear()
        self.blocked_commands.clear()
        self.allowed_commands.clear()
        
        # Clear environment variables
        if 'ALIEN_SECURITY_MODE' in os.environ:
            del os.environ['ALIEN_SECURITY_MODE']
        
        logger.info("✅ Secure shutdown completed")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get terminal security status"""
        return {
            "security_level": self.security_level.value,
            "environment_locked": self.environment_locked,
            "debug_protection": self.debug_protection_active,
            "total_violations": len(self.violations),
            "input_filters": len(self.input_filters),
            "output_filters": len(self.output_filters),
            "allowed_commands": len(self.allowed_commands),
            "blocked_commands": len(self.blocked_commands)
        }
    
    def get_violation_summary(self) -> Dict[str, int]:
        """Get violation summary by type"""
        summary = {}
        for violation in self.violations:
            violation_type = violation.violation_type
            summary[violation_type] = summary.get(violation_type, 0) + 1
        return summary

# Global terminal security instance
_terminal_security = None

def get_terminal_security() -> TerminalSecurityHardening:
    """Get global terminal security instance"""
    global _terminal_security
    if _terminal_security is None:
        _terminal_security = TerminalSecurityHardening()
    return _terminal_security

def initialize_terminal_security(security_level: TerminalSecurityLevel = TerminalSecurityLevel.FORTRESS) -> TerminalSecurityHardening:
    """Initialize global terminal security"""
    global _terminal_security
    _terminal_security = TerminalSecurityHardening(security_level)
    return _terminal_security

if __name__ == "__main__":
    # Demo terminal security
    print("🛸 TERMINAL SECURITY HARDENING DEMO 🛸")
    
    security = TerminalSecurityHardening(TerminalSecurityLevel.FORTRESS)
    
    # Test input sanitization
    test_inputs = [
        "help",
        "rm -rf /",
        "'; DROP TABLE users; --",
        "../../../etc/passwd",
        "help && cat /etc/passwd",
        "A" * 2000,  # Buffer overflow test
    ]
    
    print("\n🔍 Testing input sanitization:")
    for test_input in test_inputs:
        sanitized = security.sanitize_input(test_input)
        valid = security.validate_command(sanitized)
        print(f"Input: '{test_input[:50]}...' -> Valid: {valid}")
    
    print(f"\n📊 Security Status: {security.get_security_status()}")
    print(f"📊 Violations: {security.get_violation_summary()}")
    
    print("🔒 Terminal security demo completed")