#!/usr/bin/env python3
"""
💰 Alien Crypto - Real Cryptocurrency Analysis Tool
==================================================

Real cryptocurrency analysis and monitoring tools:
- Price tracking and alerts
- Portfolio analysis
- Market trend analysis
- Technical indicators
- Risk assessment

Usage:
    alien-crypto price <symbol>     - Get current price
    alien-crypto track <symbols>    - Track multiple coins
    alien-crypto portfolio         - Analyze portfolio
    alien-crypto trends            - Market trend analysis
    alien-crypto alerts <symbol>   - Set price alerts
"""

import sys
import argparse
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class CryptoAnalyzer:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Alien-Crypto-Analyzer/1.0'
        })
    
    def get_price(self, symbol: str) -> Dict[str, Any]:
        """Get current price for a cryptocurrency"""
        try:
            # Convert symbol to CoinGecko ID format
            symbol = symbol.lower()
            
            # Common symbol mappings
            symbol_map = {
                'btc': 'bitcoin',
                'eth': 'ethereum',
                'ada': 'cardano',
                'dot': 'polkadot',
                'sol': 'solana',
                'matic': 'polygon',
                'avax': 'avalanche-2',
                'atom': 'cosmos',
                'link': 'chainlink',
                'uni': 'uniswap'
            }
            
            coin_id = symbol_map.get(symbol, symbol)
            
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_market_cap': 'true',
                'include_24hr_vol': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if coin_id not in data:
                return {"error": f"Cryptocurrency '{symbol}' not found"}
            
            coin_data = data[coin_id]
            
            return {
                "symbol": symbol.upper(),
                "coin_id": coin_id,
                "price_usd": coin_data.get('usd', 0),
                "change_24h": coin_data.get('usd_24h_change', 0),
                "market_cap": coin_data.get('usd_market_cap', 0),
                "volume_24h": coin_data.get('usd_24h_vol', 0),
                "timestamp": datetime.now().isoformat()
            }
        
        except requests.RequestException as e:
            return {"error": f"Network error: {str(e)}"}
        except Exception as e:
            return {"error": f"Error getting price: {str(e)}"}
    
    def track_multiple(self, symbols: List[str]) -> Dict[str, Any]:
        """Track multiple cryptocurrencies"""
        results = {}
        
        for symbol in symbols:
            result = self.get_price(symbol)
            results[symbol] = result
            time.sleep(0.1)  # Rate limiting
        
        return {
            "tracked_coins": len(symbols),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def analyze_trends(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """Analyze price trends for a cryptocurrency"""
        try:
            symbol = symbol.lower()
            symbol_map = {
                'btc': 'bitcoin',
                'eth': 'ethereum',
                'ada': 'cardano',
                'dot': 'polkadot'
            }
            coin_id = symbol_map.get(symbol, symbol)
            
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            prices = data.get('prices', [])
            
            if not prices:
                return {"error": "No price data available"}
            
            # Calculate trend metrics
            price_values = [price[1] for price in prices]
            start_price = price_values[0]
            end_price = price_values[-1]
            max_price = max(price_values)
            min_price = min(price_values)
            
            trend_change = ((end_price - start_price) / start_price) * 100
            volatility = ((max_price - min_price) / min_price) * 100
            
            # Determine trend direction
            if trend_change > 5:
                trend = "Strong Uptrend"
            elif trend_change > 1:
                trend = "Uptrend"
            elif trend_change > -1:
                trend = "Sideways"
            elif trend_change > -5:
                trend = "Downtrend"
            else:
                trend = "Strong Downtrend"
            
            return {
                "symbol": symbol.upper(),
                "period_days": days,
                "start_price": start_price,
                "end_price": end_price,
                "max_price": max_price,
                "min_price": min_price,
                "trend_change_percent": round(trend_change, 2),
                "volatility_percent": round(volatility, 2),
                "trend_direction": trend,
                "data_points": len(prices)
            }
        
        except requests.RequestException as e:
            return {"error": f"Network error: {str(e)}"}
        except Exception as e:
            return {"error": f"Error analyzing trends: {str(e)}"}
    
    def portfolio_analysis(self, holdings: Dict[str, float]) -> Dict[str, Any]:
        """Analyze a cryptocurrency portfolio"""
        portfolio_value = 0
        portfolio_change = 0
        coin_analysis = {}
        
        for symbol, amount in holdings.items():
            price_data = self.get_price(symbol)
            
            if 'error' not in price_data:
                current_value = price_data['price_usd'] * amount
                change_24h = price_data['change_24h']
                
                portfolio_value += current_value
                portfolio_change += (current_value * change_24h / 100)
                
                coin_analysis[symbol] = {
                    "amount": amount,
                    "price_usd": price_data['price_usd'],
                    "value_usd": current_value,
                    "change_24h": change_24h,
                    "portfolio_weight": 0  # Will calculate after total
                }
            else:
                coin_analysis[symbol] = {"error": price_data['error']}
        
        # Calculate portfolio weights
        for symbol in coin_analysis:
            if 'value_usd' in coin_analysis[symbol]:
                coin_analysis[symbol]['portfolio_weight'] = round(
                    (coin_analysis[symbol]['value_usd'] / portfolio_value) * 100, 2
                ) if portfolio_value > 0 else 0
        
        portfolio_change_percent = (portfolio_change / portfolio_value) * 100 if portfolio_value > 0 else 0
        
        return {
            "total_value_usd": round(portfolio_value, 2),
            "change_24h_usd": round(portfolio_change, 2),
            "change_24h_percent": round(portfolio_change_percent, 2),
            "holdings": coin_analysis,
            "analysis_time": datetime.now().isoformat()
        }
    
    def risk_assessment(self, symbol: str) -> Dict[str, Any]:
        """Assess risk level of a cryptocurrency"""
        try:
            # Get price data and trends
            price_data = self.get_price(symbol)
            trend_data = self.analyze_trends(symbol, 30)
            
            if 'error' in price_data or 'error' in trend_data:
                return {"error": "Unable to assess risk - insufficient data"}
            
            # Risk factors
            volatility = trend_data.get('volatility_percent', 0)
            market_cap = price_data.get('market_cap', 0)
            volume_24h = price_data.get('volume_24h', 0)
            change_24h = abs(price_data.get('change_24h', 0))
            
            # Risk scoring
            risk_score = 0
            
            # Volatility risk (0-40 points)
            if volatility > 50:
                risk_score += 40
            elif volatility > 30:
                risk_score += 30
            elif volatility > 15:
                risk_score += 20
            else:
                risk_score += 10
            
            # Market cap risk (0-30 points)
            if market_cap < 100_000_000:  # < $100M
                risk_score += 30
            elif market_cap < 1_000_000_000:  # < $1B
                risk_score += 20
            elif market_cap < 10_000_000_000:  # < $10B
                risk_score += 10
            else:
                risk_score += 5
            
            # Daily change risk (0-20 points)
            if change_24h > 20:
                risk_score += 20
            elif change_24h > 10:
                risk_score += 15
            elif change_24h > 5:
                risk_score += 10
            else:
                risk_score += 5
            
            # Volume risk (0-10 points)
            volume_to_mcap = (volume_24h / market_cap) * 100 if market_cap > 0 else 0
            if volume_to_mcap < 1:
                risk_score += 10
            elif volume_to_mcap < 5:
                risk_score += 5
            
            # Risk level classification
            if risk_score >= 80:
                risk_level = "Very High"
            elif risk_score >= 60:
                risk_level = "High"
            elif risk_score >= 40:
                risk_level = "Medium"
            elif risk_score >= 20:
                risk_level = "Low"
            else:
                risk_level = "Very Low"
            
            return {
                "symbol": symbol.upper(),
                "risk_score": risk_score,
                "risk_level": risk_level,
                "factors": {
                    "volatility_30d": round(volatility, 2),
                    "market_cap_usd": market_cap,
                    "daily_change": round(change_24h, 2),
                    "volume_to_mcap_ratio": round(volume_to_mcap, 2)
                },
                "recommendation": self.get_risk_recommendation(risk_level)
            }
        
        except Exception as e:
            return {"error": f"Error assessing risk: {str(e)}"}
    
    def get_risk_recommendation(self, risk_level: str) -> str:
        """Get investment recommendation based on risk level"""
        recommendations = {
            "Very Low": "Suitable for conservative investors. Consider for long-term holding.",
            "Low": "Good for most investors. Suitable for portfolio allocation.",
            "Medium": "Moderate risk. Suitable for experienced investors with risk tolerance.",
            "High": "High risk investment. Only for experienced traders with high risk tolerance.",
            "Very High": "Extremely risky. Only for speculation with money you can afford to lose."
        }
        return recommendations.get(risk_level, "Unable to provide recommendation")

def main():
    parser = argparse.ArgumentParser(description="💰 Alien Crypto - Real Cryptocurrency Analysis Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Price command
    price_parser = subparsers.add_parser('price', help='Get current price')
    price_parser.add_argument('symbol', help='Cryptocurrency symbol (e.g., BTC, ETH)')
    
    # Track command
    track_parser = subparsers.add_parser('track', help='Track multiple cryptocurrencies')
    track_parser.add_argument('symbols', nargs='+', help='Cryptocurrency symbols to track')
    
    # Portfolio command
    portfolio_parser = subparsers.add_parser('portfolio', help='Analyze portfolio')
    portfolio_parser.add_argument('--file', help='JSON file with holdings (symbol: amount)')
    
    # Trends command
    trends_parser = subparsers.add_parser('trends', help='Analyze market trends')
    trends_parser.add_argument('symbol', help='Cryptocurrency symbol')
    trends_parser.add_argument('--days', type=int, default=7, help='Number of days to analyze')
    
    # Risk command
    risk_parser = subparsers.add_parser('risk', help='Assess investment risk')
    risk_parser.add_argument('symbol', help='Cryptocurrency symbol')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("💰 Alien Crypto - Real Cryptocurrency Analysis Tool")
    print("=" * 55)
    
    analyzer = CryptoAnalyzer()
    
    if args.command == 'price':
        result = analyzer.get_price(args.symbol)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            change_icon = "📈" if result['change_24h'] > 0 else "📉"
            print(f"💰 {result['symbol']} Price Information:")
            print(f"   Current Price: ${result['price_usd']:,.2f}")
            print(f"   24h Change: {change_icon} {result['change_24h']:+.2f}%")
            print(f"   Market Cap: ${result['market_cap']:,.0f}")
            print(f"   24h Volume: ${result['volume_24h']:,.0f}")
    
    elif args.command == 'track':
        result = analyzer.track_multiple(args.symbols)
        print(f"📊 Tracking {result['tracked_coins']} cryptocurrencies:")
        for symbol, data in result['results'].items():
            if 'error' in data:
                print(f"   ❌ {symbol.upper()}: {data['error']}")
            else:
                change_icon = "📈" if data['change_24h'] > 0 else "📉"
                print(f"   💰 {data['symbol']}: ${data['price_usd']:,.2f} {change_icon} {data['change_24h']:+.2f}%")
    
    elif args.command == 'portfolio':
        # Example portfolio if no file provided
        if args.file:
            try:
                with open(args.file, 'r') as f:
                    holdings = json.load(f)
            except Exception as e:
                print(f"❌ Error reading portfolio file: {e}")
                return
        else:
            print("📝 Using example portfolio (use --file to specify your own):")
            holdings = {"btc": 0.1, "eth": 2.0, "ada": 1000}
        
        result = analyzer.portfolio_analysis(holdings)
        print(f"💼 Portfolio Analysis:")
        print(f"   Total Value: ${result['total_value_usd']:,.2f}")
        change_icon = "📈" if result['change_24h_percent'] > 0 else "📉"
        print(f"   24h Change: {change_icon} ${result['change_24h_usd']:+,.2f} ({result['change_24h_percent']:+.2f}%)")
        print(f"\\n   Holdings:")
        for symbol, data in result['holdings'].items():
            if 'error' not in data:
                print(f"     {symbol.upper()}: {data['amount']} coins = ${data['value_usd']:,.2f} ({data['portfolio_weight']}%)")
    
    elif args.command == 'trends':
        result = analyzer.analyze_trends(args.symbol, args.days)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            trend_icon = {"Strong Uptrend": "🚀", "Uptrend": "📈", "Sideways": "➡️", 
                         "Downtrend": "📉", "Strong Downtrend": "💥"}.get(result['trend_direction'], "📊")
            print(f"📈 {result['symbol']} Trend Analysis ({result['period_days']} days):")
            print(f"   Trend: {trend_icon} {result['trend_direction']}")
            print(f"   Price Change: {result['trend_change_percent']:+.2f}%")
            print(f"   Volatility: {result['volatility_percent']:.2f}%")
            print(f"   Price Range: ${result['min_price']:,.2f} - ${result['max_price']:,.2f}")
    
    elif args.command == 'risk':
        result = analyzer.risk_assessment(args.symbol)
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            risk_icons = {"Very Low": "🟢", "Low": "🟡", "Medium": "🟠", "High": "🔴", "Very High": "⚫"}
            risk_icon = risk_icons.get(result['risk_level'], "❓")
            print(f"⚠️ {result['symbol']} Risk Assessment:")
            print(f"   Risk Level: {risk_icon} {result['risk_level']} (Score: {result['risk_score']}/100)")
            print(f"   Volatility: {result['factors']['volatility_30d']}%")
            print(f"   Market Cap: ${result['factors']['market_cap_usd']:,.0f}")
            print(f"   Daily Change: {result['factors']['daily_change']}%")
            print(f"\\n   💡 Recommendation: {result['recommendation']}")

if __name__ == "__main__":
    main()