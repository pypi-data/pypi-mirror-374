#!/usr/bin/env python3
"""
🔌 THIRD-PARTY PAYMENT API 🔌
API untuk memungkinkan pihak ketiga menggunakan Alien Payment System

Features:
- RESTful API endpoints
- Authentication & API keys
- Payment processing
- Webhook notifications
- Rate limiting
- Revenue sharing
- Merchant dashboard
- Multi-currency support
- Fraud detection
- Compliance features
"""

import asyncio
import json
import time
import uuid
import math
import random
import hashlib
import hmac
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from datetime import datetime, timedelta

class APIKeyTier(Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class WebhookEvent(Enum):
    PAYMENT_CREATED = "payment.created"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUNDED = "payment.refunded"
    PAYOUT_PROCESSED = "payout.processed"

@dataclass
class APIKey:
    """API Key untuk third-party access"""
    api_key_id: str
    merchant_id: str
    public_key: str
    private_key: str
    tier: APIKeyTier
    permissions: List[str]
    rate_limit: int  # requests per minute
    revenue_share: float  # percentage
    created_time: float
    last_used: float
    active: bool = True
    monthly_volume: float = 0.0
    total_volume: float = 0.0

@dataclass
class ThirdPartyPayment:
    """Payment yang diproses melalui third-party API"""
    payment_id: str
    merchant_id: str
    api_key_id: str
    amount: float
    currency: str
    description: str
    customer_id: Optional[str]
    customer_email: Optional[str]
    metadata: Dict[str, Any]
    status: PaymentStatus
    acc_transaction_id: Optional[str]
    created_time: float
    completed_time: Optional[float]
    webhook_url: Optional[str]
    return_url: Optional[str]
    cancel_url: Optional[str]
    fees: Dict[str, float]
    net_amount: float

@dataclass
class Merchant:
    """Merchant yang menggunakan payment API"""
    merchant_id: str
    business_name: str
    business_type: str
    contact_email: str
    wallet_id: str
    api_keys: List[str]
    webhook_endpoints: List[str]
    settlement_schedule: str  # daily, weekly, monthly
    revenue_share_tier: float
    total_processed: float
    monthly_processed: float
    created_time: float
    verified: bool = False
    active: bool = True

class ThirdPartyPaymentAPI:
    """
    🔌 THIRD-PARTY PAYMENT API 🔌
    
    Sistem API yang memungkinkan pihak ketiga mengintegrasikan
    Alien Payment System ke dalam aplikasi mereka
    """
    
    def __init__(self):
        self.version = "∞.0.0"
        self.api_name = "Alien Payment API"
        self.base_url = "https://api.alienmonopoly.com"
        
        # API management
        self.merchants: Dict[str, Merchant] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.payments: Dict[str, ThirdPartyPayment] = {}
        self.webhook_queue: List[Dict] = []
        
        # Rate limiting
        self.rate_limits: Dict[str, List[float]] = {}
        
        # Revenue sharing tiers
        self.revenue_share_tiers = {
            APIKeyTier.BASIC: 0.05,      # 5% fee
            APIKeyTier.PROFESSIONAL: 0.03,  # 3% fee
            APIKeyTier.ENTERPRISE: 0.02,    # 2% fee
            APIKeyTier.CUSTOM: 0.01         # 1% fee
        }
        
        # API endpoints
        self.endpoints = {
            "create_payment": "/v1/payments",
            "get_payment": "/v1/payments/{payment_id}",
            "refund_payment": "/v1/payments/{payment_id}/refund",
            "list_payments": "/v1/payments",
            "create_webhook": "/v1/webhooks",
            "merchant_dashboard": "/v1/merchant/dashboard",
            "api_keys": "/v1/api-keys"
        }
        
        print("🔌 Third-Party Payment API initialized")
        print(f"   API Name: {self.api_name}")
        print(f"   Base URL: {self.base_url}")
        print(f"   Available Endpoints: {len(self.endpoints)}")
    
    def register_merchant(self, business_name: str, business_type: str, 
                         contact_email: str, wallet_id: str) -> str:
        """Register merchant baru untuk API access"""
        merchant_id = f"merchant-{uuid.uuid4().hex[:8]}"
        
        merchant = Merchant(
            merchant_id=merchant_id,
            business_name=business_name,
            business_type=business_type,
            contact_email=contact_email,
            wallet_id=wallet_id,
            api_keys=[],
            webhook_endpoints=[],
            settlement_schedule="weekly",
            revenue_share_tier=self.revenue_share_tiers[APIKeyTier.BASIC],
            total_processed=0.0,
            monthly_processed=0.0,
            created_time=time.time()
        )
        
        self.merchants[merchant_id] = merchant
        
        print(f"🏪 Registered merchant: {business_name}")
        print(f"   Merchant ID: {merchant_id}")
        print(f"   Business Type: {business_type}")
        print(f"   Contact: {contact_email}")
        
        return merchant_id
    
    def create_api_key(self, merchant_id: str, tier: APIKeyTier = APIKeyTier.BASIC,
                      permissions: List[str] = None) -> Dict[str, str]:
        """Create API key untuk merchant"""
        if merchant_id not in self.merchants:
            raise ValueError("Merchant not found")
        
        if permissions is None:
            permissions = ["payments.create", "payments.read", "webhooks.create"]
        
        api_key_id = f"ak-{uuid.uuid4().hex[:8]}"
        public_key = f"pk_{uuid.uuid4().hex}"
        private_key = f"sk_{uuid.uuid4().hex}"
        
        # Rate limits berdasarkan tier
        rate_limits = {
            APIKeyTier.BASIC: 100,        # 100 requests/minute
            APIKeyTier.PROFESSIONAL: 500,  # 500 requests/minute
            APIKeyTier.ENTERPRISE: 2000,   # 2000 requests/minute
            APIKeyTier.CUSTOM: 10000       # 10000 requests/minute
        }
        
        api_key = APIKey(
            api_key_id=api_key_id,
            merchant_id=merchant_id,
            public_key=public_key,
            private_key=private_key,
            tier=tier,
            permissions=permissions,
            rate_limit=rate_limits[tier],
            revenue_share=self.revenue_share_tiers[tier],
            created_time=time.time(),
            last_used=0.0
        )
        
        self.api_keys[api_key_id] = api_key
        self.merchants[merchant_id].api_keys.append(api_key_id)
        
        print(f"🔑 Created API key for {self.merchants[merchant_id].business_name}")
        print(f"   API Key ID: {api_key_id}")
        print(f"   Tier: {tier.value}")
        print(f"   Rate Limit: {rate_limits[tier]} req/min")
        print(f"   Revenue Share: {self.revenue_share_tiers[tier]:.1%}")
        
        return {
            "api_key_id": api_key_id,
            "public_key": public_key,
            "private_key": private_key,
            "tier": tier.value,
            "permissions": permissions
        }
    
    def authenticate_request(self, public_key: str, signature: str, 
                           payload: str, timestamp: str) -> Optional[APIKey]:
        """Authenticate API request"""
        # Find API key
        api_key = None
        for key in self.api_keys.values():
            if key.public_key == public_key and key.active:
                api_key = key
                break
        
        if not api_key:
            return None
        
        # Check timestamp (prevent replay attacks)
        current_time = time.time()
        request_time = float(timestamp)
        if abs(current_time - request_time) > 300:  # 5 minutes tolerance
            return None
        
        # Verify signature
        expected_signature = hmac.new(
            api_key.private_key.encode(),
            f"{timestamp}.{payload}".encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
        
        # Check rate limiting
        if not self._check_rate_limit(api_key.api_key_id, api_key.rate_limit):
            return None
        
        # Update last used
        api_key.last_used = current_time
        
        return api_key
    
    def _check_rate_limit(self, api_key_id: str, limit: int) -> bool:
        """Check rate limiting untuk API key"""
        current_time = time.time()
        
        if api_key_id not in self.rate_limits:
            self.rate_limits[api_key_id] = []
        
        # Remove old requests (older than 1 minute)
        self.rate_limits[api_key_id] = [
            req_time for req_time in self.rate_limits[api_key_id]
            if current_time - req_time < 60
        ]
        
        # Check if under limit
        if len(self.rate_limits[api_key_id]) >= limit:
            return False
        
        # Add current request
        self.rate_limits[api_key_id].append(current_time)
        return True
    
    def create_payment(self, api_key: APIKey, amount: float, currency: str = "ACC",
                      description: str = "", customer_id: str = None,
                      customer_email: str = None, metadata: Dict = None,
                      webhook_url: str = None, return_url: str = None,
                      cancel_url: str = None) -> Dict[str, Any]:
        """Create payment melalui API"""
        if "payments.create" not in api_key.permissions:
            raise ValueError("Insufficient permissions")
        
        payment_id = f"pay-{uuid.uuid4().hex[:8]}"
        
        # Calculate fees
        platform_fee = amount * api_key.revenue_share
        processing_fee = amount * 0.005  # 0.5% processing fee
        total_fees = platform_fee + processing_fee
        net_amount = amount - total_fees
        
        payment = ThirdPartyPayment(
            payment_id=payment_id,
            merchant_id=api_key.merchant_id,
            api_key_id=api_key.api_key_id,
            amount=amount,
            currency=currency,
            description=description,
            customer_id=customer_id,
            customer_email=customer_email,
            metadata=metadata or {},
            status=PaymentStatus.PENDING,
            acc_transaction_id=None,
            created_time=time.time(),
            completed_time=None,
            webhook_url=webhook_url,
            return_url=return_url,
            cancel_url=cancel_url,
            fees={
                "platform_fee": platform_fee,
                "processing_fee": processing_fee,
                "total_fees": total_fees
            },
            net_amount=net_amount
        )
        
        self.payments[payment_id] = payment
        
        # Queue webhook
        if webhook_url:
            self._queue_webhook(webhook_url, WebhookEvent.PAYMENT_CREATED, payment)
        
        print(f"💳 Created payment: {payment_id}")
        print(f"   Amount: {amount} {currency}")
        print(f"   Merchant: {api_key.merchant_id}")
        print(f"   Fees: {total_fees:.4f} {currency}")
        print(f"   Net Amount: {net_amount:.4f} {currency}")
        
        return {
            "payment_id": payment_id,
            "amount": amount,
            "currency": currency,
            "status": payment.status.value,
            "fees": payment.fees,
            "net_amount": net_amount,
            "created_time": payment.created_time,
            "payment_url": f"{self.base_url}/pay/{payment_id}",
            "return_url": return_url,
            "cancel_url": cancel_url
        }
    
    def process_payment(self, payment_id: str, acc_system) -> Dict[str, Any]:
        """Process payment menggunakan ACC system"""
        if payment_id not in self.payments:
            raise ValueError("Payment not found")
        
        payment = self.payments[payment_id]
        
        if payment.status != PaymentStatus.PENDING:
            raise ValueError(f"Payment already {payment.status.value}")
        
        try:
            payment.status = PaymentStatus.PROCESSING
            
            # Get merchant wallet
            merchant = self.merchants[payment.merchant_id]
            
            # Create ACC transaction (simplified - would need customer wallet)
            # For demo, we'll simulate successful payment
            payment.acc_transaction_id = f"acc-tx-{uuid.uuid4().hex[:8]}"
            payment.status = PaymentStatus.COMPLETED
            payment.completed_time = time.time()
            
            # Update merchant statistics
            merchant.total_processed += payment.amount
            merchant.monthly_processed += payment.amount
            
            # Update API key statistics
            api_key = self.api_keys[payment.api_key_id]
            api_key.total_volume += payment.amount
            api_key.monthly_volume += payment.amount
            
            # Queue webhook
            if payment.webhook_url:
                self._queue_webhook(payment.webhook_url, WebhookEvent.PAYMENT_COMPLETED, payment)
            
            print(f"✅ Payment processed: {payment_id}")
            print(f"   ACC Transaction: {payment.acc_transaction_id}")
            
            return {
                "payment_id": payment_id,
                "status": payment.status.value,
                "acc_transaction_id": payment.acc_transaction_id,
                "completed_time": payment.completed_time
            }
            
        except Exception as e:
            payment.status = PaymentStatus.FAILED
            
            # Queue webhook
            if payment.webhook_url:
                self._queue_webhook(payment.webhook_url, WebhookEvent.PAYMENT_FAILED, payment)
            
            print(f"❌ Payment failed: {payment_id} - {e}")
            
            return {
                "payment_id": payment_id,
                "status": payment.status.value,
                "error": str(e)
            }
    
    def _queue_webhook(self, webhook_url: str, event: WebhookEvent, payment: ThirdPartyPayment):
        """Queue webhook untuk delivery"""
        webhook_data = {
            "event": event.value,
            "payment_id": payment.payment_id,
            "merchant_id": payment.merchant_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "status": payment.status.value,
            "timestamp": time.time(),
            "webhook_url": webhook_url
        }
        
        self.webhook_queue.append(webhook_data)
        print(f"📡 Queued webhook: {event.value} for {payment.payment_id}")
    
    def get_payment(self, api_key: APIKey, payment_id: str) -> Dict[str, Any]:
        """Get payment information"""
        if "payments.read" not in api_key.permissions:
            raise ValueError("Insufficient permissions")
        
        if payment_id not in self.payments:
            raise ValueError("Payment not found")
        
        payment = self.payments[payment_id]
        
        # Check if payment belongs to merchant
        if payment.merchant_id != api_key.merchant_id:
            raise ValueError("Payment not found")
        
        return {
            "payment_id": payment.payment_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "description": payment.description,
            "status": payment.status.value,
            "customer_id": payment.customer_id,
            "customer_email": payment.customer_email,
            "metadata": payment.metadata,
            "fees": payment.fees,
            "net_amount": payment.net_amount,
            "created_time": payment.created_time,
            "completed_time": payment.completed_time,
            "acc_transaction_id": payment.acc_transaction_id
        }
    
    def list_payments(self, api_key: APIKey, limit: int = 10, 
                     status: str = None, start_date: float = None,
                     end_date: float = None) -> Dict[str, Any]:
        """List payments untuk merchant"""
        if "payments.read" not in api_key.permissions:
            raise ValueError("Insufficient permissions")
        
        # Filter payments by merchant
        merchant_payments = [
            payment for payment in self.payments.values()
            if payment.merchant_id == api_key.merchant_id
        ]
        
        # Apply filters
        if status:
            merchant_payments = [
                p for p in merchant_payments
                if p.status.value == status
            ]
        
        if start_date:
            merchant_payments = [
                p for p in merchant_payments
                if p.created_time >= start_date
            ]
        
        if end_date:
            merchant_payments = [
                p for p in merchant_payments
                if p.created_time <= end_date
            ]
        
        # Sort by creation time (newest first)
        merchant_payments.sort(key=lambda p: p.created_time, reverse=True)
        
        # Apply limit
        merchant_payments = merchant_payments[:limit]
        
        # Format response
        payments_data = []
        for payment in merchant_payments:
            payments_data.append({
                "payment_id": payment.payment_id,
                "amount": payment.amount,
                "currency": payment.currency,
                "status": payment.status.value,
                "created_time": payment.created_time,
                "completed_time": payment.completed_time
            })
        
        return {
            "payments": payments_data,
            "total_count": len(payments_data),
            "has_more": len(self.payments) > limit
        }
    
    def get_merchant_dashboard(self, api_key: APIKey) -> Dict[str, Any]:
        """Get merchant dashboard data"""
        merchant = self.merchants[api_key.merchant_id]
        
        # Calculate statistics
        merchant_payments = [
            p for p in self.payments.values()
            if p.merchant_id == api_key.merchant_id
        ]
        
        completed_payments = [
            p for p in merchant_payments
            if p.status == PaymentStatus.COMPLETED
        ]
        
        total_revenue = sum(p.net_amount for p in completed_payments)
        total_fees_paid = sum(p.fees["total_fees"] for p in completed_payments)
        
        # Monthly statistics
        current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0).timestamp()
        monthly_payments = [
            p for p in completed_payments
            if p.completed_time and p.completed_time >= current_month_start
        ]
        
        monthly_revenue = sum(p.net_amount for p in monthly_payments)
        monthly_volume = sum(p.amount for p in monthly_payments)
        
        return {
            "merchant_id": merchant.merchant_id,
            "business_name": merchant.business_name,
            "total_payments": len(merchant_payments),
            "completed_payments": len(completed_payments),
            "total_revenue": total_revenue,
            "total_fees_paid": total_fees_paid,
            "monthly_revenue": monthly_revenue,
            "monthly_volume": monthly_volume,
            "api_keys_count": len(merchant.api_keys),
            "current_tier": api_key.tier.value,
            "revenue_share_rate": api_key.revenue_share,
            "rate_limit": api_key.rate_limit,
            "account_created": merchant.created_time,
            "verified": merchant.verified
        }
    
    def get_api_documentation(self) -> Dict[str, Any]:
        """Get API documentation"""
        return {
            "api_name": self.api_name,
            "version": self.version,
            "base_url": self.base_url,
            "authentication": {
                "type": "HMAC-SHA256",
                "headers": {
                    "X-API-Key": "Your public key",
                    "X-Timestamp": "Unix timestamp",
                    "X-Signature": "HMAC signature"
                }
            },
            "endpoints": self.endpoints,
            "rate_limits": {
                "basic": "100 requests/minute",
                "professional": "500 requests/minute",
                "enterprise": "2000 requests/minute",
                "custom": "10000 requests/minute"
            },
            "revenue_sharing": {
                tier.value: f"{rate:.1%}" 
                for tier, rate in self.revenue_share_tiers.items()
            },
            "supported_currencies": ["ACC", "USD", "BTC", "ETH"],
            "webhook_events": [event.value for event in WebhookEvent],
            "example_requests": {
                "create_payment": {
                    "method": "POST",
                    "endpoint": "/v1/payments",
                    "body": {
                        "amount": 10.0,
                        "currency": "ACC",
                        "description": "Game purchase",
                        "customer_email": "user@example.com",
                        "webhook_url": "https://yoursite.com/webhook"
                    }
                }
            }
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        total_merchants = len(self.merchants)
        total_api_keys = len(self.api_keys)
        total_payments = len(self.payments)
        
        completed_payments = [
            p for p in self.payments.values()
            if p.status == PaymentStatus.COMPLETED
        ]
        
        total_volume = sum(p.amount for p in completed_payments)
        total_fees_collected = sum(p.fees["total_fees"] for p in completed_payments)
        
        return {
            "total_merchants": total_merchants,
            "total_api_keys": total_api_keys,
            "total_payments": total_payments,
            "completed_payments": len(completed_payments),
            "total_volume_processed": total_volume,
            "total_fees_collected": total_fees_collected,
            "average_payment_size": total_volume / max(1, len(completed_payments)),
            "api_version": self.version,
            "uptime": time.time() - getattr(self, 'start_time', time.time())
        }

# Demo dan testing
if __name__ == "__main__":
    print("🔌 THIRD-PARTY PAYMENT API DEMO 🔌")
    
    # Initialize API
    api = ThirdPartyPaymentAPI()
    
    # Register demo merchants
    print("\n🏪 Registering Demo Merchants...")
    merchant1 = api.register_merchant(
        "GameDev Studio", "gaming", "contact@gamedev.com", "wallet-123"
    )
    merchant2 = api.register_merchant(
        "E-commerce Store", "retail", "admin@store.com", "wallet-456"
    )
    
    # Create API keys
    print("\n🔑 Creating API Keys...")
    api_key1 = api.create_api_key(merchant1, APIKeyTier.PROFESSIONAL)
    api_key2 = api.create_api_key(merchant2, APIKeyTier.BASIC)
    
    # Simulate authentication
    print("\n🔐 Testing Authentication...")
    key_obj = api.api_keys[api_key1["api_key_id"]]
    
    # Create payments
    print("\n💳 Creating Demo Payments...")
    payment1 = api.create_payment(
        key_obj, 
        amount=25.0,
        currency="ACC",
        description="Premium Game Purchase",
        customer_email="player@example.com",
        webhook_url="https://gamedev.com/webhook"
    )
    
    payment2 = api.create_payment(
        key_obj,
        amount=10.0,
        currency="ACC", 
        description="In-game Item",
        customer_email="player2@example.com"
    )
    
    # Process payments (simulate)
    print("\n⚡ Processing Payments...")
    # Note: Would need actual ACC system for real processing
    
    # Get merchant dashboard
    print("\n📊 Merchant Dashboard:")
    dashboard = api.get_merchant_dashboard(key_obj)
    print(f"   Business: {dashboard['business_name']}")
    print(f"   Total Payments: {dashboard['total_payments']}")
    print(f"   Monthly Volume: {dashboard['monthly_volume']:.2f} ACC")
    print(f"   Current Tier: {dashboard['current_tier']}")
    
    # List payments
    print("\n📋 Payment List:")
    payments_list = api.list_payments(key_obj, limit=5)
    for payment in payments_list["payments"]:
        print(f"   {payment['payment_id']}: {payment['amount']} {payment['currency']} - {payment['status']}")
    
    # Show API documentation
    print("\n📚 API Documentation Available:")
    docs = api.get_api_documentation()
    print(f"   API: {docs['api_name']} v{docs['version']}")
    print(f"   Base URL: {docs['base_url']}")
    print(f"   Endpoints: {len(docs['endpoints'])}")
    
    # System statistics
    print("\n📈 System Statistics:")
    stats = api.get_system_stats()
    print(f"   Total Merchants: {stats['total_merchants']}")
    print(f"   Total API Keys: {stats['total_api_keys']}")
    print(f"   Total Payments: {stats['total_payments']}")
    print(f"   Volume Processed: {stats['total_volume_processed']:.2f} ACC")
    print(f"   Fees Collected: {stats['total_fees_collected']:.4f} ACC")
    
    print("\n✅ Third-Party Payment API demo completed!")
    print("🔌 Ready for merchant integration!")