#!/usr/bin/env python3
"""
💻 TECH MONOPOLY - Silicon Valley Edition 💻
Technology-themed monopoly game dengan startup ecosystem

Features:
- Tech company properties (Google, Apple, Microsoft, etc.)
- Startup incubators dan venture capital
- IPO events dan stock market
- Tech talent acquisition
- Innovation challenges
- Patent warfare
- Cryptocurrency integration
"""

import asyncio
import json
import time
import uuid
import math
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class TechPropertyType(Enum):
    STARTUP = "startup"
    UNICORN = "unicorn"
    BIG_TECH = "big_tech"
    VENTURE_CAPITAL = "venture_capital"
    INCUBATOR = "incubator"
    RESEARCH_LAB = "research_lab"
    DATA_CENTER = "data_center"
    PATENT_OFFICE = "patent_office"

class TechEvent(Enum):
    IPO_LAUNCH = "ipo_launch"
    ACQUISITION = "acquisition"
    FUNDING_ROUND = "funding_round"
    PATENT_DISPUTE = "patent_dispute"
    TECH_BUBBLE = "tech_bubble"
    INNOVATION_BREAKTHROUGH = "innovation_breakthrough"
    CYBER_ATTACK = "cyber_attack"
    REGULATION_CHANGE = "regulation_change"

@dataclass
class TechProperty:
    """Tech company property"""
    property_id: str
    name: str
    property_type: TechPropertyType
    base_price: float
    current_valuation: float
    revenue_multiple: float
    innovation_level: int
    employee_count: int
    tech_stack: List[str]
    market_cap: float
    growth_rate: float
    risk_factor: float
    patents_owned: int
    
    # Ownership
    owner_id: Optional[str] = None
    acquisition_price: float = 0.0
    development_level: int = 0
    
    # Performance
    monthly_revenue: float = 0.0
    user_base: int = 0
    market_share: float = 0.0

@dataclass
class TechPlayer:
    """Tech mogul player"""
    player_id: str
    name: str
    net_worth: float
    acc_balance: float
    
    # Tech empire
    owned_properties: List[str]
    portfolio_value: float
    innovation_points: int
    reputation_score: float
    
    # Specializations
    tech_expertise: Dict[str, int]  # AI, blockchain, biotech, etc.
    investment_strategy: str
    risk_tolerance: float

