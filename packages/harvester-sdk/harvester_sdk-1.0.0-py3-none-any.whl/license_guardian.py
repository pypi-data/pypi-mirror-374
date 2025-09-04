"""
JesterNet License Guardian - Standalone Validator
================================================

Standalone licensing module that doesn't depend on the full SDK.
The Sentinel at the gates of our sovereign arsenal.
"""
import os
import sys
import click
from typing import Optional, Dict, Any
from pathlib import Path

# License Tier Definitions (Aligned with Cloud Deployment)
TIERS = {
    'freemium': 0,      # $0/mo - 5 concurrent workers, single provider
    'professional': 1,   # $99/mo - 20 workers, all providers
    'premium': 2,        # $500/mo - 100 workers, batch processing
    'enterprise': 3      # Custom - Unlimited power
}

# CLI Tool Tier Requirements (Aligned with Deployed Pricing)
CLI_REQUIREMENTS = {
    # FREEMIUM ($0/mo) - Taste of parallel power
    'batch_code.py': 'freemium',              # Code transformation engine (was harvest.py)
    'test_installation.py': 'freemium',        # Installation validator
    'test_gpt5_batch.py': 'freemium',         # GPT-5 batch tester
    'test_xai_deepseek.py': 'freemium',       # XAI/DeepSeek tester
    'test_models.py': 'freemium',             # Model validation tool
    
    # PROFESSIONAL ($99/mo) - All AI providers, advanced features
    'image_cli.py': 'professional',           # Image generation CLI (was prophet.py)
    'style_openai_cli.py': 'professional',    # OpenAI style wrapper
    'style_vertex_cli.py': 'professional',    # Vertex style wrapper
    'router_image.py': 'professional',        # Smart image routing (was image_router.py)
    
    # PREMIUM ($500/mo) - CSV batch processing, industrial scale
    'batch_image.py': 'premium',              # Batch image generation (was imagen_batch_cli.py)
    'batch_vertex.py': 'premium',             # Ultra batch processing (was vertex_batch_ultra.py)
    'batch_vertex_processor.py': 'premium',   # Advanced batch processor
    
    # ENTERPRISE (Custom) - The entire sovereign engine
    'ai_assistant.py': 'enterprise'           # Universal AI orchestrator (was summon.py)
}

# Upgrade messaging by tier (Aligned with Live Pricing)
UPGRADE_MESSAGES = {
    'professional': """
🔒 This feature requires the PROFESSIONAL tier ($99/month)

✨ PROFESSIONAL unlocks:
   • 20 concurrent workers (vs 5)
   • All AI providers access
   • Advanced creative tools (prophet.py, style wrappers)
   • Smart image routing
   • Priority support

🚀 Upgrade now: https://quantumencoding.io/pricing
   For the serious craftsman.
""",
    'premium': """  
🔒 This feature requires the PREMIUM tier ($500/month)

🏭 PREMIUM - Command the factory:
   • 100 concurrent workers
   • CSV batch processing arsenal
   • Industrial scale image generation
   • Codebase refactoring tools
   • Enterprise-grade performance

⚡ Upgrade now: https://quantumencoding.io/pricing
   Industrial scale power.
""",
    'enterprise': """
🔒 This feature requires the ENTERPRISE tier (Custom pricing)

👑 ENTERPRISE - The entire sovereign engine:
   • Unlimited concurrent power
   • Custom integrations
   • Dedicated support team
   • White-label options
   • Full sovereign control

🌟 Contact sales: https://quantumencoding.io/enterprise
   Unlimited power awaits.
"""
}

def get_license_key() -> Optional[str]:
    """Get license key from environment or config files"""
    # Check environment first
    key = os.environ.get('HARVESTER_LICENSE_KEY')
    if key:
        return key.strip()
    
    # Check user config directory
    config_path = Path.home() / '.harvester' / 'license.key'
    if config_path.exists():
        try:
            return config_path.read_text().strip()
        except Exception:
            pass
    
    # Check current directory
    local_path = Path('./harvester_license.key')
    if local_path.exists():
        try:
            return local_path.read_text().strip()
        except Exception:
            pass
    
    return None

