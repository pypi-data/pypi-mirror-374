#!/usr/bin/env python3
"""
Harvester SDK - Unified CLI
© 2025 QUANTUM ENCODING LTD
Contact: info@quantumencoding.io
Website: https://quantumencoding.io

The Master Conductor for all AI processing capabilities

This is the central command interface for the entire SDK, providing unified access to:
- Batch text processing from CSV
- Directory processing with templates
- Image generation and processing
- Interactive chat interfaces
- Live search capabilities

Usage:
    harvester batch --provider openai /path/to/data.csv
    harvester process --template refactor --model gpt-5 /path/to/code
    harvester image --provider dalle3 "A beautiful sunset"
    harvester chat --provider grok
    harvester search "latest AI news" --provider grok
"""

import click
import sys
import os
import asyncio
import subprocess
import json
import time
import threading
import queue
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

# License Guardian - Entry point validation
from license_guardian import check_cli_access
check_cli_access(__file__)

@click.group()
@click.version_option(version='1.0.0', prog_name='Harvester SDK by Quantum Encoding Ltd')
def cli():
    """
    🚀 Harvester SDK - Unified CLI
    
    © 2025 QUANTUM ENCODING LTD
    📧 Contact: info@quantumencoding.io
    🌐 Website: https://quantumencoding.io
    
    The Master Conductor for all AI processing capabilities.
    Use 'harvester COMMAND --help' for more information on each command.
    """
    pass

@cli.command('batch')
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--provider', '-p', help='AI provider to use')
@click.option('--model', '-m', help='Model to use (or group like grp-fast, grp-quality)')
@click.option('--template', '-t', default='default', help='Template to apply')
@click.option('--output', '-o', help='Output directory')
@click.option('--parallel', default=5, help='Number of parallel workers')
@click.option('--image', is_flag=True, help='Process as image generation batch')
def batch_command(csv_file, provider, model, template, output, parallel, image):
    """Process CSV batch with AI providers (text or image)"""
    if image:
        click.echo("🎨 Batch image processing")
        # Route to image batch processor
        cmd = [
            sys.executable,
            'batch_vertex_processor.py',  # Or appropriate image batch processor
            csv_file
        ]
        if model:
            cmd.extend(['--model', model])
        if output:
            cmd.extend(['--output', output])
    else:
        click.echo("📝 Batch text processing from CSV")
        # Use csv_processor for CSV batch processing
        cmd = [
            sys.executable,
            'csv_processor.py',
            'process',
            csv_file
        ]
        if model:
            cmd.extend(['--model', model])
        if template:
            cmd.extend(['--template', template])
        if output:
            cmd.extend(['--output', output])
    
    subprocess.run(cmd)

@cli.command('process')
@click.argument('directory', type=click.Path(exists=True))
@click.option('--template', '-t', required=True, help='Template number or name to use')
@click.option('--model', '-m', default='gemini-2.5-flash', help='Model to use (or "all" for multi-provider)')
@click.option('--parallel', '-p', default=20, help='Number of parallel workers')
@click.option('--pattern', default='**/*', help='File pattern to match')
@click.option('--output', '-o', help='Output directory')
@click.option('--max-files', default=100, help='Maximum files to process')
def process_command(directory, template, model, parallel, pattern, output, max_files):
    """Process directory with templates (formerly batch_code)"""
    click.echo(f"📁 Processing directory: {directory}")
    click.echo(f"📋 Template: {template}")
    
    # Check for --model all flag
    if model.lower() == 'all':
        # Import Divine Arbiter to check permissions
        from core.divine_arbiter import get_divine_arbiter
        arbiter = get_divine_arbiter()
        
        if not arbiter.check_model_all_permission():
            click.echo("⚠️  Note: --model all requires Premium tier")
            click.echo("📍 Falling back to single model: gemini-2.5-flash")
            model = 'gemini-2.5-flash'
        else:
            click.echo("🌌 GALACTIC FEDERATION MODE ACTIVATED")
            click.echo("⚡ Processing with ALL providers in parallel!")
    
    click.echo(f"🤖 Model: {model}")
    click.echo(f"⚡ Parallel workers: {parallel}")
    
    # Route to process_dir (renamed batch_code)
    cmd = [
        sys.executable,
        'process_dir.py',
        '--source', directory,
        '--template', f'{template}.j2' if not template.endswith('.j2') else template,
        '--model', model,
        '--workers', str(parallel),
        '--file-pattern', pattern,
        '--max-files', str(max_files)
    ]
    
    if output:
        cmd.extend(['--output', output])
    
    subprocess.run(cmd)

