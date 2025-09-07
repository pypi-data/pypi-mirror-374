#!/usr/bin/env python3
"""
🛸 Alien Terminal Launcher - Launch Advanced Terminal
===================================================

Launch the Alien Terminal Pro with advanced features:
- AI-powered command suggestions
- Consciousness-driven interface
- Cross-platform compatibility
- Rich UI and advanced features

Usage:
    alien-terminal                  - Launch interactive mode
    alien-terminal --visual         - Launch visual mode
    alien-terminal --daemon         - Start daemon mode
    alien-terminal --consciousness  - Set consciousness level
"""

import sys
import os
import argparse
from pathlib import Path

def launch_alien_terminal(mode="interactive", consciousness=None):
    """Launch Alien Terminal Pro"""
    
    # Get the path to alien terminal
    current_dir = Path(__file__).parent.parent
    terminal_path = current_dir / "alien_terminal_pro" / "alien_terminal.py"
    
    if not terminal_path.exists():
        print("❌ Alien Terminal Pro not found!")
        print(f"Expected location: {terminal_path}")
        return False
    
    # Build command
    cmd_args = [sys.executable, str(terminal_path)]
    
    if mode != "interactive":
        cmd_args.extend(["--mode", mode])
    
    if consciousness:
        cmd_args.extend(["--consciousness", str(consciousness)])
    
    print("🛸 Launching Alien Terminal Pro...")
    print(f"Mode: {mode}")
    if consciousness:
        print(f"Consciousness Level: {consciousness}")
    print("=" * 50)
    
    # Launch the terminal
    try:
        os.execv(sys.executable, cmd_args)
    except Exception as e:
        print(f"❌ Error launching terminal: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="🛸 Alien Terminal Launcher")
    parser.add_argument("--mode", choices=["interactive", "visual", "daemon"], 
                       default="interactive", help="Terminal mode")
    parser.add_argument("--consciousness", type=float, 
                       help="Initial consciousness level (0.0-1.0)")
    parser.add_argument("--visual", action="store_true", 
                       help="Launch in visual mode")
    parser.add_argument("--daemon", action="store_true", 
                       help="Start in daemon mode")
    
    args = parser.parse_args()
    
    # Determine mode
    mode = args.mode
    if args.visual:
        mode = "visual"
    elif args.daemon:
        mode = "daemon"
    
    # Validate consciousness level
    consciousness = args.consciousness
    if consciousness is not None:
        consciousness = max(0.0, min(1.0, consciousness))
    
    # Launch terminal
    success = launch_alien_terminal(mode, consciousness)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()