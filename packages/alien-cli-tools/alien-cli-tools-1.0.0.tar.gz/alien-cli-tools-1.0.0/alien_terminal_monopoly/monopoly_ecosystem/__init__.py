#!/usr/bin/env python3
"""
🎮 MONOPOLY ECOSYSTEM EXPANSION 🎮
Multiple themed monopoly games menggunakan Alien Payment System

Features:
- Industry-specific monopoly games
- Regional monopoly variants
- Professional monopoly series
- Educational monopoly games
- Themed monopoly experiences
- Unified payment system (ACC)
- Cross-game progression
- Ecosystem rewards
"""

from .tech_monopoly import TechMonopoly
from .crypto_monopoly import CryptoMonopoly
from .space_monopoly import SpaceMonopoly
from .ocean_monopoly import OceanMonopoly
from .medical_monopoly import MedicalMonopoly
from .education_monopoly import EducationMonopoly
from .entertainment_monopoly import EntertainmentMonopoly
from .business_monopoly import BusinessMonopoly

__version__ = "∞.0.0"
__author__ = "Alien Technologies"

# Monopoly game registry
MONOPOLY_GAMES = {
    "tech": TechMonopoly,
    "crypto": CryptoMonopoly,
    "space": SpaceMonopoly,
    "ocean": OceanMonopoly,
    "medical": MedicalMonopoly,
    "education": EducationMonopoly,
    "entertainment": EntertainmentMonopoly,
    "business": BusinessMonopoly
}

# Game categories
GAME_CATEGORIES = {
    "industry": ["tech", "crypto", "medical", "entertainment"],
    "exploration": ["space", "ocean"],
    "professional": ["business", "education"],
    "themed": ["tech", "crypto", "space", "ocean", "medical", "education", "entertainment", "business"]
}

def initialize_monopoly_ecosystem():
    """Initialize Monopoly Ecosystem"""
    print("🎮 Initializing Monopoly Ecosystem...")
    
    games = {}
    for name, game_class in MONOPOLY_GAMES.items():
        try:
            games[name] = game_class()
            print(f"✅ {name.replace('_', ' ').title()} Monopoly initialized")
        except Exception as e:
            print(f"⚠️ Failed to initialize {name}: {e}")
    
    print(f"🌟 Monopoly Ecosystem initialized: {len(games)}/{len(MONOPOLY_GAMES)} games")
    return games

def get_ecosystem_status():
    """Get status of monopoly ecosystem"""
    return {
        "total_games": len(MONOPOLY_GAMES),
        "available_games": list(MONOPOLY_GAMES.keys()),
        "categories": GAME_CATEGORIES,
        "payment_system": "Alien Consciousness Currency (ACC)",
        "cross_game_progression": True,
        "unified_ecosystem": True
    }

def get_game_recommendations(player_interests: List[str]) -> List[str]:
    """Get game recommendations berdasarkan player interests"""
    recommendations = []
    
    interest_mapping = {
        "technology": ["tech", "crypto"],
        "science": ["space", "medical", "education"],
        "business": ["business", "entertainment"],
        "exploration": ["space", "ocean"],
        "finance": ["crypto", "business"],
        "healthcare": ["medical"],
        "education": ["education"],
        "entertainment": ["entertainment"],
        "gaming": ["tech", "entertainment"]
    }
    
    for interest in player_interests:
        if interest.lower() in interest_mapping:
            recommendations.extend(interest_mapping[interest.lower()])
    
    # Remove duplicates and return
    return list(set(recommendations))

# Auto-initialize when imported
print("🎮 Monopoly Ecosystem package loaded")
print(f"🌟 Available games: {len(MONOPOLY_GAMES)}")