"""
JesterNet License Guardian - The Sovereign Validator
==================================================

The Guardian of tiered reality. This module validates license tiers and 
controls access to our most powerful CLI weapons.

"We give them the map to the treasure hoard, but we sell them the keys to the chests."
"""
import os
import sys
import click
from typing import Optional, Dict, Any
import hashlib
import time
from pathlib import Path

# License Tier Definitions
TIERS = {
    'freemium': 0,
    'professional': 1, 
    'ultimate': 2
}

# CLI Tool Tier Requirements
CLI_REQUIREMENTS = {
    # FREEMIUM (Free) - Basic functionality
    'harvest.py': 'freemium',
    'test_installation.py': 'freemium',
    
    # PROFESSIONAL ($49/month) - Creative tools
    'prophet.py': 'professional',
    'style-openai': 'professional', 
    'style-vertex': 'professional',
    'image_router.py': 'professional',
    
    # ULTIMATE ($149/month) - Enterprise batch processing
    'imagen_batch_cli.py': 'ultimate',
    'vertex_batch_ultra.py': 'ultimate',
    'batch_vertex_processor.py': 'ultimate', 
    'test_gpt5_batch.py': 'ultimate',
    'test_xai_deepseek.py': 'ultimate',
    'summon.py': 'ultimate'
}

# Upgrade messaging by tier
UPGRADE_MESSAGES = {
    'professional': """
🔒 This feature requires the PROFESSIONAL tier ($49/month)

✨ PROFESSIONAL unlocks:
   • Creative image generation with prophet.py
   • OpenAI & Vertex AI style wrappers
   • Smart image routing
   • Template-based generation
   • Basic batch processing

🚀 Upgrade now: https://quantumencoding.io/pricing
   Use code ARCHITECT for 30% off first month
""",
    'ultimate': """  
🔒 This feature requires the ULTIMATE tier ($149/month)

🏆 ULTIMATE unlocks the full arsenal:
   • High-volume batch processing
   • Ultra-quality Imagen generation
   • Multi-provider testing suite
   • Advanced orchestration with summon.py
   • Full HarvesterSDK enterprise features
   • Priority support & custom templates

⚡ Upgrade now: https://quantumencoding.io/pricing
   Use code ARCHITECT for 30% off first month
"""
}

def get_license_key() -> Optional[str]:
    """
    Retrieve license key from environment or config
    
    Order of precedence:
    1. HARVESTER_LICENSE_KEY environment variable
    2. ~/.harvester/license.key file
    3. ./harvester_license.key file
    """
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
    """
    Parse license key and extract tier information
    
    Expected format: HSK-{TIER}-{HASH}
    Examples:
    - HSK-FREE-abc123 (freemium)
    - HSK-PRO-xyz789 (professional)  
    - HSK-PRE-ultimate-def456 (ultimate)
    """
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
    elif tier_part == 'pre' and len(parts) >= 4 and parts[2].lower() == 'ultimate':
        tier = 'ultimate'
    else:
        tier = 'freemium'
    
    # For now, accept any properly formatted key as valid
    # In production, this would validate against a service
    valid = True
    
    return {
        'tier': tier,
        'valid': valid,
        'key': key,
        'parsed_at': int(time.time())
    }

def get_user_tier() -> str:
    """Get the current user's license tier"""
    key = get_license_key()
    if not key:
        return 'freemium'
    
    license_info = parse_license_key(key)
    return license_info['tier']

def check_license_tier(required_tier: str, script_name: Optional[str] = None) -> bool:
    """
    Check if user has required license tier
    
    Args:
        required_tier: Minimum tier required ('freemium', 'professional', 'ultimate')
        script_name: Name of the script requesting access (for better messaging)
        
    Returns:
        True if access granted, exits program if denied
    """
    user_tier = get_user_tier()
    required_level = TIERS.get(required_tier, 999)
    user_level = TIERS.get(user_tier, 0)
    
    if user_level >= required_level:
        return True
    
    # Access denied - show seductive upgrade message
    click.echo(f"🚫 Access Denied")
    if script_name:
        click.echo(f"   {script_name} requires {required_tier.upper()} tier")
    
    upgrade_msg = UPGRADE_MESSAGES.get(required_tier, UPGRADE_MESSAGES['professional'])
    click.echo(upgrade_msg)
    
    sys.exit(1)

def check_cli_access(script_path: str) -> bool:
    """
    Check access for a CLI script based on its filename
    
    Args:
        script_path: Path to the script being executed
        
    Returns:
        True if access granted, exits if denied
    """
    script_name = Path(script_path).name
    required_tier = CLI_REQUIREMENTS.get(script_name, 'freemium')
    
    return check_license_tier(required_tier, script_name)

def display_license_status():
    """Display current license status"""
    key = get_license_key()
    
    if not key:
        click.echo("📋 License Status: FREEMIUM (No license key found)")
        click.echo("   Set HARVESTER_LICENSE_KEY environment variable")
        click.echo("   Or save key to ~/.harvester/license.key")
        return
    
    license_info = parse_license_key(key)
    tier = license_info['tier']
    
    if license_info['valid']:
        tier_emoji = {'freemium': '🆓', 'professional': '🥈', 'ultimate': '🥇'}
        click.echo(f"📋 License Status: {tier_emoji.get(tier, '❓')} {tier.upper()}")
        click.echo(f"   Key: {key[:15]}...")
    else:
        click.echo("📋 License Status: ❌ INVALID KEY")
        click.echo(f"   Key: {key[:15]}...")
        click.echo("   Contact support for assistance")

# Convenience function for CLI scripts
def require_tier(tier: str):
    """Decorator-style function for requiring a specific tier"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            check_license_tier(tier)
            return func(*args, **kwargs)
        return wrapper
    return decorator

if __name__ == "__main__":
    # Test the license system
    display_license_status()
    click.echo("\n🔧 Testing tier checks:")
    for tier in ['freemium', 'professional', 'ultimate']:
        user_tier = get_user_tier()
        user_level = TIERS.get(user_tier, 0)
        required_level = TIERS.get(tier, 999)
        
        if user_level >= required_level:
            click.echo(f"   ✅ {tier}: GRANTED")
        else:
            click.echo(f"   🔒 {tier}: LOCKED")