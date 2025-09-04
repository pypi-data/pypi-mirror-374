"""
The Divine Arbiter - Sovereign Processor Selection Based on License Tier

This module implements the Stratification of Power, determining which
level of parallel processing sovereignty a user may wield based on
their ascension through the pricing tiers.

"To command the Federation, you must first be crowned an Emperor."

Copyright (c) 2025 Quantum Encoding Ltd.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import the Monarchy processor
from processors.parallel import ParallelProcessor  # The Monarchy
# Federation will be imported dynamically when needed

logger = logging.getLogger(__name__)


class DivineArbiter:
    """
    The Divine Arbiter - Guardian of Sovereignty
    
    This arbiter determines which level of parallel processing power
    a user may access based on their license tier. It is the gateway
    between the Monarchy and the Federation.
    
    Tiers and Their Sovereignty:
    - FREEMIUM/PROFESSIONAL: The Monarchy (single-provider parallelism)
    - PREMIUM/ENTERPRISE: The Federation (multi-provider parallelism)
    """
    
    # The Ladder of Sovereignty
    TIER_SOVEREIGNTY = {
        'freemium': 'monarchy',
        'professional': 'monarchy',
        'premium': 'federation',
        'enterprise': 'federation'
    }
    
    # The Divine Messages
    ASCENSION_MESSAGES = {
        'monarchy_limit': """
