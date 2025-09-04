# Harvester SDK Installation Guide

## Quick Start

```bash
# 1. Clone or navigate to the repository
cd /home/rich/productions/sdk-harvester

# 2. Run the setup script
./setup.sh

# 3. Activate the virtual environment
source venv/bin/activate

# 4. Test the installation
python -c "from harvester_sdk import HarvesterSDK; print('✅ SDK imported successfully!')"
```

## Manual Installation

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .  # Install package in development mode
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```env
# OpenAI (GPT-5, DALL-E 3)
OPENAI_API_KEY=sk-...

# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-...

# Google Cloud (Gemini, Imagen)
GOOGLE_CLOUD_PROJECT=your-project-id

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# xAI (Grok)
XAI_API_KEY=xai-...
```

Or export them in your shell:

```bash
export OPENAI_API_KEY='your-key-here'
export ANTHROPIC_API_KEY='your-key-here'
export GOOGLE_CLOUD_PROJECT='your-project-id'
export DEEPSEEK_API_KEY='your-key-here'
export XAI_API_KEY='your-key-here'
```

### 4. Google Cloud Authentication (for Gemini/Imagen)

```bash
# Install gcloud CLI if needed
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

## Available Models

### Text Generation
- **GPT-5 Series**: `gpt-5`, `gpt-5-mini`, `gpt-5-nano`
- **Gemini 2.5**: `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`
- **Claude**: `claude-opus-4`, `claude-sonnet-4`, `claude-3-5-haiku`
- **Grok**: `grok-4`, `grok-3`, `grok-fast`
- **DeepSeek**: `deepseek-chat`, `deepseek-reasoner`

### Image Generation
- **OpenAI**: `dalle-3`, `gpt-image-1`
- **Google**: `imagen-4`, `imagen-4-ultra`, `imagen-4-fast`

### Multimodal/Vision
- **Grok Vision**: `grok-image` (text model with image understanding)

## Testing Your Installation

### Test Text Generation

```python
from harvester_sdk import HarvesterSDK

sdk = HarvesterSDK(license_key="HSK-PRE-ultimate")

# Test GPT-5
result = await sdk.process_single(
    prompt="What is the meaning of life?",
    model_alias="gpt-5-nano"
)
print(result)
```

### Test Image Generation

```bash
# Using prophet CLI for images
python prophet.py paint1 --model dalle-3 "modern minimalist living room"

# Or using the SDK
python imagen_batch_cli.py --prompts "sunset over mountains" --model imagen-4
```

### Test Multiple Providers

```bash
# Run comprehensive test
python summon.py test_all

# Test specific providers
python test_xai_deepseek.py
python test_gpt5_batch.py
```

## Common Issues

### Missing API Key
```
ValueError: OpenAI API key required
```
**Solution**: Set the appropriate environment variable or add to `.env` file

### Google Cloud Auth Error
```
Failed to authenticate with Google Cloud
```
**Solution**: Run `gcloud auth login` and ensure project is set

### Module Import Error
```
ModuleNotFoundError: No module named 'harvester_sdk'
```
**Solution**: Install package with `pip install -e .` in the project root

## Directory Structure

After installation, outputs will be saved to:
```
~/harvester-sdk/
├── text/
│   ├── openai/
│   ├── google/
│   ├── anthropic/
│   └── ...
└── image/
    ├── dalle3/
    ├── imagen/
    └── ...
```

## License Tiers

- **Freemium**: 5 concurrent workers, 10 batch size
- **Premium**: 20 concurrent workers, 100 batch size  
- **Enterprise**: 50 concurrent workers, 500 batch size
- **Ultimate**: Unlimited workers and batch size

## Support

For issues or questions:
- Check the [Sacred Wrapper documentation](docs/README_SDK.md)
- Review the [providers configuration](config/providers.yaml)
- Examine test scripts for usage examples

Ready to harvest at scale! 🚀