@cli.command('image')
@click.argument('prompt', required=False)
@click.option('--model', '-m', default='dalle-3', help='Image model (dalle-3, dall-e-2, imagen, etc.)')
@click.option('--template', '-t', help='Style template (cosmic_duck, professional, etc.)')
@click.option('--size', default='1024x1024', help='Image size (1024x1024, 1792x1024, etc.)')
@click.option('--save', '-s', help='Save image to specific file path')
@click.option('--batch', type=click.Path(exists=True), help='Process batch from CSV file')
def image_command(prompt, model, template, size, save, batch):
    """Generate images with AI models
    
    Two ways to generate images:
    
    1. Single image with command args:
        harvester image "two ducks and a swan" --model dalle-3
        harvester image "cosmic scene" --model dalle-3 --template cosmic_duck
        harvester image "professional headshot" --model imagen --size 1792x1024
    
    2. Batch generation from CSV:
        harvester image --batch images.csv
        
        CSV format: prompt,model,template,size,save
        Example row: "two ducks,dalle-3,cosmic_duck,1024x1024,duck.png"
    """
    # Map models to providers automatically  
    model_to_provider = {
        'dalle-3': 'dalle3',
        'dall-e-3': 'dalle3', 
        'dalle-2': 'dalle2',
        'dall-e-2': 'dalle2',
        'imagen': 'vertex_image',
        'imagen-3': 'vertex_image',
        'stable-diffusion': 'stability',
        'sd3': 'stability'
    }
    
    # Validate that either prompt or batch is provided
    if not batch and not prompt:
        click.echo("❌ Either provide a prompt or use --batch with a CSV file")
        click.echo("\nExamples:")
        click.echo("  harvester image 'two ducks and a swan' --model dalle-3")
        click.echo("  harvester image --batch images.csv")
        return
    
    provider = model_to_provider.get(model.lower(), 'dalle3')
    
    # Apply template to prompt if specified
    if template and prompt:
        if template == 'cosmic_duck':
            prompt = f"{prompt}, cosmic nebula background, ethereal lighting, space fantasy art style"
        elif template == 'professional':
            prompt = f"{prompt}, professional photography, clean background, high quality"
        elif template == 'artistic':
            prompt = f"{prompt}, digital art, vibrant colors, artistic composition"
        # Add more templates as needed
    
    if batch:
        click.echo(f"🎨 Batch image generation from: {batch}")
        click.echo("📋 CSV should have columns: prompt, model, template (optional), size (optional), filename (optional)")
        click.echo("   Example: 'two ducks,dalle-3,cosmic_duck,1024x1024,duck_image.png'")
        click.echo()
        
        # Check if this is a vertex/imagen batch that should use vertex_batch_ultra.py
        try:
            import pandas as pd
            df = pd.read_csv(batch)
            models_in_batch = df['model'].str.lower() if 'model' in df.columns else ['dalle-3']
            
            # If any imagen models detected, offer vertex batch processing
            imagen_models = [m for m in models_in_batch if 'imagen' in str(m)]
            if imagen_models:
                vertex_script = Path(__file__).parent.parent / 'knowledge-query-system' / 'harvesting_engine' / 'vertex_batch_ultra.py'
                if vertex_script.exists():
                    click.echo(f"🚀 Detected Imagen models: {set(imagen_models)}")
                    click.echo(f"💡 For optimized Imagen processing, consider using:")
                    click.echo(f"   python {vertex_script} process {batch} --concurrency 15")
                    click.echo()
        except Exception:
            pass
        
        cmd = [sys.executable, 'image_cli.py', 'batch', batch]
        # Let the image_cli handle the model mapping and templates
    else:
        click.echo(f"🎨 Generating image with {model}: {prompt[:50]}...")
        cmd = [
            sys.executable, 'image_cli.py', 'generate', prompt,
            '--provider', provider, '--model', model, '--size', size
        ]
        if save:
            cmd.extend(['--save', save])
        else:
            # Auto-save with descriptive filename
            safe_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_prompt.replace(' ', '_')}_{model}.png"
            cmd.extend(['--save', filename])
            click.echo(f"💾 Will save as: {filename}")
    
    subprocess.run(cmd)

