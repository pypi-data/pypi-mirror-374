#!/usr/bin/env python3
"""
Sacred Wrapper - Universal Image Generation CLI

A unified interface for all image generation providers with smart model routing,
legacy compatibility, and battle-tested reliability.
"""

import click
import json
import base64
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# License Guardian - Entry point validation  
from license_guardian import check_cli_access
check_cli_access(__file__)

from providers.provider_factory import ProviderFactory
from utils.output_paths import generate_cli_output_directory

# Legacy model compatibility mapping
IMAGE_MODEL_ALIASES = {
    'o1-img': 'dalle-3',      # Old alias -> DALL-E 3
    'o2-img': 'dalle-3',      # Old alias -> DALL-E 3
    'g1-img': 'imagen-3',     # Old alias -> Imagen 3
    'g2-img': 'imagen-4',     # Old alias -> Imagen 4
}

@click.command()
@click.option('--prompt', '-p', required=True, help='Image generation prompt')
@click.option('--model', '-m', default='dalle-3', help='Model: dalle-3, imagen-3, imagen-4, gpt-image-1')
@click.option('--output', '-o', help='Custom output directory (uses sovereign structure by default)')
@click.option('--size', '-s', default='1024x1024', help='Image size (1024x1024, 1792x1024, 1024x1792)')
@click.option('--quality', '-q', default='standard', help='Image quality (standard, hd)')
@click.option('--style', default='vivid', help='Image style (vivid, natural)')
@click.option('--aspect-ratio', '-a', help='Aspect ratio for Imagen models (16:9, 4:3, etc.)')
@click.option('--save-metadata', is_flag=True, help='Save generation metadata as JSON')
def main(prompt, model, output, size, quality, style, aspect_ratio, save_metadata):
    """
    Sacred Wrapper - Universal Image Generation CLI
    
    Generate images using various AI providers with unified interface.
    
    Examples:
        # Generate with DALL-E 3
        image-cli -p "A serene mountain landscape" -m dalle-3
        
        # High quality portrait with custom size
        image-cli -p "Portrait of a wise sage" -m dalle-3 -q hd -s 1024x1792
        
        # Imagen 4 with aspect ratio
        image-cli -p "Futuristic cityscape" -m imagen-4 -a 16:9
        
        # Save with metadata
        image-cli -p "Abstract art" -m gpt-image-1 --save-metadata
    """
    
    # Handle legacy model aliases
    if model in IMAGE_MODEL_ALIASES:
        click.echo(f"🔄 Converting legacy alias '{model}' -> '{IMAGE_MODEL_ALIASES[model]}'")
        model = IMAGE_MODEL_ALIASES[model]
    
    # Generate sovereign output directory
    if not output:
        output = generate_cli_output_directory("image_cli", prompt[:50])
    
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    click.echo(f"🎨 Sacred Wrapper SDK - Image Generation")
    click.echo(f"🤖 Model: {model}")
    click.echo(f"📝 Prompt: {prompt}")
    click.echo(f"📐 Size: {size}")
    click.echo(f"💎 Quality: {quality}")
    click.echo(f"🎭 Style: {style}")
    if aspect_ratio:
        click.echo(f"📏 Aspect Ratio: {aspect_ratio}")
    click.echo(f"📂 Output: {output_path}")
    
    try:
        # Initialize provider
        config_dir = Path(__file__).parent / 'config'
        provider_factory = ProviderFactory(config_dir)
        provider = provider_factory.get_provider(model)
        
        # Prepare parameters based on provider
        params = {
            'prompt': prompt,
            'model': model
        }
        
        # Provider-specific parameters
        if 'dalle' in model or 'gpt-image' in model:
            # OpenAI parameters
            params.update({
                'size': size,
                'quality': quality,
                'style': style
            })
        elif 'imagen' in model:
            # Vertex AI Imagen parameters
            if aspect_ratio:
                params['aspect_ratio'] = aspect_ratio
            params.update({
                'safety_filter_level': 'block_some',
                'person_generation': 'allow_adult',
                'add_watermark': True
            })
        
        click.echo("🎨 Generating image...")
        
        # Generate image
        result = provider.generate_image(**params)
        
        # Parse result
        if isinstance(result, str):
            result = json.loads(result)
        
        # Process and save image
        if result.get('images') and len(result['images']) > 0:
            image_data = result['images'][0]
            
            if 'b64_json' in image_data:
                # Decode and save image
                image_bytes = base64.b64decode(image_data['b64_json'])
                
                # Generate filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"image_{timestamp}.png"
                filepath = output_path / filename
                
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                
                click.echo(f"✅ Image saved: {filepath}")
                
                # Save metadata if requested
                if save_metadata:
                    metadata = {
                        'prompt': prompt,
                        'model': model,
                        'parameters': params,
                        'filename': filename,
                        'timestamp': datetime.now().isoformat(),
                        'safety_rating': image_data.get('safety_rating', 'unknown'),
                        'revised_prompt': image_data.get('revised_prompt', prompt)
                    }
                    
                    metadata_file = output_path / f"metadata_{timestamp}.json"
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    
                    click.echo(f"📄 Metadata saved: {metadata_file}")
                
                return 0
            else:
                click.echo("❌ No image data in response")
                return 1
        else:
            click.echo("❌ No images in response")
            return 1
            
    except Exception as e:
        click.echo(f"❌ Error generating image: {str(e)}")
        return 1

if __name__ == '__main__':
    main()