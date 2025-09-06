"""
DeepSeek provider implementation
"""
import aiohttp
import json
from typing import Dict, Any
import logging

from .base_provider import BaseProvider

logger = logging.getLogger(__name__)

class DeepseekProvider(BaseProvider):
    """Provider for DeepSeek models with updated configuration"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get('api_key')
        self.base_url = config.get('endpoint', 'https://api.deepseek.com/v1/chat/completions')
        
        # Updated model settings per API documentation
        self.model_settings = {
            'deepseek-chat': {  # Points to DeepSeek-V3-0328
                'max_tokens': 8000,     # Matches MAX OUTPUT: 8K
                'temperature': 0.7,
                'cost_per_million_input_cache_hit': 0.07,
                'cost_per_million_input_cache_miss': 0.27,
                'cost_per_million_output': 1.10
            },
            'deepseek-reasoner': {  # Points to DeepSeek-R1-0528
                'max_tokens': 64000,    # Matches MAX OUTPUT: 64K
                'temperature': 0.7,
                'cost_per_million_input_cache_hit': 0.14,
                'cost_per_million_input_cache_miss': 0.55,
                'cost_per_million_output': 2.19
            }
        }
    
    async def complete(self, prompt: str, model: str) -> str:
        """Send completion request to DeepSeek"""
        # Resolve model alias
        actual_model = self.resolve_model_alias(model)
        
        # Verify model is supported
        if actual_model not in self.model_settings:
            raise ValueError(f"Unsupported model: {actual_model}. Valid models: {list(self.model_settings.keys())}")
        
        # Apply rate limiting
        estimated_tokens = self.estimate_tokens(prompt, "")
        await self._apply_rate_limit(estimated_tokens)
        
        # Prepare request
        settings = self.model_settings[actual_model]
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': actual_model,
            'messages': [{
                'role': 'user',
                'content': prompt
            }],
            'max_tokens': settings['max_tokens'],
            'temperature': settings['temperature'],
            'stream': False
        }
        
        # Make request
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        try:
            async with self.session.post(
                self.base_url,
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"DeepSeek API error: {response.status} - {error_text}")
                
                data = await response.json()
                
                # Extract response text
                if 'choices' in data and data['choices']:
                    return data['choices'][0]['message']['content']
                
                raise Exception("No response content from DeepSeek")
                
        except Exception as e:
            logger.error(f"DeepSeek completion error: {e}")
            raise
    
    def resolve_model_alias(self, alias: str) -> str:
        """Convert alias to actual model name"""
        aliases = self.config.get('aliases', {
            'deepseek-v3': 'deepseek-chat',
            'deepseek-r1': 'deepseek-reasoner'
        })
        return aliases.get(alias, alias)
    
    def estimate_tokens(self, prompt: str, response: str) -> int:
        """Estimate token count for DeepSeek models"""
        # DeepSeek uses similar tokenization to GPT
        # Approximately 1 token per 4 characters
        total_chars = len(prompt) + len(response)
        return int(total_chars / 4)
    
    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Estimate cost for token usage (using cache miss pricing)"""
        actual_model = self.resolve_model_alias(model)
        settings = self.model_settings.get(actual_model)
        
        if not settings:
            return 0.0
        
        # Using cache miss pricing by default (worst-case scenario)
        input_cost = (input_tokens / 1_000_000) * settings['cost_per_million_input_cache_miss']
        output_cost = (output_tokens / 1_000_000) * settings['cost_per_million_output']
        
        return input_cost + output_cost