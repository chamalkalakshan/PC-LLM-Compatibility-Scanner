# PC LLM Compatibility Scanner

Automatically detects your PC's hardware and tells you exactly which local LLMs you can run - and how well.

## Features

- **Hardware detection** - CPU, RAM, GPU (VRAM), disk space
- **25+ LLM catalogue** - Llama 3, Mistral, Qwen, DeepSeek-R1, Phi, Gemma, Mixtral and more
- **5-tier rating system** - Excellent / Good / Possible / Slow / No-Go
- **Run mode** - GPU, CPU, Partial GPU offload, Multi-GPU
- **Ollama commands** - Copy-paste ready `ollama run` commands
- **Export** - Save results as JSON for scripting

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the scanner
python main.py
```

## Usage

```bash
# Show all models with full table + top 5 picks
python main.py

# Show only top 10 models your PC can run
python main.py --top 10

# Hide models that won't run on your hardware
python main.py --hide-nogo

# Show only EXCELLENT tier models
python main.py --tier EXCELLENT

# Get detailed info for a specific model
python main.py --detail "Llama 3.1 8B"

# Export results to JSON
python main.py --export-json results.json

# Combine flags
python main.py --hide-nogo --top 8 --export-json my_results.json
```

## Compatibility Tiers

| Tier | Description |
|------|-------------|
| 🚀 EXCELLENT | Fits in GPU VRAM with headroom - fast inference |
| ✅ GOOD | Fits in GPU VRAM (tight) - good performance |
| ⚡ POSSIBLE | Partial GPU offload or CPU inference with plenty of RAM |
| 🐌 SLOW | CPU-only, works but < 2 tokens/sec |
| ❌ NO-GO | Insufficient RAM and VRAM |

## Supported Models

| Family | Models |
|--------|--------|
| Llama | 3.2 1B, 3.2 3B, 3.1 8B, 3.1 70B, 3.1 405B |
| Mistral | 7B, Nemo 12B, Mixtral 8x7B |
| Phi | Phi-3.5 Mini 3.8B, Phi-4 14B |
| Gemma | 2B, 9B, 27B |
| Qwen | 1.5B, 3B, 7B, 14B, 32B, 72B, Coder 7B |
| DeepSeek | R1 Distill 7B, 14B, 32B, 70B |
| CodeLlama | 7B, 34B |

## Requirements

- Python 3.9+
- NVIDIA GPU: `nvidia-smi` must be accessible for accurate VRAM detection
- AMD/Intel GPU: detected via Windows WMI (VRAM may show 4 GB cap on large cards)

## How It Works

1. `scanner/hardware.py` - Detects CPU, RAM, GPU, storage using `psutil`, `py-cpuinfo`, `nvidia-smi`, and PowerShell WMI
2. `scanner/llm_database.py` - Catalogue of 25+ models with Q4-quantised VRAM/RAM requirements
3. `scanner/recommender.py` - Scores each model against your hardware and assigns a tier
4. `scanner/display.py` - Renders everything with `rich` for a polished terminal UI

## Author

Chamalka Lakshan