@cli.command('templates')
@click.option('--type', '-t', default='image', type=click.Choice(['image', 'text', 'batch']), help='Template type')
@click.option('--category', '-c', help='Template category (blog, product, universal, etc.)')
@click.option('--list', '-l', is_flag=True, help='List available templates')
@click.option('--copy', help='Copy template to current directory')
def templates_command(type, category, list, copy):
    """Manage batch processing templates
    
    Examples:
        harvester templates --list                    # List all templates
        harvester templates --copy image_batch_blog   # Copy blog template
        harvester templates --type image --category blog  # Show blog image template
    """
    templates_dir = Path(__file__).parent / 'templates'
    
    if list:
        click.echo("📋 Available Templates:")
        click.echo()
        
        # Image batch templates
        click.echo("🎨 Image Batch Templates:")
        for template_file in templates_dir.glob('image_batch_*.csv'):
            category_name = template_file.stem.replace('image_batch_', '')
            click.echo(f"   • image_batch_{category_name}")
            
            # Show first few rows as preview
            try:
                import pandas as pd
                df = pd.read_csv(template_file)
                click.echo(f"     Columns: {', '.join(df.columns)}")
                click.echo(f"     Examples: {len(df)} rows")
                click.echo(f"     Usage: harvester templates --copy image_batch_{category_name}")
            except:
                pass
            click.echo()
        
        click.echo("💡 Create your own prompts:")
        click.echo("   1. Copy a template: harvester templates --copy image_batch_blog")
        click.echo("   2. Edit the CSV with your prompts")  
        click.echo("   3. Process: harvester image --batch your_prompts.csv")
        click.echo()
        click.echo("🤖 Or ask any AI to fill the template:")
        click.echo("   'Hey Claude/Gemini, create 50 blog header prompts using this CSV format'")
        return
    
    if copy:
        template_file = templates_dir / f"{copy}.csv"
        if template_file.exists():
            import shutil
            dest = Path.cwd() / f"{copy}.csv"
            shutil.copy2(template_file, dest)
            click.echo(f"✅ Copied template to: {dest}")
            click.echo(f"📝 Edit the CSV and run: harvester image --batch {dest}")
        else:
            click.echo(f"❌ Template '{copy}' not found. Use --list to see available templates")
        return
    
    if type == 'image' and category:
        template_file = templates_dir / f"image_batch_{category}.csv"
        if template_file.exists():
            click.echo(f"📋 Template: image_batch_{category}")
            click.echo(f"📁 File: {template_file}")
            click.echo()
            
            # Show template content
            try:
                with open(template_file, 'r') as f:
                    lines = f.readlines()[:6]  # Show header + 5 examples
                    for i, line in enumerate(lines):
                        if i == 0:
                            click.echo(f"Header: {line.strip()}")
                        else:
                            click.echo(f"Row {i}: {line.strip()[:80]}...")
            except:
                pass
            
            click.echo(f"\n💡 Copy with: harvester templates --copy image_batch_{category}")
        else:
            click.echo(f"❌ Template 'image_batch_{category}' not found")

