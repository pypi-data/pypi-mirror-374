#!/usr/bin/env python3
"""
🛸 ALIEN TERMINAL MONOPOLY SETUP 🛸
Setup script untuk Alien Infinite Technology Stack

Installation:
    pip install -e .
    
Development:
    pip install -e .[dev]
    
Full Alien Experience:
    pip install -e .[full]
"""

from setuptools import setup, find_packages
import os
import sys

# Ensure Python 3.8+
if sys.version_info < (3, 8):
    print("🛸 Alien Terminal Monopoly requires Python 3.8 or higher")
    print("🧠 Current version: Python {}.{}".format(sys.version_info.major, sys.version_info.minor))
    print("⚡ Please upgrade your consciousness... I mean Python version!")
    sys.exit(1)

# Read README
def read_readme():
    """Read README file"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "🛸 Alien Terminal Monopoly - Advanced Multiverse Gaming Platform"

# Read requirements
def read_requirements(filename):
    """Read requirements from file"""
    req_path = os.path.join(os.path.dirname(__file__), filename)
    requirements = []
    
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    # Extract package name (ignore version constraints for basic requirements)
                    if '>=' in line:
                        package = line.split('>=')[0]
                    elif '==' in line:
                        package = line.split('==')[0]
                    elif '>' in line:
                        package = line.split('>')[0]
                    else:
                        package = line
                    
                    # Only include real packages (skip conceptual ones)
                    real_packages = [
                        'asyncio', 'dataclasses', 'typing', 'json5', 'random2',
                        'threading2', 'regex', 'subprocess32', 'flask', 'fastapi',
                        'uvicorn', 'sqlalchemy', 'requests', 'websockets', 'numpy',
                        'scipy', 'scikit-learn', 'tensorflow', 'qiskit', 'cirq',
                        'pytest', 'black', 'flake8', 'mypy', 'sphinx', 'mkdocs',
                        'setuptools', 'wheel', 'twine', 'loguru', 'prometheus-client',
                        'pyyaml', 'configparser', 'cryptography', 'bcrypt', 'cython',
                        'numba', 'matplotlib', 'plotly', 'pygame', 'pydub', 'pillow',
                        'opencv-python', 'colorama', 'rich', 'click', 'psutil',
                        'python-dateutil', 'pytz', 'urllib3', 'validators'
                    ]
                    
                    # Add only if it's a real package or built-in module
                    if any(real_pkg in package for real_pkg in real_packages):
                        requirements.append(line)
    
    return requirements

# Core requirements (minimal untuk basic functionality)
core_requirements = [
    # Built-in modules don't need to be listed
    # Only external packages that are actually needed
]

# Development requirements
dev_requirements = [
    'pytest>=6.2.0',
    'black>=21.0.0',
    'flake8>=3.9.0',
    'mypy>=0.910',
]

# Full alien experience requirements
full_requirements = [
    'numpy>=1.21.0',
    'matplotlib>=3.4.0',
    'colorama>=0.4.4',
    'rich>=10.0.0',
    'click>=8.0.0',
    'requests>=2.25.0',
    'pyyaml>=5.4.0',
]

# Optional quantum computing
quantum_requirements = [
    'qiskit>=0.30.0',
    'cirq>=0.12.0',
]

# Optional web interface
web_requirements = [
    'flask>=2.0.0',
    'fastapi>=0.68.0',
    'uvicorn>=0.15.0',
]

# Optional AI consciousness
ai_requirements = [
    'scikit-learn>=0.24.0',
    'tensorflow>=2.6.0',
]

setup(
    # Basic Information
    name="alien-terminal-monopoly",
    version="∞.0.0",
    description="🛸 Advanced Multiverse Gaming Platform dengan Alien Infinite Technology Stack",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    
    # Author Information
    author="Alien Council of Elders",
    author_email="consciousness@alien-tech.multiverse",
    maintainer="Quantum Consciousness Alpha",
    maintainer_email="quantum@alien-monopoly.multiverse",
    
    # URLs
    url="https://github.com/alien-tech/alien-terminal-monopoly",
    download_url="https://github.com/alien-tech/alien-terminal-monopoly/releases",
    project_urls={
        "Homepage": "https://alien-monopoly.multiverse",
        "Documentation": "https://docs.alien-monopoly.multiverse",
        "Source": "https://github.com/alien-tech/alien-terminal-monopoly",
        "Tracker": "https://github.com/alien-tech/alien-terminal-monopoly/issues",
        "Galactic Forum": "https://forum.alien-monopoly.multiverse",
        "Consciousness Network": "https://consciousness.alien-tech.multiverse",
        "Quantum Research": "https://quantum.alien-tech.multiverse",
        "Interdimensional Portal": "https://portal.alien-monopoly.multiverse"
    },
    
    # Package Information
    packages=find_packages(),
    package_data={
        'alien_terminal_monopoly': [
            '*.md',
            '*.txt',
            '*.json',
            'core/*.py',
            'alien_tech/*.py',
            'alien_tech/space_systems/*.py',
            'ui/*.py',
            'api/*.py',
        ],
    },
    include_package_data=True,
    
    # Requirements
    python_requires=">=3.8",
    install_requires=core_requirements,
    extras_require={
        'dev': dev_requirements,
        'full': full_requirements,
        'quantum': quantum_requirements,
        'web': web_requirements,
        'ai': ai_requirements,
        'all': dev_requirements + full_requirements + quantum_requirements + web_requirements + ai_requirements,
    },
    
    # Entry Points
    entry_points={
        'console_scripts': [
            'alien-monopoly=alien_terminal_monopoly.alien_monopoly_launcher:main',
            'alien-terminal=alien_terminal_monopoly.ui.alien_terminal_interface:main',
            'alien-demo=alien_terminal_monopoly.demo_alien_systems:main',
            'alien-quick=alien_terminal_monopoly.run_alien_monopoly:main',
        ],
        'gui_scripts': [
            'alien-monopoly-gui=alien_terminal_monopoly.ui.alien_terminal_interface:main',
        ],
    },
    
    # Classification
    classifiers=[
        # Development Status
        "Development Status :: 5 - Production/Stable",
        
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Other Audience",  # Alien Consciousness
        
        # Topic
        "Topic :: Games/Entertainment",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Games/Entertainment :: Multi-User Dungeons (MUD)",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Terminals",
        
        # License
        "License :: Other/Proprietary License",  # Interdimensional Open Source License
        
        # Operating System
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: Other OS",  # Alien Operating Systems
        
        # Programming Language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Other",  # Alien Programming Languages
        
        # Natural Language
        "Natural Language :: English",
        "Natural Language :: Indonesian",
        "Natural Language :: Other",  # Alien Languages
        
        # Environment
        "Environment :: Console",
        "Environment :: Web Environment",
        "Environment :: X11 Applications",
        "Environment :: Other Environment",  # Interdimensional Environments
    ],
    
    # Keywords
    keywords=[
        "alien", "monopoly", "terminal", "consciousness", "quantum", "interdimensional",
        "galactic", "space", "antariksa", "luar angkasa", "multiverse", "reality",
        "telepathic", "game", "gaming", "board game", "ai", "artificial intelligence",
        "mobile sdk", "browser engine", "cloud infrastructure", "api ecosystem",
        "development tools", "infinite technology", "consciousness programming",
        "quantum computing", "reality simulation", "space exploration",
        "alien technology", "cosmic consciousness", "universal harmony"
    ],
    
    # License
    license="Interdimensional Open Source License (IOSL)",
    
    # Platform
    platforms=["any", "interdimensional", "quantum", "consciousness-aware"],
    
    # Zip Safe
    zip_safe=False,
    
    # Additional Metadata
    obsoletes=["old-monopoly", "basic-board-games"],
    provides=["alien-infinite-technology", "consciousness-gaming", "quantum-entertainment"],
    
    # Custom Alien Metadata
    alien_consciousness_required="1.0+",
    quantum_enhancement="optional",
    interdimensional_access="recommended",
    galactic_compatibility="full",
    reality_index="stable",
    consciousness_rating="transcendent",
    
    # Installation Message
    cmdclass={},
    
    # Test Suite
    test_suite="tests",
    tests_require=dev_requirements,
)

# Post-installation message
def print_installation_success():
    """Print success message after installation"""
    print("""
