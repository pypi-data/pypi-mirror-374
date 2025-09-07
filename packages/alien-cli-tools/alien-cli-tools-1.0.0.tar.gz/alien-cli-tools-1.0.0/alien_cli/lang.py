#!/usr/bin/env python3
"""
👽 Alien Lang CLI - AlienLang Programming Language Interface
==========================================================

Command-line interface for the AlienLang programming language:
- Run AlienLang programs
- Interactive REPL mode
- Compile to bytecode
- Package management
- Language server

Usage:
    alien-lang run <file>           - Run AlienLang program
    alien-lang repl                 - Interactive REPL
    alien-lang compile <file>       - Compile to bytecode
    alien-lang package <command>    - Package management
    alien-lang consciousness       - Consciousness analysis
"""

import sys
import os
import argparse
from pathlib import Path

def launch_alien_lang(command_args):
    """Launch AlienLang with specified arguments"""
    
    # Get the path to alien_v3.py
    current_dir = Path(__file__).parent.parent
    alien_lang_path = current_dir / "alien_v3.py"
    
    if not alien_lang_path.exists():
        print("❌ AlienLang interpreter not found!")
        print(f"Expected location: {alien_lang_path}")
        return False
    
    # Build command
    cmd_args = [sys.executable, str(alien_lang_path)] + command_args
    
    print("👽 AlienLang Programming Language")
    print("=" * 40)
    
    # Launch AlienLang
    try:
        os.execv(sys.executable, cmd_args)
    except Exception as e:
        print(f"❌ Error launching AlienLang: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="👽 Alien Lang CLI - AlienLang Programming Language Interface")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run AlienLang program')
    run_parser.add_argument('file', help='AlienLang file to run')
    
    # REPL command
    repl_parser = subparsers.add_parser('repl', help='Interactive REPL mode')
    
    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile to bytecode')
    compile_parser.add_argument('file', help='AlienLang file to compile')
    
    # Package command
    package_parser = subparsers.add_parser('package', help='Package management')
    package_parser.add_argument('subcommand', help='Package subcommand')
    package_parser.add_argument('args', nargs='*', help='Package arguments')
    
    # Consciousness command
    consciousness_parser = subparsers.add_parser('consciousness', help='Consciousness analysis')
    consciousness_parser.add_argument('file', nargs='?', help='File to analyze')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('file', nargs='?', help='Test file')
    
    # LSP command
    lsp_parser = subparsers.add_parser('lsp', help='Start language server')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version')
    
    # Help command
    help_parser = subparsers.add_parser('help', help='Show help')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Build command arguments for alien_v3.py
    if args.command == 'run':
        command_args = ['run', args.file]
    elif args.command == 'repl':
        command_args = ['repl']
    elif args.command == 'compile':
        command_args = ['compile', args.file]
    elif args.command == 'package':
        command_args = ['package', args.subcommand] + args.args
    elif args.command == 'consciousness':
        command_args = ['consciousness']
        if args.file:
            command_args.append(args.file)
    elif args.command == 'test':
        command_args = ['test']
        if args.file:
            command_args.append(args.file)
    elif args.command == 'lsp':
        command_args = ['lsp']
    elif args.command == 'version':
        command_args = ['--version']
    elif args.command == 'help':
        command_args = ['--help']
    else:
        print(f"❌ Unknown command: {args.command}")
        return
    
    # Launch AlienLang
    success = launch_alien_lang(command_args)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()