@cli.command('chat')
@click.option('--provider', '-p', default='grok', help='Chat provider (grok, deepseek, openai, anthropic, etc.)')
@click.option('--model', '-m', help='Specific model to use')
@click.option('--search', is_flag=True, help='Enable live search (Grok only)')
@click.option('--functions', is_flag=True, help='Enable function calling')
def chat_command(provider, model, search, functions):
    """Start interactive chat with AI provider"""
    if provider == 'grok':
        click.echo("💬 Starting Grok chat...")
        cmd = [sys.executable, 'grok_chat.py']
        if model:
            cmd.extend(['--model', model])
        if search:
            cmd.append('--search')
        if functions:
            cmd.append('--functions')
    elif provider == 'deepseek':
        click.echo("💬 Starting DeepSeek chat...")
        cmd = [sys.executable, 'deepseek_chat.py']
        if model:
            # Map model names for DeepSeek
            if model in ['chat', 'deepseek-chat']:
                cmd.extend(['--model', 'chat'])
            elif model in ['reasoner', 'deepseek-reasoner']:
                cmd.extend(['--model', 'reasoner'])
    else:
        click.echo(f"💬 Starting AI assistant with {provider}...")
        cmd = [sys.executable, 'ai_assistant.py']
        if model:
            cmd.extend(['--model', model])
        if provider:
            cmd.extend(['--provider', provider])
    
    subprocess.run(cmd)