╔══════════════════════════════════════════════════════════════╗
║                    👑 MONARCHY LIMITATION 👑                 ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  You are wielding the power of the Monarchy - you can       ║
║  command parallel operations against a single provider.     ║
║                                                              ║
║  To unleash the GALACTIC FEDERATION and command multiple    ║
║  providers simultaneously (--model all), you must ascend    ║
║  to the PREMIUM tier.                                       ║
║                                                              ║
║  🌟 PREMIUM TIER UNLOCKS:                                   ║
║  • Multi-provider parallel execution (75+ workers)          ║
║  • True parallel warfare across all AI nations              ║
║  • Provider isolation (no bottlenecks)                      ║
║  • 10x throughput for multi-model operations                ║
║                                                              ║
║  Upgrade at: https://quantumencoding.io/premium             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""",
        'federation_granted': """
🌟 GALACTIC FEDERATION ACCESS GRANTED 🌟
You now command the sovereign armies of all provider nations!
Mobilizing {nations} nations with {workers} total workers...
""",
        'structured_output_limit': """
╔══════════════════════════════════════════════════════════════╗
║                  🎯 STRUCTURED OUTPUT PREMIUM 🎯             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Structured Outputs with guaranteed JSON schema compliance  ║
║  is a PREMIUM tier feature.                                 ║
║                                                              ║
║  🎯 PREMIUM STRUCTURED OUTPUTS INCLUDE:                     ║
║  • Pydantic schema validation                                ║
║  • Automatic retry on invalid responses                     ║
║  • Multi-provider structured output support                 ║
║  • Type-safe response guarantees                            ║
║  • Custom schema compilation                                 ║
║                                                              ║
║  Currently available: Basic text responses only             ║
║                                                              ║
║  🌟 Upgrade to Premium: https://quantumencoding.io/premium  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""",
        'function_calling_limit': """
╔══════════════════════════════════════════════════════════════╗
║                    🔧 FUNCTION CALLING ELITE 🔧              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Function Calling & Tool Use enables agentic AI that can    ║
║  interact with external systems and execute tasks.          ║
║                                                              ║
║  🔧 FUNCTION CALLING TIERS:                                 ║
║  • PROFESSIONAL: Basic file operations                      ║
║  • PREMIUM: Full tool library (web, code, data)             ║
║  • ENTERPRISE: Custom tools + workflow orchestration       ║
║                                                              ║
║  Your tier: {tier}                                          ║
║  Available tools: {available_tools}                         ║
║                                                              ║
║  🌟 Upgrade to Premium: https://quantumencoding.io/premium  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""",
        'ascension_complete': """
✨ ASCENSION COMPLETE ✨
Your license has been upgraded. The Federation awaits your command.
"""
    }
    
    def __init__(self):
        """Initialize the Divine Arbiter"""
        self.current_tier = self._detect_license_tier()
        self.processor = None
        self.federation_attempted = False
        
        logger.info(f"🏛️ Divine Arbiter initialized")
        logger.info(f"👤 Current tier: {self.current_tier.upper()}")
        logger.info(f"⚔️ Sovereignty level: {self.TIER_SOVEREIGNTY[self.current_tier].upper()}")
    
    def _detect_license_tier(self) -> str:
        """Detect the current license tier using secure validation"""
        # SECURITY FIX: Remove environment variable bypass
        # This was the vulnerability! Users could set HARVESTER_LICENSE_TIER=premium
        
        try:
            # Use secure license validation
            from secure_license import get_secure_validator
            validator = get_secure_validator()
            tier = validator.get_user_tier()
            
            logger.info(f"Secure license tier detected: {tier.upper()}")
            return tier
            
        except ImportError:
            # Fallback if secure license not available (development only)
            logger.warning("Secure license validation not available, using freemium")
            return 'freemium'
        except Exception as e:
            logger.error(f"License validation error: {e}")
            return 'freemium'
    
    def summon_processor(self, 
                        operation_mode: str = 'single',
                        models: Optional[List[str]] = None) -> Any:
        """
        Summon the appropriate processor based on license tier and operation mode
        
        Args:
            operation_mode: 'single' for single provider, 'multi' for multi-provider
            models: List of models requested
            
        Returns:
            Either ParallelProcessor (Monarchy) or GalacticFederation based on tier
        """
        sovereignty = self.TIER_SOVEREIGNTY[self.current_tier]
        
        # Determine if Federation is needed
        needs_federation = (
            operation_mode == 'multi' or 
            (models and len(models) > 3) or
            (models and self._spans_multiple_providers(models))
        )
        
        if needs_federation and sovereignty == 'monarchy':
            # User wants Federation but only has Monarchy access
            self._display_monarchy_limitation()
            # Still return Monarchy processor but with warning
            return self._summon_monarchy()
        
        elif needs_federation and sovereignty == 'federation':
            # User has earned Federation access
            return self._summon_federation()
        
        else:
            # Single provider operation - use Monarchy
            return self._summon_monarchy()
    
    def _summon_monarchy(self) -> ParallelProcessor:
        """Summon the Monarchy processor for single-provider operations"""
        if not self.processor or not isinstance(self.processor, ParallelProcessor):
            logger.info("👑 Summoning the Monarchy Processor...")
            self.processor = ParallelProcessor(
                max_workers=20,
                rate_limit_per_minute=60,
                retry_attempts=3,
                backoff_multiplier=2.0
            )
        return self.processor
    
    def _summon_federation(self):
        """Summon the Federation processor for multi-provider operations"""
        if not self.processor or not isinstance(self.processor, GalacticFederation):
            logger.info("🌌 Summoning the Galactic Federation...")
            
            # Import and create the Federation
            from processors.galactic_federation import GalacticFederation
            self.processor = GalacticFederation()
            
            # Display granted message
            status = self.processor.get_federal_status()
            nations = len(status['nations'])
            workers = sum(n['max_workers'] for n in status['nations'].values())
            
            print(self.ASCENSION_MESSAGES['federation_granted'].format(
                nations=nations,
                workers=workers
            ))
        
        return self.processor
    
    def _spans_multiple_providers(self, models: List[str]) -> bool:
        """Check if model list spans multiple providers"""
        providers = set()
        
        # Model to provider mapping
        provider_map = {
            'gpt': 'openai',
            'claude': 'anthropic',
            'gemini': 'google',
            'deepseek': 'deepseek',
            'grok': 'xai'
        }
        
        for model in models:
            for prefix, provider in provider_map.items():
                if model.lower().startswith(prefix):
                    providers.add(provider)
                    break
        
        return len(providers) > 1
    
    def _display_monarchy_limitation(self):
        """Display the monarchy limitation message"""
        if not self.federation_attempted:
            print(self.ASCENSION_MESSAGES['monarchy_limit'])
            self.federation_attempted = True
            logger.info("🚫 Federation access attempted with Monarchy tier")
    
    def check_model_all_permission(self) -> bool:
        """Check if user has permission for --model all"""
        sovereignty = self.TIER_SOVEREIGNTY[self.current_tier]
        
        if sovereignty == 'monarchy':
            self._display_monarchy_limitation()
            return False
        
        return True
    
    def check_structured_output_permission(self) -> bool:
        """Check if user has permission for structured outputs"""
        # Structured outputs are Premium+ feature
        if self.current_tier in ['freemium', 'professional']:
            self._display_structured_output_limitation()
            return False
        
        return True
    
    def _display_structured_output_limitation(self):
        """Display the structured output limitation message"""
        if not hasattr(self, 'structured_output_attempted'):
            print(self.ASCENSION_MESSAGES['structured_output_limit'])
            self.structured_output_attempted = True
            logger.info("🚫 Structured output access attempted with lower tier")
    
    def check_function_calling_permission(self) -> bool:
        """Check if user has permission for function calling"""
        # Function calling starts at Professional tier
        if self.current_tier in ['freemium']:
            self._display_function_calling_limitation()
            return False
        
        return True
    
    def get_function_calling_tier(self) -> str:
        """Get the function calling access level for current tier"""
        if self.current_tier in ['freemium']:
            return 'none'
        elif self.current_tier in ['professional']:
            return 'basic'  # File operations only
        elif self.current_tier in ['premium']:
            return 'full'   # All built-in tools
        elif self.current_tier in ['enterprise']:
            return 'unlimited'  # Custom tools + workflows
        else:
            return 'none'
    
    def _display_function_calling_limitation(self):
        """Display the function calling limitation message"""
        if not hasattr(self, 'function_calling_attempted'):
            # Get available tools for current tier
            from core.function_calling import get_function_registry
            registry = get_function_registry()
            available_tools = registry.get_tools_for_tier(self.current_tier)
            tool_count = len(available_tools)
            
            message = self.ASCENSION_MESSAGES['function_calling_limit'].format(
                tier=self.current_tier.upper(),
                available_tools=f"{tool_count} tools" if tool_count > 0 else "None"
            )
            print(message)
            self.function_calling_attempted = True
            logger.info("🚫 Function calling access attempted")
    
    def get_tier_capabilities(self) -> Dict[str, Any]:
        """Get current tier capabilities"""
        sovereignty = self.TIER_SOVEREIGNTY[self.current_tier]
        
        if sovereignty == 'monarchy':
            return {
                'tier': self.current_tier,
                'sovereignty': 'monarchy',
                'max_workers': 20,
                'max_providers': 1,
                'parallel_providers': False,
                'model_all': False,
                'structured_output': False,
                'function_calling': self.get_function_calling_tier(),
                'description': 'Single-provider parallel processing'
            }
        else:
            return {
                'tier': self.current_tier,
                'sovereignty': 'federation',
                'max_workers': 75,
                'max_providers': 6,
                'parallel_providers': True,
                'model_all': True,
                'structured_output': True,
                'function_calling': self.get_function_calling_tier(),
                'description': 'Multi-provider parallel warfare + structured outputs + function calling'
            }
    
    def upgrade_tier(self, new_tier: str) -> bool:
        """
        Upgrade to a new tier (for testing or after payment)
        
        Args:
            new_tier: The new tier to upgrade to
            
        Returns:
            True if upgrade successful
        """
        if new_tier not in self.TIER_SOVEREIGNTY:
            logger.error(f"Invalid tier: {new_tier}")
            return False
        
        old_sovereignty = self.TIER_SOVEREIGNTY[self.current_tier]
        new_sovereignty = self.TIER_SOVEREIGNTY[new_tier]
        
        self.current_tier = new_tier
        
        # Clear processor cache to force re-summoning
        self.processor = None
        
        if old_sovereignty == 'monarchy' and new_sovereignty == 'federation':
            print(self.ASCENSION_MESSAGES['ascension_complete'])
            logger.info(f"🌟 ASCENSION: {old_sovereignty} → {new_sovereignty}")
        
        return True


# Global Divine Arbiter instance
_divine_arbiter = None

def get_divine_arbiter() -> DivineArbiter:
    """Get or create the global Divine Arbiter instance"""
    global _divine_arbiter
    if _divine_arbiter is None:
        _divine_arbiter = DivineArbiter()
    return _divine_arbiter