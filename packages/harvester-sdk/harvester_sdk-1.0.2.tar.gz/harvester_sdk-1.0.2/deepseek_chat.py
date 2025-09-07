#!/usr/bin/env python3
"""
DeepSeek Interactive Chat with Streaming
A terminal-based chat interface for DeepSeek models with real-time streaming and multi-round conversations

Features:
- Streaming responses for real-time interaction
- Multi-round conversation with context preservation
- Model switching between deepseek-chat and deepseek-reasoner
- Conversation history management
- Export/save functionality
"""
import asyncio
import sys
import os
import json
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import click

# Color codes for terminal output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

class DeepSeekChat:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DeepSeek API key required. Set DEEPSEEK_API_KEY environment variable.")
        
        self.base_url = "https://api.deepseek.com/chat/completions"
        self.conversation_history: List[Dict[str, str]] = []
        self.current_model = "deepseek-chat"
        self.temperature = 0.7
        self.max_tokens = 4096
        self.session = None
        
    def print_welcome(self):
        """Print welcome message and instructions"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}🚀 DeepSeek Interactive Chat{Colors.ENDC}")
        print("=" * 50)
        print(f"{Colors.YELLOW}💡 Commands:{Colors.ENDC}")
        print("  /help     - Show help")
        print("  /model    - Switch model (chat/reasoner)")
        print("  /clear    - Clear conversation history")
        print("  /history  - Show conversation history")
        print("  /save     - Save conversation to file")
        print("  /load     - Load conversation from file")
        print("  /export   - Export as markdown")
        print("  /temp     - Set temperature (0.0-2.0)")
        print("  /tokens   - Set max tokens")
        print("  /paste    - Multi-line input mode")
        print("  /quit     - Exit chat")
        print("=" * 50)
        
    def print_status(self):
        """Print current status"""
        model_name = "DeepSeek Chat" if self.current_model == "deepseek-chat" else "DeepSeek Reasoner"
        print(f"\n{Colors.BLUE}🤖 Model: {model_name} | Temp: {self.temperature} | Max: {self.max_tokens} tokens{Colors.ENDC}")
        print(f"{Colors.GREEN}💬 Type your message or /help for commands...{Colors.ENDC}\n")
    
    async def stream_completion(self, messages: List[Dict[str, str]]) -> str:
        """Stream completion from DeepSeek API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream'
        }
        
        payload = {
            'model': self.current_model,
            'messages': messages,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'stream': True,
            'presence_penalty': 0,
            'frequency_penalty': 0
        }
        
        full_response = ""
        
        try:
            async with self.session.post(
                self.base_url,
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"{Colors.RED}❌ API Error: {error_text}{Colors.ENDC}")
                    return ""
                
                print(f"{Colors.CYAN}🤖 DeepSeek:{Colors.ENDC} ", end='', flush=True)
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        
                        if data == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data)
                            if 'choices' in chunk and chunk['choices']:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    print(content, end='', flush=True)
                                    full_response += content
                        except json.JSONDecodeError:
                            continue
                
                print()  # New line after response
                return full_response
                
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {str(e)}{Colors.ENDC}")
            return ""
    
    def handle_command(self, command: str) -> bool:
        """Handle user commands. Returns True if should continue, False to exit"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == '/quit' or cmd == '/exit':
            return False
        
        elif cmd == '/help':
            self.print_welcome()
        
        elif cmd == '/model':
            if len(parts) > 1:
                model = parts[1].lower()
                if model in ['chat', 'deepseek-chat']:
                    self.current_model = 'deepseek-chat'
                    print(f"{Colors.GREEN}✓ Switched to DeepSeek Chat{Colors.ENDC}")
                elif model in ['reasoner', 'deepseek-reasoner']:
                    self.current_model = 'deepseek-reasoner'
                    print(f"{Colors.GREEN}✓ Switched to DeepSeek Reasoner{Colors.ENDC}")
                else:
                    print(f"{Colors.RED}❌ Invalid model. Use 'chat' or 'reasoner'{Colors.ENDC}")
            else:
                print(f"Current model: {self.current_model}")
                print("Usage: /model [chat|reasoner]")
        
        elif cmd == '/clear':
            self.conversation_history = []
            print(f"{Colors.GREEN}✓ Conversation history cleared{Colors.ENDC}")
        
        elif cmd == '/history':
            if not self.conversation_history:
                print("No conversation history yet.")
            else:
                print(f"\n{Colors.CYAN}📜 Conversation History:{Colors.ENDC}")
                for i, msg in enumerate(self.conversation_history, 1):
                    role_color = Colors.GREEN if msg['role'] == 'user' else Colors.BLUE
                    prefix = "👤 You" if msg['role'] == 'user' else "🤖 DeepSeek"
                    content = msg['content'][:100] + '...' if len(msg['content']) > 100 else msg['content']
                    print(f"{i}. {role_color}{prefix}: {content}{Colors.ENDC}")
        
        elif cmd == '/save':
            filename = parts[1] if len(parts) > 1 else f"deepseek_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            try:
                with open(filename, 'w') as f:
                    json.dump({
                        'model': self.current_model,
                        'timestamp': datetime.now().isoformat(),
                        'messages': self.conversation_history
                    }, f, indent=2)
                print(f"{Colors.GREEN}✓ Conversation saved to {filename}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}❌ Error saving: {str(e)}{Colors.ENDC}")
        
        elif cmd == '/load':
            if len(parts) < 2:
                print("Usage: /load <filename>")
            else:
                try:
                    with open(parts[1], 'r') as f:
                        data = json.load(f)
                        self.conversation_history = data['messages']
                        self.current_model = data.get('model', 'deepseek-chat')
                    print(f"{Colors.GREEN}✓ Conversation loaded from {parts[1]}{Colors.ENDC}")
                except Exception as e:
                    print(f"{Colors.RED}❌ Error loading: {str(e)}{Colors.ENDC}")
        
        elif cmd == '/export':
            filename = parts[1] if len(parts) > 1 else f"deepseek_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            try:
                with open(filename, 'w') as f:
                    f.write(f"# DeepSeek Chat Export\n")
                    f.write(f"**Model**: {self.current_model}\n")
                    f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("---\n\n")
                    
                    for msg in self.conversation_history:
                        if msg['role'] == 'user':
                            f.write(f"### 👤 User\n{msg['content']}\n\n")
                        else:
                            f.write(f"### 🤖 DeepSeek\n{msg['content']}\n\n")
                
                print(f"{Colors.GREEN}✓ Exported to {filename}{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.RED}❌ Error exporting: {str(e)}{Colors.ENDC}")
        
        elif cmd == '/temp' or cmd == '/temperature':
            if len(parts) > 1:
                try:
                    temp = float(parts[1])
                    if 0.0 <= temp <= 2.0:
                        self.temperature = temp
                        print(f"{Colors.GREEN}✓ Temperature set to {temp}{Colors.ENDC}")
                    else:
                        print(f"{Colors.RED}❌ Temperature must be between 0.0 and 2.0{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.RED}❌ Invalid temperature value{Colors.ENDC}")
            else:
                print(f"Current temperature: {self.temperature}")
                print("Usage: /temp <0.0-2.0>")
        
        elif cmd == '/tokens':
            if len(parts) > 1:
                try:
                    tokens = int(parts[1])
                    if 1 <= tokens <= 64000:
                        self.max_tokens = tokens
                        print(f"{Colors.GREEN}✓ Max tokens set to {tokens}{Colors.ENDC}")
                    else:
                        max_val = 64000 if self.current_model == 'deepseek-reasoner' else 8000
                        print(f"{Colors.RED}❌ Max tokens must be between 1 and {max_val}{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.RED}❌ Invalid token value{Colors.ENDC}")
            else:
                print(f"Current max tokens: {self.max_tokens}")
                print("Usage: /tokens <number>")
        
        elif cmd == '/paste':
            print(f"{Colors.YELLOW}📝 Multi-line input mode. Type '###' on a new line to send.{Colors.ENDC}")
            lines = []
            while True:
                line = input()
                if line == '###':
                    break
                lines.append(line)
            
            if lines:
                message = '\n'.join(lines)
                return self.process_message(message)
        
        else:
            print(f"{Colors.RED}❌ Unknown command: {cmd}{Colors.ENDC}")
            print("Type /help for available commands")
        
        return True
    
    def process_message(self, message: str) -> bool:
        """Process a user message (used by /paste command)"""
        # This will be called from within the async context
        return True  # Continue conversation
    
    async def run(self):
        """Main chat loop"""
        self.print_welcome()
        self.print_status()
        
        try:
            while True:
                try:
                    # Get user input
                    user_input = input(f"{Colors.GREEN}👤 You: {Colors.ENDC}")
                    
                    # Check if it's a command
                    if user_input.startswith('/'):
                        if not self.handle_command(user_input):
                            print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.ENDC}")
                            break
                        continue
                    
                    # Skip empty messages
                    if not user_input.strip():
                        continue
                    
                    # Add user message to history
                    self.conversation_history.append({
                        'role': 'user',
                        'content': user_input
                    })
                    
                    # Stream response from DeepSeek
                    response = await self.stream_completion(self.conversation_history)
                    
                    if response:
                        # Add assistant response to history
                        self.conversation_history.append({
                            'role': 'assistant',
                            'content': response
                        })
                    
                    print()  # Extra line for readability
                    
                except KeyboardInterrupt:
                    print(f"\n{Colors.YELLOW}Use /quit to exit or Ctrl+C again to force quit{Colors.ENDC}")
                    continue
                    
        finally:
            if self.session:
                await self.session.close()

def main():
    """Main entry point"""
    # Check for API key
    if not os.getenv('DEEPSEEK_API_KEY'):
        print(f"{Colors.RED}❌ Error: DEEPSEEK_API_KEY environment variable not set{Colors.ENDC}")
        print("Please set your DeepSeek API key:")
        print("export DEEPSEEK_API_KEY='your-api-key-here'")
        return
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='DeepSeek Interactive Chat')
    parser.add_argument('--model', choices=['chat', 'reasoner'], default='chat',
                       help='Initial model to use')
    parser.add_argument('--temperature', type=float, default=0.7,
                       help='Temperature (0.0-2.0)')
    parser.add_argument('--max-tokens', type=int, default=4096,
                       help='Maximum tokens in response')
    args = parser.parse_args()
    
    # Create and configure chat instance
    chat = DeepSeekChat()
    chat.current_model = f"deepseek-{args.model}"
    chat.temperature = args.temperature
    chat.max_tokens = args.max_tokens
    
    # Run the chat
    try:
        asyncio.run(chat.run())
    except KeyboardInterrupt:
        print(f"\n{Colors.CYAN}👋 Goodbye!{Colors.ENDC}")

if __name__ == "__main__":
    main()