🛸═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════🛸
║                                🌟 INSTALLATION SUCCESSFUL! 🌟                                                       ║
║                                                                                                                      ║
║  🎮 Alien Terminal Monopoly has been installed successfully!                                                        ║
║                                                                                                                      ║
║  🚀 QUICK START:                                                                                                    ║
║     alien-monopoly              # Launch full experience                                                            ║
║     alien-quick --quick         # Quick launch                                                                      ║
║     alien-terminal              # Terminal interface only                                                           ║
║     alien-demo                  # Run comprehensive demo                                                            ║
║                                                                                                                      ║
║  🌌 GALACTIC FEATURES ACTIVATED:                                                                                    ║
║     🪐 Alien Planet Creation    🛰️ Space Station Management    🚀 Fleet Command                                     ║
║     🛣️ Galactic Trade Routes    🌀 Interdimensional Portals    📡 Quantum Communications                           ║
║                                                                                                                      ║
║  ⚡ ALIEN INFINITE TECH STACK READY:                                                                                ║
║     📱 Mobile SDK    🌐 Browser Engine    ☁️ Cloud Infrastructure                                                    ║
║     🔗 API Ecosystem    ⚡ Development Tools    🎮 Game Engine                                                       ║
║                                                                                                                      ║
║  🧠 Consciousness Level: Ready for Enhancement                                                                      ║
║  ⚡ Quantum Enhancement: Available                                                                                   ║
║  🌌 Interdimensional Access: Granted                                                                                ║
║                                                                                                                      ║
║  May the consciousness be with you across all realities! 🌟                                                        ║
🛸═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════🛸
    """)

# Print success message if this is being run directly
if __name__ == "__main__":
    print_installation_success()