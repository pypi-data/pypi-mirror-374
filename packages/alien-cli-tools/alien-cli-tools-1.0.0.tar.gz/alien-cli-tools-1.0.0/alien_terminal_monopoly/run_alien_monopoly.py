#!/usr/bin/env python3
"""
🛸 RUN ALIEN TERMINAL MONOPOLY 🛸
Quick launcher untuk Alien Terminal Monopoly dengan aktivasi sistem antariksa

Usage:
    python run_alien_monopoly.py              # Launch dengan full initialization
    python run_alien_monopoly.py --quick      # Quick launch tanpa full setup
    python run_alien_monopoly.py --terminal   # Direct ke terminal interface
    python run_alien_monopoly.py --galactic   # Focus pada galactic systems
"""

import asyncio
import sys
import argparse
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from alien_monopoly_launcher import AlienMonopolyLauncher
from ui.alien_terminal_interface import AlienTerminalInterface

def print_quick_banner():
    """Print quick launch banner"""
    print("""
🛸═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════🛸
║                                    🌟 ALIEN TERMINAL MONOPOLY 🌟                                                     ║
║                                      Quick Launch Activated                                                          ║
║                                                                                                                      ║
║  🚀 ANTARIKSA & LUAR ANGKASA SYSTEMS READY:                                                                         ║
║     🪐 Alien Planets        🛰️ Space Stations        🚀 Alien Fleets                                                ║
║     🛣️ Trade Routes         🌀 Portal Networks       📡 Quantum Communications                                      ║
║                                                                                                                      ║
║  ⚡ ALIEN INFINITE TECH STACK ONLINE:                                                                               ║
║     📱 Mobile SDK    🌐 Browser Engine    ☁️ Cloud Infrastructure                                                    ║
║     🔗 API Ecosystem    ⚡ Development Tools    🎮 Game Engine                                                       ║
║                                                                                                                      ║
║  🧠 Consciousness Level: MAXIMUM    ⚡ Quantum: ACTIVE    🌌 Interdimensional: READY                               ║
🛸═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════🛸
""")

def print_galactic_banner():
    """Print galactic focus banner"""
    print("""
🌌═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════🌌
║                                🚀 GALACTIC COMMAND CENTER 🚀                                                        ║
║                                  Antariksa & Luar Angkasa                                                           ║
║                                                                                                                      ║
║  🪐 PLANET MANAGEMENT:                                                                                               ║
║     • Create alien worlds dengan consciousness fields                                                               ║
║     • Manage alien species dan resources                                                                            ║
║     • Establish consciousness networks                                                                               ║
║                                                                                                                      ║
║  🛰️ SPACE STATION OPERATIONS:                                                                                        ║
║     • Deploy quantum research facilities                                                                            ║
║     • Manage consciousness amplifiers                                                                               ║
║     • Control interdimensional gateways                                                                             ║
║                                                                                                                      ║
║  🚀 FLEET COMMAND:                                                                                                   ║
║     • Command alien armadas                                                                                          ║
║     • Execute interdimensional missions                                                                              ║
║     • Protect consciousness networks                                                                                 ║
║                                                                                                                      ║
║  🛣️ TRADE NETWORKS:                                                                                                  ║
║     • Establish galactic commerce                                                                                    ║
║     • Manage consciousness trading                                                                                   ║
║     • Control quantum resource flows                                                                                 ║
🌌═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════🌌
""")

async def quick_launch():
    """Quick launch dengan minimal setup"""
    print_quick_banner()
    print("🚀 Quick launching Alien Terminal Monopoly...")
    print("⚡ Skipping full system initialization for faster startup...")
    
    # Direct launch terminal interface
    try:
        terminal = AlienTerminalInterface()
        terminal.consciousness_level = 50.0  # Boost consciousness untuk quick start
        terminal.quantum_enhancement = True
        terminal.interdimensional_access = True
        
        print("✅ Quick launch successful!")
        print("🌟 All alien systems simulated and ready!")
        print("🎮 Type 'help' for commands or 'setup_all' for full initialization")
        
        terminal.run()
        
    except Exception as e:
        print(f"❌ Quick launch failed: {e}")
        print("🔧 Try full launch instead: python run_alien_monopoly.py")