@cli.command('message')
@click.option('--model', '-m', default='gemini-2.5-flash', help='Model to use for conversation')
@click.option('--system', '-s', help='System prompt/context')
@click.option('--temperature', '-t', default=0.7, help='Response creativity (0.0-2.0)')
@click.option('--save', is_flag=True, help='Save conversation history to file')
@click.option('--max-tokens', default=4000, help='Maximum response length')
def message_command(model, system, temperature, save, max_tokens):
    """Start turn-based conversation with AI (non-streaming)"""
    import json
    from datetime import datetime
    
    click.echo("💬 Harvester SDK - Turn-Based Conversation")
    click.echo("© 2025 QUANTUM ENCODING LTD | info@quantumencoding.io")
    click.echo(f"🤖 Model: {model}")
    click.echo(f"🌡️  Temperature: {temperature}")
    if system:
        click.echo(f"⚙️  System: {system}")
    click.echo("Type 'exit', 'quit', or press Ctrl+C to end conversation")
    click.echo("=" * 60)
    
    # Initialize components
    from providers.provider_factory import ProviderFactory
    
    provider_factory = ProviderFactory()
    conversation_history = []
    
    # Add system message if provided
    if system:
        conversation_history.append({"role": "system", "content": system})
    
    try:
        provider = provider_factory.get_provider(model)
        click.echo(f"✅ Connected to {model}")
    except Exception as e:
        click.echo(f"❌ Error connecting to {model}: {e}")
        return
    
    conversation_count = 0
    
    # Enable readline for better input handling (paste support)
    try:
        import readline
        # Set up readline for better paste handling
        readline.set_startup_hook(None)
    except ImportError:
        pass  # readline not available on Windows
    
    try:
        while True:
            # Get user input with proper editing support
            try:
                click.echo("\n👤 You: ", nl=False)
                sys.stdout.flush()
                
                # Enhanced input with better editing support
                def get_input_with_editing():
                    import select
                    
                    # Read first line with full readline editing support
                    first_line = input()
                    if not first_line.strip():
                        return ""
                    
                    lines = [first_line]
                    
                    # Check for pasted multi-line content
                    try:
                        while hasattr(select, 'select') and select.select([sys.stdin], [], [], 0)[0]:
                            additional_line = input()
                            lines.append(additional_line)
                    except (EOFError, OSError, AttributeError):
                        pass
                    
                    # If single line, return as-is (full editing was available)
                    if len(lines) == 1:
                        return first_line
                    
                    # Check if any line is an exit command
                    for line in lines:
                        if line.strip().lower() in ['exit', 'quit']:
                            return line.strip()
                    
                    # Multi-line detected - offer editing options
                    combined = '\n'.join(lines)
                    click.echo(f"\n📋 Multi-line input detected ({len(lines)} lines)")
                    
                    # Show preview
                    preview_lines = lines[:2]
                    for i, line in enumerate(preview_lines, 1):
                        display_line = line[:50] + "..." if len(line) > 50 else line
                        click.echo(f"   {i}: {display_line}")
                    if len(lines) > 2:
                        click.echo(f"   ... and {len(lines) - 2} more lines")
                    
                    # Simple choice: use as-is or re-enter
                    click.echo("\nOptions:")
                    click.echo("  [Enter] - Use this text")
                    click.echo("  [e] - Re-enter text with full editing")
                    choice = input("Choice: ").strip().lower()
                    
                    if choice == 'e':
                        # Let them re-enter with a pre-filled readline buffer
                        click.echo("\n✏️  Enter your text (with full backspace/editing support):")
                        # Pre-fill the readline buffer with the combined text (spaces instead of newlines)
                        combined_single_line = combined.replace('\n', ' ')
                        return input(f"Re-edit: ")
                    else:
                        return combined
                
                user_input = get_input_with_editing().strip()
                
                # Handle empty input
                if not user_input:
                    continue
                    
            except (EOFError, KeyboardInterrupt):
                break
            
            if user_input.lower() in ['exit', 'quit']:
                break
                
            conversation_count += 1
            
            # Add user message to history
            conversation_history.append({"role": "user", "content": user_input})
            
            # Show thinking indicator
            click.echo("🤔 Thinking...")
            
            try:
                # Use direct provider approach with model parameter
                response = asyncio.run(provider.complete(user_input, model))
                
                if response:
                    # Response is typically a string from complete method
                    assistant_message = str(response)
                    
                    # Display response with nice formatting
                    click.echo(f"\n🤖 {model}:")
                    click.echo("-" * 50)
                    click.echo(assistant_message)
                    click.echo("-" * 50)
                    
                    # Add assistant response to history
                    conversation_history.append({"role": "assistant", "content": assistant_message})
                    
                    # Save conversation periodically if requested
                    if save and conversation_count % 5 == 0:  # Save every 5 exchanges
                        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        conv_file = f"conversation_{model.replace('/', '_').replace('-', '_')}_{timestamp}.json"
                        with open(conv_file, 'w') as f:
                            json.dump({
                                "model": model,
                                "timestamp": timestamp,
                                "temperature": temperature,
                                "system": system,
                                "conversation": conversation_history
                            }, f, indent=2)
                        click.echo(f"💾 Conversation saved to {conv_file}")
                
                else:
                    click.echo("❌ No response received")
                    
            except Exception as e:
                click.echo(f"❌ Error getting response: {e}")
                continue
    
    except KeyboardInterrupt:
        pass
    
    # Final save if requested
    if save and conversation_count > 0:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        conv_file = f"conversation_{model.replace('/', '_').replace('-', '_')}_{timestamp}_final.json"
        with open(conv_file, 'w') as f:
            json.dump({
                "model": model,
                "timestamp": timestamp,
                "temperature": temperature,
                "system": system,
                "total_exchanges": conversation_count,
                "conversation": conversation_history
            }, f, indent=2)
        click.echo(f"\n💾 Final conversation saved to {conv_file}")
    
    click.echo(f"\n👋 Conversation ended. Total exchanges: {conversation_count}")
    click.echo("Thank you for using Harvester SDK!")

@cli.command('search')
@click.argument('query')
@click.option('--provider', '-p', default='grok', help='Search provider (currently only grok)')
@click.option('--model', '-m', default='grok-4', help='Model to use')
@click.option('--sources', multiple=True, default=['web', 'x', 'news'], help='Search sources')
@click.option('--country', help='Country code for results')
@click.option('--format', '-f', type=click.Choice(['text', 'json']), default='text', help='Output format')
@click.option('--save', '-s', help='Save results to file')
def search_command(query, provider, model, sources, country, format, save):
    """Search the web with AI-enhanced results"""
    if provider != 'grok':
        click.echo(f"⚠️  Search is currently only available with Grok provider")
        return
    
    click.echo(f"🔍 Searching: {query}")
    cmd = [
        sys.executable,
        'grok_search.py',
        query,
        '--model', model,
        '--format', format
    ]
    
    if sources:
        cmd.extend(['--sources'] + list(sources))
    if country:
        cmd.extend(['--country', country])
    if save:
        cmd.extend(['--save', save])
    
    subprocess.run(cmd)