def parse_license_key(key: str) -> Dict[str, Any]:
    """Parse license key and extract tier information"""
    if not key or not key.startswith('HSK-'):
        return {'tier': 'freemium', 'valid': False}
    
    parts = key.split('-')
    if len(parts) < 3:
        return {'tier': 'freemium', 'valid': False}
    
    # Extract tier
    tier_part = parts[1].lower()
    if tier_part == 'free':
        tier = 'freemium'
    elif tier_part == 'pro':
        tier = 'professional'
    elif tier_part == 'prem' or tier_part == 'premium':
        tier = 'premium'
    elif tier_part == 'ent' or tier_part == 'enterprise':
        tier = 'enterprise'
    else:
        tier = 'freemium'
    
    # For now, accept any properly formatted key as valid
    # In production, this would validate against a service
    valid = True
    
    return {'tier': tier, 'valid': valid, 'key': key}

def get_user_tier() -> str:
    """Get the current user's license tier"""
    # Check for direct tier override first (for testing)
    tier_override = os.environ.get('HARVESTER_LICENSE_TIER')
    if tier_override and tier_override.lower() in TIERS:
        return tier_override.lower()
    
    key = get_license_key()
    if not key:
        return 'freemium'
    
    license_info = parse_license_key(key)
    return license_info['tier']

def check_license_tier(required_tier: str, script_name: Optional[str] = None) -> bool:
    """Check if user has required license tier"""
    user_tier = get_user_tier()
    required_level = TIERS.get(required_tier, 999)
    user_level = TIERS.get(user_tier, 0)
    
    if user_level >= required_level:
        return True
    
    # Access denied - show seductive upgrade message
    if script_name:
        print(f"🚫 Access Denied: {script_name} requires {required_tier.upper()} tier")
    else:
        print(f"🚫 Access Denied: {required_tier.upper()} tier required")
    
    upgrade_msg = UPGRADE_MESSAGES.get(required_tier, UPGRADE_MESSAGES['professional'])
    print(upgrade_msg)
    
    sys.exit(1)

def get_allowed_providers(tier: str = None) -> list:
    """Get list of allowed providers for the given tier"""
    if tier is None:
        tier = get_user_tier()
    
    tier_level = TIERS.get(tier, 0)
    
    if tier_level == 0:  # Freemium - Google only
        return ['google', 'gemini_exp']  # Gemini models only
    elif tier_level >= 1:  # Professional and above - all providers
        return ['google', 'gemini_exp', 'openai', 'vertex', 'deepseek', 'xai', 'anthropic', 
                'dalle3', 'gpt_image', 'vertex_image', 'vertex_video']
    
    return []

def get_allowed_models(tier: str = None) -> list:
    """Get list of allowed model aliases for the given tier"""
    if tier is None:
        tier = get_user_tier()
    
    tier_level = TIERS.get(tier, 0)
    
    if tier_level == 0:  # Freemium - Gemini models only (2 models)
        return ['gemini-2.5-pro', 'gemini-2.5-flash']
    elif tier_level >= 1:  # Professional and above - all models
        return []  # Empty list means all models allowed
    
    return ['gemini-2.5-flash']  # Default to Gemini Flash if unknown

def check_cli_access(script_path: str) -> bool:
    """Check access for a CLI script based on its filename"""
    script_name = Path(script_path).name
    required_tier = CLI_REQUIREMENTS.get(script_name, 'freemium')
    
    return check_license_tier(required_tier, script_name)

if __name__ == "__main__":
    # Test the license system
    key = get_license_key()
    tier = get_user_tier()
    
    if key:
        print(f"📋 License: {tier.upper()} (Key: {key[:15]}...)")
    else:
        print("📋 License: FREEMIUM (No key found)")
    
    print("\n🔧 Testing tier checks:")
    for test_tier in ['freemium', 'professional', 'premium', 'enterprise']:
        user_level = TIERS.get(tier, 0)
        required_level = TIERS.get(test_tier, 999)
        
        if user_level >= required_level:
            print(f"   ✅ {test_tier}: GRANTED")
        else:
            print(f"   🔒 {test_tier}: LOCKED")