async def terminal_launch():
    """Direct terminal launch"""
    print("🖥️ Launching Alien Terminal Interface directly...")
    
    try:
        terminal = AlienTerminalInterface()
        terminal.consciousness_level = 25.0
        terminal.quantum_enhancement = True
        
        print("✅ Terminal interface ready!")
        print("🧠 Consciousness-aware commands available")
        print("⚡ Quantum enhancement active")
        
        terminal.run()
        
    except Exception as e:
        print(f"❌ Terminal launch failed: {e}")

async def galactic_launch():
    """Launch dengan focus pada galactic systems"""
    print_galactic_banner()
    print("🌌 Initializing Galactic Command Center...")
    
    try:
        # Initialize launcher dengan focus galactic
        launcher = AlienMonopolyLauncher()
        launcher.galactic_activation = True
        launcher.launcher_consciousness = 100.0
        
        # Initialize galactic infrastructure first
        print("🚀 Prioritizing galactic infrastructure initialization...")
        success = await launcher._initialize_galactic_infrastructure()
        
        if success:
            print("✅ Galactic infrastructure online!")
            
            # Launch galactic command interface
            terminal = AlienTerminalInterface()
            terminal.consciousness_level = 75.0
            terminal.current_mode = terminal.current_mode.GALACTIC
            terminal.galactic_infrastructure = launcher.galactic_infrastructure
            
            print("🌟 Galactic Command Center operational!")
            print("🪐 Planet management ready")
            print("🛰️ Space station control active")
            print("🚀 Fleet command systems online")
            print("\nType 'galactic_status' to see full galactic overview")
            
            terminal.run()
        else:
            print("❌ Failed to initialize galactic systems")
            
    except Exception as e:
        print(f"❌ Galactic launch failed: {e}")

async def full_launch():
    """Full launch dengan complete initialization"""
    print("🛸 Starting full Alien Terminal Monopoly initialization...")
    
    try:
        launcher = AlienMonopolyLauncher()
        await launcher.run()
        
    except Exception as e:
        print(f"❌ Full launch failed: {e}")

def main():
    """Main function dengan argument parsing"""
    parser = argparse.ArgumentParser(
        description="🛸 Alien Terminal Monopoly Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_alien_monopoly.py              # Full launch dengan complete setup
  python run_alien_monopoly.py --quick      # Quick launch untuk testing
  python run_alien_monopoly.py --terminal   # Direct terminal interface
  python run_alien_monopoly.py --galactic   # Galactic systems focus

🌟 Alien Terminal Monopoly - Powered by Alien Infinite Technology Stack
🚀 Ready for consciousness-aware interdimensional gameplay!
        """
    )
    
    parser.add_argument(
        "--quick", 
        action="store_true",
        help="Quick launch tanpa full system initialization"
    )
    
    parser.add_argument(
        "--terminal",
        action="store_true", 
        help="Launch direct ke terminal interface"
    )
    
    parser.add_argument(
        "--galactic",
        action="store_true",
        help="Launch dengan focus pada galactic infrastructure"
    )
    
    parser.add_argument(
        "--consciousness",
        type=float,
        default=10.0,
        help="Set initial consciousness level (default: 10.0)"
    )
    
    args = parser.parse_args()
    
    # Determine launch mode
    if args.quick:
        print("🚀 Quick Launch Mode Selected")
        asyncio.run(quick_launch())
    elif args.terminal:
        print("🖥️ Terminal Launch Mode Selected")
        asyncio.run(terminal_launch())
    elif args.galactic:
        print("🌌 Galactic Launch Mode Selected")
        asyncio.run(galactic_launch())
    else:
        print("🛸 Full Launch Mode Selected")
        asyncio.run(full_launch())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n🛸 Alien Terminal Monopoly launcher interrupted.")
        print(f"🌟 Consciousness preserved across all realities.")
        print(f"🚀 Thank you for using Alien Infinite Technology!")
    except Exception as e:
        print(f"\n❌ Fatal launcher error: {e}")
        print(f"🔧 Please check system requirements:")
        print(f"   - Python 3.8+")
        print(f"   - Consciousness level 1.0+")
        print(f"   - Quantum-capable processor (simulated)")
        print(f"   - Interdimensional network access (optional)")