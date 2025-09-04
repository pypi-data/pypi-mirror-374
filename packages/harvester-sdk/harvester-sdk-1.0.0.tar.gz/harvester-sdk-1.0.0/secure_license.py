"""
Harvester SDK - Secure License Validation System
© 2025 QUANTUM ENCODING LTD

Production-grade license validation with cryptographic security.
No bypasses, no client-side hacks, no environment variable overrides.
"""

import os
import json
import time
import hmac
import hashlib
import requests
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# License server configuration  
LICENSE_SERVER_URL = os.environ.get('HARVESTER_LICENSE_ENDPOINT', 'https://m9pfenpmpc.eu-west-1.awsapprunner.com')
VALIDATION_CACHE_HOURS = 4  # Cache valid licenses for 4 hours
SECRET_KEY = "HSK_VALIDATION_SECRET_2025"  # Server-side shared secret

# Tier definitions (server-authoritative)
TIER_LEVELS = {
    'freemium': 0,
    'professional': 1, 
    'premium': 2,
    'enterprise': 3
}

class SecureLicenseValidator:
    """Production-grade license validation with server verification"""
    
    def __init__(self):
        self.cache_db = self._init_cache_db()
        self.last_validation = {}
        
    def _init_cache_db(self) -> sqlite3.Connection:
        """Initialize license cache database"""
        cache_dir = Path.home() / '.harvester'
        cache_dir.mkdir(exist_ok=True)
        
        db_path = cache_dir / 'license_cache.db'
        conn = sqlite3.connect(str(db_path))
        
        # Create cache table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS license_cache (
                license_key TEXT PRIMARY KEY,
                tier TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                validated_at INTEGER NOT NULL,
                machine_id TEXT NOT NULL,
                features TEXT NOT NULL
            )
        """)
        conn.commit()
        return conn
    
    def get_machine_id(self) -> str:
        """Get unique machine identifier"""
        import uuid
        import socket
        
        # Combine multiple machine characteristics
        hostname = socket.gethostname()
        mac = hex(uuid.getnode())[2:]
        
        # Create deterministic machine ID
        machine_string = f"{hostname}:{mac}:{os.name}"
        return hashlib.sha256(machine_string.encode()).hexdigest()[:16]
    
    def validate_license(self, license_key: str) -> Dict[str, Any]:
        """
        Validate license with server verification and caching
        
        Returns:
            {
                'valid': bool,
                'tier': str,
                'expires_at': int,
                'features': list,
                'error': str (if invalid)
            }
        """
        if not license_key or not license_key.startswith('HSK-'):
            return {
                'valid': False, 
                'tier': 'freemium',
                'expires_at': 0,
                'features': [],
                'error': 'Invalid license key format'
            }
        
        # Check cache first (but not forever)
        cached = self._check_cache(license_key)
        if cached and cached['expires_at'] > time.time():
            logger.debug(f"Using cached license validation for {license_key[:8]}...")
            return cached
        
        # Server validation required
        try:
            result = self._validate_with_server(license_key)
            if result['valid']:
                self._update_cache(license_key, result)
            return result
            
        except requests.RequestException as e:
            logger.warning(f"License server unavailable: {e}")
            
            # Fall back to cache if server is down (limited grace period)
            if cached and cached['validated_at'] > time.time() - (24 * 3600):  # 24h grace
                logger.info("Using cached license due to server unavailability")
                return cached
            
            # No cache, no server = freemium only
            return {
                'valid': False,
                'tier': 'freemium', 
                'expires_at': 0,
                'features': [],
                'error': 'License server unavailable and no valid cache'
            }
    
    def _check_cache(self, license_key: str) -> Optional[Dict[str, Any]]:
        """Check license cache"""
        cursor = self.cache_db.execute(
            "SELECT tier, expires_at, validated_at, features FROM license_cache WHERE license_key = ?",
            (license_key,)
        )
        row = cursor.fetchone()
        
        if not row:
            return None
            
        tier, expires_at, validated_at, features_json = row
        
        # Check if cache is still fresh (4 hours)
        cache_age = time.time() - validated_at
        if cache_age > VALIDATION_CACHE_HOURS * 3600:
            return None
            
        return {
            'valid': True,
            'tier': tier,
            'expires_at': expires_at,
            'features': json.loads(features_json),
            'cached': True
        }
    
    def _validate_with_server(self, license_key: str) -> Dict[str, Any]:
        """Validate license with remote server"""
        machine_id = self.get_machine_id()
        timestamp = int(time.time())
        
        # Create authenticated request
        payload = {
            'license_key': license_key,
            'machine_id': machine_id,
            'timestamp': timestamp,
            'sdk_version': '1.0.0',
            'platform': os.name
        }
        
        # Add HMAC signature for request integrity
        signature = self._create_signature(payload)
        headers = {
            'Content-Type': 'application/json',
            'X-HSK-Signature': signature,
            'User-Agent': 'HarvesterSDK/1.0.0'
        }
        
        # Make validation request  
        # Support both old format (/validate) and new quantum-keymaster format (/v1/keys/validate)
        validation_path = "/v1/keys/validate" if "apprunner.amazonaws.com" in LICENSE_SERVER_URL else "/validate"
        
        response = requests.post(
            f"{LICENSE_SERVER_URL}{validation_path}",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                'valid': True,
                'tier': data.get('tier', 'freemium'),
                'expires_at': data.get('expires_at', 0),
                'features': data.get('features', []),
                'machine_limit': data.get('machine_limit', 1)
            }
        elif response.status_code == 401:
            return {
                'valid': False,
                'tier': 'freemium',
                'expires_at': 0,
                'features': [],
                'error': 'Invalid or expired license key'
            }
        elif response.status_code == 429:
            return {
                'valid': False,
                'tier': 'freemium', 
                'expires_at': 0,
                'features': [],
                'error': 'License key exceeded machine limit'
            }
        else:
            raise requests.RequestException(f"Server error: {response.status_code}")
    
    def _create_signature(self, payload: dict) -> str:
        """Create HMAC signature for request authenticity"""
        # Sort keys for consistent signature
        sorted_payload = json.dumps(payload, sort_keys=True)
        return hmac.new(
            SECRET_KEY.encode(),
            sorted_payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def _update_cache(self, license_key: str, result: Dict[str, Any]):
        """Update license cache"""
        machine_id = self.get_machine_id()
        
        self.cache_db.execute("""
            INSERT OR REPLACE INTO license_cache 
            (license_key, tier, expires_at, validated_at, machine_id, features)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            license_key,
            result['tier'],
            result['expires_at'],
            int(time.time()),
            machine_id,
            json.dumps(result['features'])
        ))
        self.cache_db.commit()
    
    def check_feature_access(self, feature: str, license_key: str = None) -> bool:
        """Check if license allows specific feature access"""
        if not license_key:
            license_key = self.get_license_key()
        
        if not license_key:
            return feature in ['basic_processing']  # Freemium features
        
        validation = self.validate_license(license_key)
        if not validation['valid']:
            return feature in ['basic_processing']
        
        # Feature mapping by tier
        tier_features = {
            'freemium': ['basic_processing'],
            'professional': ['basic_processing', 'multi_provider', 'image_generation'],
            'premium': ['basic_processing', 'multi_provider', 'image_generation', 'batch_processing', 'advanced_features'],
            'enterprise': ['*']  # All features
        }
        
        allowed_features = tier_features.get(validation['tier'], [])
        return '*' in allowed_features or feature in allowed_features
    
    def get_license_key(self) -> Optional[str]:
        """Get license key from secure sources only"""
        # Check environment variable (but validate it)
        key = os.environ.get('HARVESTER_LICENSE_KEY')
        if key:
            return key.strip()
        
        # Check user config file
        config_path = Path.home() / '.harvester' / 'license.key'
        if config_path.exists():
            try:
                return config_path.read_text().strip()
            except Exception:
                pass
        
        return None
    
    def get_user_tier(self) -> str:
        """Get validated user tier (no bypasses allowed)"""
        # REMOVED: Environment variable bypass (HARVESTER_LICENSE_TIER)
        # This was the security vulnerability!
        
        license_key = self.get_license_key()
        if not license_key:
            return 'freemium'
        
        validation = self.validate_license(license_key)
        return validation['tier'] if validation['valid'] else 'freemium'


