# Sacred Wrapper SDK - CLI Reference

## Standardized CLI Tools

All CLI tools follow clear, descriptive naming patterns for non-technical users:

### 🆓 FREEMIUM TIER ($0/month)
**Provider**: Google Gemini 2.5 (Pro & Flash)
- **`batch-code`** - Code transformation engine (batch processes code files)
  - Models: `gemini-2.5-pro` (high quality) & `gemini-2.5-flash` (fast)
  - 5 concurrent workers
  - Perfect for evaluation

### 💼 PROFESSIONAL TIER ($99/month) 
- **`image-cli`** - Image generation CLI (DALL-E, Imagen, etc.)
- **`router-image`** - Smart image routing (automatically selects best model)
- **`style-openai`** - OpenAI style wrapper (simplified OpenAI access)
- **`style-vertex`** - Vertex style wrapper (simplified Google Vertex access)

### 🏭 PREMIUM TIER ($500/month)
- **`batch-image`** - Batch image generation (CSV-driven image creation)
- **`batch-vertex`** - Ultra batch processing (high-volume Vertex operations)
- **`batch-vertex-pro`** - Advanced batch processor (enterprise-grade batching)

### 👑 ENTERPRISE TIER (Custom pricing)
- **`ai-assistant`** - Universal AI orchestrator (handles any AI task with any model)

### 🔧 UTILITIES
- **`license-check`** - License management and validation

## Usage Examples

```bash
# Code transformation (Freemium)
batch-code ~/my-project --model goo-2 --dry-run

# Image generation (Professional)
image-cli paint1 "red living room" --model dalle-3

# Batch image processing (Premium)
batch-image --csv prompts.csv --model goo-4-img

# Universal AI assistant (Enterprise)
ai-assistant maths "prove pythagorean theorem" --model all
ai-assistant code_review "review this function" --model grp-quality
ai-assistant advice "should I start a company?" --model vtx-1
```

## Legacy Compatibility

Old names are mapped to new names for backward compatibility:
- `harvest` → `batch-code`
- `prophet` → `image-cli`
- `imagen-batch` → `batch-image`
- `vertex-batch-ultra` → `batch-vertex`
- `summon` → `ai-assistant`

## Installation

```bash
pip install harvester-sdk

# Verify installation
test-installation

# Check license status
license-check
```