@cli.command('structured')
@click.argument('prompt')
@click.option('--schema', '-s', help='Schema type: person, review, meeting, code, analysis', default='analysis')
@click.option('--model', '-m', default='gemini-2.5-flash', help='Model to use')
@click.option('--output', '-o', help='Output file to save structured JSON')
def structured_command(prompt, schema, model, output):
    """Generate structured output with schema validation (Premium feature)"""
    click.echo(f"🎯 Structured Output Generation")
    
    # Check tier permission first
    from core.divine_arbiter import get_divine_arbiter
    arbiter = get_divine_arbiter()
    
    if not arbiter.check_structured_output_permission():
        click.echo("⚠️  Structured output requires Premium tier")
        return
    
    click.echo(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
    click.echo(f"📋 Schema: {schema}")
    click.echo(f"🤖 Model: {model}")
    
    # For now, show what would happen
    click.echo("\n✅ Premium tier access confirmed!")
    click.echo("🎯 Would generate structured output with schema validation")
    click.echo("📊 Would include automatic retry on validation failures")
    
    if output:
        click.echo(f"💾 Would save to: {output}")

@cli.command('functions')
@click.argument('function_name', required=False)
@click.option('--list', 'list_functions', is_flag=True, help='List available functions for current tier')
@click.option('--args', help='Function arguments as JSON string')
@click.option('--file', help='Read function arguments from JSON file')
def functions_command(function_name, list_functions, args, file):
    """Execute functions and tools (Professional+ feature)"""
    click.echo("🔧 FUNCTION CALLING & TOOL USE")
    click.echo("=" * 60)
    
    # Check tier permission first
    from core.divine_arbiter import get_divine_arbiter
    arbiter = get_divine_arbiter()
    
    if not arbiter.check_function_calling_permission():
        click.echo("⚠️  Function calling requires Professional tier or higher")
        return
    
    # Import SDK for function calling
    import asyncio
    import json
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from harvester_sdk.sdk import HarvesterSDK
    
    async def run_function_command():
        sdk = HarvesterSDK()
        
        if list_functions:
            # List available functions
            try:
                functions = sdk.list_available_functions()
            except Exception as e:
                click.echo(f"❌ Error listing functions: {e}")
                return
            
            if not functions:
                click.echo("ℹ️  Function calling is available at Professional tier and above")
                click.echo("📋 Basic functions available at Professional tier:")
                click.echo("  • read_file - Read contents of a file")
                click.echo("  • list_files - List files in a directory")
                click.echo("  • get_weather - Get current weather (mock)")
                click.echo()
                click.echo("🎯 Premium tier unlocks:")
                click.echo("  • write_file - Write content to files")
                click.echo("  • web_search - Search the web")
                click.echo("  • execute_code - Run code in sandbox")
                click.echo("  • analyze_image - Computer vision")
                click.echo("  • database_query - Query databases")
                click.echo()
                click.echo("🌟 Upgrade to Premium: https://quantumencoding.io/premium")
                return
            
            click.echo(f"📋 Available Functions ({arbiter.current_tier.upper()} tier):")
            click.echo()
            
            for name, info in functions.items():
                click.echo(f"🔧 {name}")
                click.echo(f"   📝 {info['description']}")
                click.echo(f"   📂 Category: {info['category']}")
                click.echo(f"   🔒 Security: {info['security_level']}")
                
                if info['parameters']:
                    click.echo("   📋 Parameters:")
                    for param_name, param_info in info['parameters'].items():
                        required = " (required)" if param_info.get('required', False) else ""
                        click.echo(f"     • {param_name}: {param_info.get('type', 'any')}{required}")
                        if param_info.get('description'):
                            click.echo(f"       └─ {param_info['description']}")
                click.echo()
            
            return
        
        if not function_name:
            click.echo("❌ Please specify a function name or use --list to see available functions")
            click.echo("Example: harvester functions read_file --args '{\"file_path\": \"/path/to/file.txt\"}'")
            return
        
        # Parse arguments
        arguments = {}
        if args:
            try:
                arguments = json.loads(args)
            except json.JSONDecodeError as e:
                click.echo(f"❌ Invalid JSON in --args: {e}")
                return
        elif file:
            try:
                with open(file, 'r') as f:
                    arguments = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                click.echo(f"❌ Error reading arguments file: {e}")
                return
        
        # Execute function
        click.echo(f"🔧 Executing: {function_name}")
        click.echo(f"📋 Arguments: {arguments}")
        click.echo()
        
        try:
            result = await sdk.call_function(function_name, arguments)
            
            if result.success:
                click.echo("✅ Function executed successfully!")
                click.echo(f"📤 Result: {result.result}")
                
                if result.metadata:
                    click.echo(f"📊 Metadata: {result.metadata}")
            else:
                click.echo(f"❌ Function failed: {result.error}")
                
        except Exception as e:
            click.echo(f"❌ Error executing function: {e}")
    
    # Run the async function
    asyncio.run(run_function_command())

@cli.command('tier')
def tier_command():
    """Display license tier and capabilities"""
    click.echo("🎫 HARVESTER SDK LICENSE STATUS")
    click.echo("=" * 60)
    
    # Get tier information from Divine Arbiter
    from core.divine_arbiter import get_divine_arbiter
    arbiter = get_divine_arbiter()
    capabilities = arbiter.get_tier_capabilities()
    
    click.echo(f"📊 Current Tier: {capabilities['tier'].upper()}")
    click.echo(f"⚖️  Sovereignty: {capabilities['sovereignty'].upper()}")
    click.echo(f"👷 Max Workers: {capabilities['max_workers']}")
    click.echo(f"🌐 Max Providers: {capabilities['max_providers']}")
    click.echo(f"🎯 Model All: {'✅ ENABLED' if capabilities['model_all'] else '❌ DISABLED'}")
    click.echo(f"⚡ Parallel Providers: {'✅ ENABLED' if capabilities['parallel_providers'] else '❌ DISABLED'}")
    click.echo(f"🎯 Structured Output: {'✅ ENABLED' if capabilities['structured_output'] else '❌ DISABLED'}")
    click.echo(f"🔧 Function Calling: {capabilities['function_calling'].upper()}")
    click.echo(f"📝 Description: {capabilities['description']}")
    click.echo("=" * 60)
    
    if capabilities['tier'] in ['freemium', 'professional']:
        click.echo("\n💎 UPGRADE TO PREMIUM FOR:")
        click.echo("  • Galactic Federation access (75+ workers)")
        click.echo("  • Enable --model all flag")
        click.echo("  • Multi-provider parallel execution")
        click.echo("  • 🎯 Structured Output with schema validation")
        click.echo("  • 🔧 Function Calling & Tool Use (web, code, data)")
        click.echo("  • Type-safe AI responses")
        click.echo("  • 10x throughput boost")
        click.echo("\n🌟 Visit: https://quantumencoding.io/premium")
    elif capabilities['tier'] == 'premium':
        click.echo("\n✨ PREMIUM TIER ACTIVE")
        click.echo("You have access to the Galactic Federation!")
        click.echo("🎯 Structured Outputs with schema validation enabled")
        click.echo("🔧 Function Calling & Tool Use with full tool library")
        click.echo("Use --model all to unleash multi-provider parallelism")
    elif capabilities['tier'] == 'enterprise':
        click.echo("\n👑 ENTERPRISE TIER ACTIVE")
        click.echo("You have unlimited access to all features!")
        click.echo("The Federation awaits your command.")

@cli.command('status')
@click.option('--job-id', help='Check specific job status')
@click.option('--all', is_flag=True, help='Show all jobs')
def status_command(job_id, all):
    """Check batch job status"""
    click.echo("📊 Checking batch status...")
    cmd = [sys.executable, 'batch_status.py']
    
    if job_id:
        cmd.extend(['--job', job_id])
    elif all:
        cmd.append('--all')
    
    subprocess.run(cmd)

@cli.command('json')
@click.argument('json_file', type=click.Path(exists=True))
@click.option('--model', '-m', default='vtx-1', help='Model to use')
@click.option('--template', '-t', default='advice', help='Template to apply')
@click.option('--output', '-o', help='Output file')
def json_command(json_file, model, template, output):
    """Process single JSON request with AI"""
    click.echo(f"📄 Processing JSON request: {json_file}")
    cmd = [
        sys.executable,
        'json_processor.py',
        json_file,
        '--model', model,
        '--template', template
    ]
    
    if output:
        cmd.extend(['--output', output])
    
    subprocess.run(cmd)

@cli.command('convert')
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output CSV file')
@click.option('--format', '-f', help='Input format (auto-detected if not specified)')
def convert_command(input_file, output, format):
    """Convert any file format to CSV for batch processing"""
    click.echo(f"🔄 Converting {input_file} to CSV...")
    cmd = [
        sys.executable,
        'csv_processor.py',
        'convert',
        input_file
    ]
    
    if output:
        cmd.extend(['--output', output])
    if format:
        cmd.extend(['--format', format])
    
    subprocess.run(cmd)

@cli.command('list-models')
@click.option('--provider', '-p', help='Filter by provider')
@click.option('--groups', is_flag=True, help='Show model groups')
def list_models_command(provider, groups):
    """List available models and providers"""
    click.echo("🤖 Available Models and Providers\n")
    
    # Import provider factory to list models
    from providers.provider_factory import ProviderFactory
    factory = ProviderFactory()
    
    if groups:
        click.echo("Model Groups:")
        click.echo("  grp-fast     : Fast, efficient models")
        click.echo("  grp-quality  : High quality, slower models")
        click.echo("  grp-code     : Optimized for code generation")
        click.echo("  all          : All available models\n")
    
    click.echo("Providers and Models:")
    for provider_name in factory.list_providers():
        if provider and provider not in provider_name:
            continue
        click.echo(f"\n  {provider_name}:")
        models = factory.list_models()
        provider_models = [m for m in models if provider_name in m.lower() or m.startswith(provider_name[:3])]
        for model in provider_models[:5]:  # Show first 5 models per provider
            click.echo(f"    - {model}")

@cli.command('config')
@click.option('--show', is_flag=True, help='Show current configuration')
@click.option('--set-key', nargs=2, help='Set API key (provider, key)')
@click.option('--test', help='Test provider configuration')
def config_command(show, set_key, test):
    """Manage SDK configuration and API keys"""
    if show:
        click.echo("📋 Current Configuration:\n")
        env_vars = {
            'ANTHROPIC_API_KEY': '✓' if os.getenv('ANTHROPIC_API_KEY') else '✗',
            'OPENAI_API_KEY': '✓' if os.getenv('OPENAI_API_KEY') else '✗',
            'GEMINI_API_KEY': '✓' if os.getenv('GEMINI_API_KEY') else '✗',
            'XAI_API_KEY': '✓' if os.getenv('XAI_API_KEY') else '✗',
            'DEEPSEEK_API_KEY': '✓' if os.getenv('DEEPSEEK_API_KEY') else '✗',
        }
        for key, status in env_vars.items():
            click.echo(f"  {key}: {status}")
    
    elif set_key:
        provider, key = set_key
        env_var = f"{provider.upper()}_API_KEY"
        click.echo(f"Setting {env_var}...")
        # Note: This only sets for current session
        os.environ[env_var] = key
        click.echo(f"✓ {env_var} set for this session")
        click.echo("To persist, add to your .env file or shell profile")
    
    elif test:
        click.echo(f"Testing {test} provider...")
        # Could implement provider test here
        click.echo("Provider test functionality coming soon!")

if __name__ == '__main__':
    cli()