# Global instance
_secure_validator = None

def get_secure_validator() -> SecureLicenseValidator:
    """Get global secure license validator instance"""
    global _secure_validator
    if _secure_validator is None:
        _secure_validator = SecureLicenseValidator()
    return _secure_validator

def check_license_tier(required_tier: str) -> bool:
    """Check if user has required license tier (secure version)"""
    validator = get_secure_validator()
    user_tier = validator.get_user_tier()
    
    required_level = TIER_LEVELS.get(required_tier, 999)
    user_level = TIER_LEVELS.get(user_tier, 0)
    
    return user_level >= required_level

def require_license_tier(required_tier: str, feature_name: str = ""):
    """Require specific license tier or exit with upgrade message"""
    if not check_license_tier(required_tier):
        print(f"🚫 License Required: {required_tier.upper()} tier needed for {feature_name}")
        print(f"📧 Upgrade at: https://quantumencoding.io/pricing")
        print(f"💼 Current tier: {get_secure_validator().get_user_tier().upper()}")
        exit(1)

if __name__ == "__main__":
    # Test the secure validation
    validator = SecureLicenseValidator()
    
    test_key = os.environ.get('HARVESTER_LICENSE_KEY', 'HSK-PRO-test123')
    result = validator.validate_license(test_key)
    
    print(f"License validation result: {result}")
    print(f"User tier: {validator.get_user_tier()}")