class TechMonopoly:
    """
    💻 TECH MONOPOLY - Silicon Valley Edition 💻
    
    Technology-themed monopoly game dengan startup ecosystem,
    venture capital, dan innovation challenges
    """
    
    def __init__(self):
        self.version = "∞.0.0"
        self.game_name = "Tech Monopoly: Silicon Valley Edition"
        self.theme = "Technology & Startups"
        
        # Game state
        self.properties: Dict[str, TechProperty] = {}
        self.players: Dict[str, TechPlayer] = {}
        self.active_games: Dict[str, Dict] = {}
        
        # Market conditions
        self.market_sentiment = 0.5  # 0.0 = bear, 1.0 = bull
        self.innovation_index = 100.0
        self.regulation_level = 0.3
        self.venture_capital_available = 1000000.0  # $1M
        
        # Tech trends
        self.trending_technologies = [
            "Artificial Intelligence", "Blockchain", "Quantum Computing",
            "Biotechnology", "Renewable Energy", "Space Technology",
            "Augmented Reality", "Internet of Things"
        ]
        
        # Initialize properties
        self._create_tech_properties()
        
        print("💻 Tech Monopoly initialized")
        print(f"   Game: {self.game_name}")
        print(f"   Properties: {len(self.properties)}")
        print(f"   Market Sentiment: {self.market_sentiment:.1%}")
    
    def _create_tech_properties(self):
        """Create tech company properties"""
        
        # Big Tech Companies
        big_tech_companies = [
            {
                "name": "Quantum Apple Corp",
                "base_price": 500000.0,
                "tech_stack": ["Hardware", "Software", "AI"],
                "market_cap": 2000000.0,
                "innovation_level": 9
            },
            {
                "name": "Consciousness Google",
                "base_price": 450000.0,
                "tech_stack": ["Search", "AI", "Cloud"],
                "market_cap": 1800000.0,
                "innovation_level": 10
            },
            {
                "name": "Interdimensional Microsoft",
                "base_price": 400000.0,
                "tech_stack": ["Cloud", "Enterprise", "Gaming"],
                "market_cap": 1600000.0,
                "innovation_level": 8
            },
            {
                "name": "Quantum Meta",
                "base_price": 350000.0,
                "tech_stack": ["Social", "VR", "AI"],
                "market_cap": 1400000.0,
                "innovation_level": 7
            }
        ]
        
        for company in big_tech_companies:
            property_id = f"tech-{uuid.uuid4().hex[:8]}"
            
            tech_property = TechProperty(
                property_id=property_id,
                name=company["name"],
                property_type=TechPropertyType.BIG_TECH,
                base_price=company["base_price"],
                current_valuation=company["base_price"],
                revenue_multiple=15.0,
                innovation_level=company["innovation_level"],
                employee_count=random.randint(50000, 200000),
                tech_stack=company["tech_stack"],
                market_cap=company["market_cap"],
                growth_rate=random.uniform(0.1, 0.3),
                risk_factor=random.uniform(0.1, 0.3),
                patents_owned=random.randint(1000, 10000)
            )
            
            self.properties[property_id] = tech_property
        
        # Unicorn Startups
        unicorn_startups = [
            {
                "name": "Consciousness AI Labs",
                "base_price": 100000.0,
                "tech_stack": ["AI", "Machine Learning"],
                "valuation": 1000000.0
            },
            {
                "name": "Quantum Blockchain Solutions",
                "base_price": 80000.0,
                "tech_stack": ["Blockchain", "Crypto"],
                "valuation": 800000.0
            },
            {
                "name": "Interdimensional VR",
                "base_price": 120000.0,
                "tech_stack": ["VR", "AR", "Gaming"],
                "valuation": 1200000.0
            },
            {
                "name": "Alien Biotech Corp",
                "base_price": 150000.0,
                "tech_stack": ["Biotech", "AI", "Healthcare"],
                "valuation": 1500000.0
            }
        ]
        
        for startup in unicorn_startups:
            property_id = f"unicorn-{uuid.uuid4().hex[:8]}"
            
            tech_property = TechProperty(
                property_id=property_id,
                name=startup["name"],
                property_type=TechPropertyType.UNICORN,
                base_price=startup["base_price"],
                current_valuation=startup["valuation"],
                revenue_multiple=25.0,
                innovation_level=random.randint(7, 10),
                employee_count=random.randint(500, 5000),
                tech_stack=startup["tech_stack"],
                market_cap=startup["valuation"],
                growth_rate=random.uniform(0.5, 2.0),
                risk_factor=random.uniform(0.3, 0.7),
                patents_owned=random.randint(10, 500)
            )
            
            self.properties[property_id] = tech_property
        
        # Venture Capital Firms
        vc_firms = [
            {
                "name": "Quantum Ventures",
                "base_price": 200000.0,
                "fund_size": 500000.0
            },
            {
                "name": "Consciousness Capital",
                "base_price": 250000.0,
                "fund_size": 750000.0
            },
            {
                "name": "Interdimensional Investments",
                "base_price": 300000.0,
                "fund_size": 1000000.0
            }
        ]
        
        for vc in vc_firms:
            property_id = f"vc-{uuid.uuid4().hex[:8]}"
            
            tech_property = TechProperty(
                property_id=property_id,
                name=vc["name"],
                property_type=TechPropertyType.VENTURE_CAPITAL,
                base_price=vc["base_price"],
                current_valuation=vc["fund_size"],
                revenue_multiple=5.0,
                innovation_level=5,
                employee_count=random.randint(50, 200),
                tech_stack=["Investment", "Due Diligence"],
                market_cap=vc["fund_size"],
                growth_rate=random.uniform(0.2, 0.5),
                risk_factor=random.uniform(0.2, 0.5),
                patents_owned=0
            )
            
            self.properties[property_id] = tech_property
        
        print(f"💻 Created {len(self.properties)} tech properties")
    
    def create_tech_player(self, name: str, starting_capital: float = 100000.0) -> str:
        """Create tech mogul player"""
        player_id = f"tech-player-{uuid.uuid4().hex[:8]}"
        
        # Random tech expertise
        tech_areas = ["AI", "Blockchain", "Biotech", "Hardware", "Software", "Cloud", "Gaming", "Fintech"]
        expertise = {}
        for area in random.sample(tech_areas, 3):
            expertise[area] = random.randint(1, 10)
        
        player = TechPlayer(
            player_id=player_id,
            name=name,
            net_worth=starting_capital,
            acc_balance=starting_capital * 0.1,  # 10% in ACC
            owned_properties=[],
            portfolio_value=0.0,
            innovation_points=random.randint(10, 50),
            reputation_score=random.uniform(0.5, 0.8),
            tech_expertise=expertise,
            investment_strategy=random.choice(["aggressive", "balanced", "conservative"]),
            risk_tolerance=random.uniform(0.3, 0.9)
        )
        
        self.players[player_id] = player
        
        print(f"💻 Created tech player: {name}")
        print(f"   Player ID: {player_id}")
        print(f"   Starting Capital: ${starting_capital:,.0f}")
        print(f"   Tech Expertise: {list(expertise.keys())}")
        print(f"   Investment Strategy: {player.investment_strategy}")
        
        return player_id
    
    def acquire_tech_property(self, player_id: str, property_id: str, 
                            acquisition_type: str = "purchase") -> Dict[str, Any]:
        """Acquire tech property"""
        if player_id not in self.players:
            raise ValueError("Player not found")
        if property_id not in self.properties:
            raise ValueError("Property not found")
        
        player = self.players[player_id]
        property = self.properties[property_id]
        
        if property.owner_id:
            raise ValueError("Property already owned")
        
        # Calculate acquisition price
        if acquisition_type == "purchase":
            price = property.current_valuation
        elif acquisition_type == "ipo":
            price = property.current_valuation * 0.8  # IPO discount
        elif acquisition_type == "acquisition":
            price = property.current_valuation * 1.2  # Acquisition premium
        else:
            price = property.current_valuation
        
        if player.net_worth < price:
            raise ValueError("Insufficient funds")
        
        # Process acquisition
        player.net_worth -= price
        player.owned_properties.append(property_id)
        player.portfolio_value += property.current_valuation
        
        property.owner_id = player_id
        property.acquisition_price = price
        
        # Innovation points bonus
        innovation_bonus = property.innovation_level * 2
        player.innovation_points += innovation_bonus
        
        # Reputation boost
        reputation_boost = 0.05 * (property.innovation_level / 10)
        player.reputation_score = min(1.0, player.reputation_score + reputation_boost)
        
        acquisition_result = {
            "player_id": player_id,
            "property_id": property_id,
            "property_name": property.name,
            "acquisition_type": acquisition_type,
            "price": price,
            "innovation_bonus": innovation_bonus,
            "reputation_boost": reputation_boost,
            "new_portfolio_value": player.portfolio_value,
            "remaining_net_worth": player.net_worth
        }
        
        print(f"💰 Tech acquisition: {player.name} acquired {property.name}")
        print(f"   Price: ${price:,.0f}")
        print(f"   Innovation Bonus: +{innovation_bonus} points")
        print(f"   Portfolio Value: ${player.portfolio_value:,.0f}")
        
        return acquisition_result
    
    def launch_ipo(self, player_id: str, property_id: str) -> Dict[str, Any]:
        """Launch IPO untuk owned startup"""
        if player_id not in self.players:
            raise ValueError("Player not found")
        if property_id not in self.properties:
            raise ValueError("Property not found")
        
        player = self.players[player_id]
        property = self.properties[property_id]
        
        if property.owner_id != player_id:
            raise ValueError("Player doesn't own this property")
        
        if property.property_type not in [TechPropertyType.STARTUP, TechPropertyType.UNICORN]:
            raise ValueError("Only startups can go public")
        
        # Calculate IPO valuation
        base_valuation = property.current_valuation
        market_multiplier = 1.0 + (self.market_sentiment - 0.5)
        innovation_multiplier = 1.0 + (property.innovation_level / 20)
        
        ipo_valuation = base_valuation * market_multiplier * innovation_multiplier
        
        # Player retains ownership but gains liquidity
        ipo_proceeds = ipo_valuation * 0.3  # 30% sold to public
        player.net_worth += ipo_proceeds
        player.acc_balance += ipo_proceeds * 0.1  # 10% in ACC
        
        # Update property
        property.current_valuation = ipo_valuation
        property.property_type = TechPropertyType.BIG_TECH  # Now public company
        property.market_cap = ipo_valuation
        
        # Innovation points bonus
        innovation_bonus = 50
        player.innovation_points += innovation_bonus
        
        ipo_result = {
            "player_id": player_id,
            "property_id": property_id,
            "property_name": property.name,
            "ipo_valuation": ipo_valuation,
            "ipo_proceeds": ipo_proceeds,
            "market_multiplier": market_multiplier,
            "innovation_multiplier": innovation_multiplier,
            "innovation_bonus": innovation_bonus,
            "new_net_worth": player.net_worth
        }
        
        print(f"📈 IPO Launch: {property.name}")
        print(f"   IPO Valuation: ${ipo_valuation:,.0f}")
        print(f"   Proceeds: ${ipo_proceeds:,.0f}")
        print(f"   Innovation Bonus: +{innovation_bonus} points")
        
        return ipo_result
    
    def invest_in_innovation(self, player_id: str, property_id: str, 
                           investment_amount: float) -> Dict[str, Any]:
        """Invest in R&D untuk property improvement"""
        if player_id not in self.players:
            raise ValueError("Player not found")
        if property_id not in self.properties:
            raise ValueError("Property not found")
        
        player = self.players[player_id]
        property = self.properties[property_id]
        
        if property.owner_id != player_id:
            raise ValueError("Player doesn't own this property")
        
        if player.net_worth < investment_amount:
            raise ValueError("Insufficient funds")
        
        # Process investment
        player.net_worth -= investment_amount
        
        # Calculate innovation improvements
        innovation_gain = investment_amount / 10000  # $10K per innovation point
        property.innovation_level = min(10, property.innovation_level + innovation_gain)
        
        # Valuation increase
        valuation_increase = investment_amount * 2  # 2x return on innovation
        property.current_valuation += valuation_increase
        player.portfolio_value += valuation_increase
        
        # Growth rate improvement
        growth_boost = investment_amount / 100000  # $100K for 1% growth boost
        property.growth_rate += growth_boost
        
        investment_result = {
            "player_id": player_id,
            "property_id": property_id,
            "investment_amount": investment_amount,
            "innovation_gain": innovation_gain,
            "valuation_increase": valuation_increase,
            "growth_boost": growth_boost,
            "new_innovation_level": property.innovation_level,
            "new_valuation": property.current_valuation
        }
        
        print(f"🔬 Innovation Investment: ${investment_amount:,.0f} in {property.name}")
        print(f"   Innovation Level: {property.innovation_level:.1f}/10")
        print(f"   Valuation Increase: ${valuation_increase:,.0f}")
        print(f"   Growth Boost: +{growth_boost:.2%}")
        
        return investment_result
    
    def trigger_tech_event(self) -> Dict[str, Any]:
        """Trigger random tech industry event"""
        event_type = random.choice(list(TechEvent))
        
        event_effects = {
            TechEvent.TECH_BUBBLE: {
                "market_sentiment_change": random.uniform(-0.3, -0.1),
                "valuation_multiplier": random.uniform(0.7, 0.9),
                "description": "Tech bubble burst! Valuations drop across the board."
            },
            TechEvent.INNOVATION_BREAKTHROUGH: {
                "innovation_index_change": random.uniform(10, 30),
                "valuation_multiplier": random.uniform(1.1, 1.3),
                "description": "Major innovation breakthrough! Tech valuations surge."
            },
            TechEvent.REGULATION_CHANGE: {
                "regulation_level_change": random.uniform(-0.2, 0.2),
                "market_sentiment_change": random.uniform(-0.1, 0.1),
                "description": "New tech regulations announced. Market reacts."
            },
            TechEvent.CYBER_ATTACK: {
                "market_sentiment_change": random.uniform(-0.2, -0.05),
                "security_focus_boost": True,
                "description": "Major cyber attack affects tech confidence."
            }
        }
        
        effect = event_effects.get(event_type, {})
        
        # Apply effects
        if "market_sentiment_change" in effect:
            self.market_sentiment = max(0.0, min(1.0, 
                self.market_sentiment + effect["market_sentiment_change"]))
        
        if "innovation_index_change" in effect:
            self.innovation_index += effect["innovation_index_change"]
        
        if "regulation_level_change" in effect:
            self.regulation_level = max(0.0, min(1.0,
                self.regulation_level + effect["regulation_level_change"]))
        
        if "valuation_multiplier" in effect:
            # Apply to all properties
            for property in self.properties.values():
                property.current_valuation *= effect["valuation_multiplier"]
        
        event_result = {
            "event_type": event_type.value,
            "description": effect.get("description", "Tech industry event occurred."),
            "effects": effect,
            "new_market_sentiment": self.market_sentiment,
            "new_innovation_index": self.innovation_index,
            "new_regulation_level": self.regulation_level
        }
        
        print(f"📰 Tech Event: {event_type.value}")
        print(f"   {effect.get('description', 'Event occurred.')}")
        print(f"   Market Sentiment: {self.market_sentiment:.1%}")
        
        return event_result
    
    def get_player_stats(self, player_id: str) -> Dict[str, Any]:
        """Get comprehensive player statistics"""
        if player_id not in self.players:
            raise ValueError("Player not found")
        
        player = self.players[player_id]
        
        # Calculate portfolio performance
        owned_properties = [self.properties[pid] for pid in player.owned_properties]
        total_acquisition_cost = sum(prop.acquisition_price for prop in owned_properties)
        current_portfolio_value = sum(prop.current_valuation for prop in owned_properties)
        portfolio_return = ((current_portfolio_value - total_acquisition_cost) / 
                          max(1, total_acquisition_cost)) if total_acquisition_cost > 0 else 0
        
        # Calculate innovation score
        total_innovation = sum(prop.innovation_level for prop in owned_properties)
        avg_innovation = total_innovation / max(1, len(owned_properties))
        
        return {
            "player_id": player.player_id,
            "name": player.name,
            "net_worth": player.net_worth,
            "acc_balance": player.acc_balance,
            "portfolio_value": current_portfolio_value,
            "portfolio_return": portfolio_return,
            "properties_owned": len(player.owned_properties),
            "innovation_points": player.innovation_points,
            "reputation_score": player.reputation_score,
            "avg_innovation_level": avg_innovation,
            "tech_expertise": player.tech_expertise,
            "investment_strategy": player.investment_strategy,
            "risk_tolerance": player.risk_tolerance,
            "total_acquisition_cost": total_acquisition_cost
        }
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Get tech market overview"""
        total_market_cap = sum(prop.market_cap for prop in self.properties.values())
        avg_innovation = sum(prop.innovation_level for prop in self.properties.values()) / len(self.properties)
        
        # Property type distribution
        type_distribution = {}
        for prop in self.properties.values():
            prop_type = prop.property_type.value
            if prop_type not in type_distribution:
                type_distribution[prop_type] = 0
            type_distribution[prop_type] += 1
        
        return {
            "total_properties": len(self.properties),
            "total_market_cap": total_market_cap,
            "average_innovation_level": avg_innovation,
            "market_sentiment": self.market_sentiment,
            "innovation_index": self.innovation_index,
            "regulation_level": self.regulation_level,
            "venture_capital_available": self.venture_capital_available,
            "trending_technologies": self.trending_technologies,
            "property_type_distribution": type_distribution,
            "total_players": len(self.players)
        }

# Demo dan testing
if __name__ == "__main__":
    print("💻 TECH MONOPOLY DEMO 💻")
    
    # Initialize Tech Monopoly
    tech_game = TechMonopoly()
    
    # Create demo players
    print("\n👨‍💼 Creating Tech Moguls...")
    player1 = tech_game.create_tech_player("Elon Quantum", 500000.0)
    player2 = tech_game.create_tech_player("Consciousness Gates", 750000.0)
    
    # Show market overview
    print("\n📊 Tech Market Overview:")
    market = tech_game.get_market_overview()
    print(f"   Total Properties: {market['total_properties']}")
    print(f"   Market Cap: ${market['total_market_cap']:,.0f}")
    print(f"   Market Sentiment: {market['market_sentiment']:.1%}")
    print(f"   Innovation Index: {market['innovation_index']:.1f}")
    
    # Acquire properties
    print("\n💰 Property Acquisitions...")
    available_properties = list(tech_game.properties.keys())[:3]
    
    for i, prop_id in enumerate(available_properties):
        player_id = player1 if i % 2 == 0 else player2
        try:
            acquisition = tech_game.acquire_tech_property(player_id, prop_id)
        except ValueError as e:
            print(f"   Failed to acquire property: {e}")
    
    # Innovation investment
    print("\n🔬 Innovation Investments...")
    player1_props = tech_game.players[player1].owned_properties
    if player1_props:
        investment = tech_game.invest_in_innovation(player1, player1_props[0], 50000.0)
    
    # Launch IPO
    print("\n📈 IPO Launch...")
    if player1_props:
        try:
            ipo = tech_game.launch_ipo(player1, player1_props[0])
        except ValueError as e:
            print(f"   IPO failed: {e}")
    
    # Trigger tech event
    print("\n📰 Tech Industry Event...")
    event = tech_game.trigger_tech_event()
    
    # Show player stats
    print("\n👨‍💼 Player Statistics:")
    for player_id in [player1, player2]:
        stats = tech_game.get_player_stats(player_id)
        print(f"   {stats['name']}:")
        print(f"      Net Worth: ${stats['net_worth']:,.0f}")
        print(f"      Portfolio Value: ${stats['portfolio_value']:,.0f}")
        print(f"      Properties: {stats['properties_owned']}")
        print(f"      Innovation Points: {stats['innovation_points']}")
        print(f"      Reputation: {stats['reputation_score']:.2f}")
    
    print("\n✅ Tech Monopoly demo completed!")
    print("💻 Ready for Silicon Valley domination!")