from dataclasses import dataclass, field
from typing import List


@dataclass
class LLMModel:
    name: str
    family: str
    parameters_b: float
    min_vram_gb: float       # GPU inference, Q4 quant
    rec_vram_gb: float       # GPU inference, comfortable
    min_ram_gb: float        # CPU-only inference, Q4 quant
    rec_ram_gb: float        # CPU-only, comfortable
    use_cases: List[str]
    description: str
    ollama_tag: str          # ollama pull <tag>
    context_length: int      # max context tokens
    released_year: int


# ---------------------------------------------------------------------------
# LLM catalogue - requirements based on Q4_K_M GGUF quantization
#
# MoE (mixture-of-experts) models list total parameters, since Q4 inference
# keeps every expert resident in memory even though only a fraction activate
# per token - active-parameter count (noted in the description) is what
# drives generation speed, not memory footprint.
# ---------------------------------------------------------------------------
LLM_DATABASE: List[LLMModel] = [

    # -- Tiny models (< 2B) -------------------------------------------------
    LLMModel(
        name="Llama 3.2 1B",
        family="Llama", parameters_b=1.0,
        min_vram_gb=1.5, rec_vram_gb=2.0,
        min_ram_gb=3.0,  rec_ram_gb=4.0,
        use_cases=["chat", "summarisation", "edge devices"],
        description="Ultra-lightweight model from Meta. Great for quick tasks on any hardware.",
        ollama_tag="llama3.2:1b", context_length=131072, released_year=2024,
    ),
    LLMModel(
        name="Qwen3 0.6B",
        family="Qwen", parameters_b=0.6,
        min_vram_gb=1.0, rec_vram_gb=1.5,
        min_ram_gb=2.0,  rec_ram_gb=3.0,
        use_cases=["chat", "edge devices", "on-device agents"],
        description="Alibaba's smallest Qwen3 model with an optional 'thinking' reasoning mode.",
        ollama_tag="qwen3:0.6b", context_length=32768, released_year=2025,
    ),
    LLMModel(
        name="Gemma 3 1B",
        family="Gemma", parameters_b=1.0,
        min_vram_gb=1.5, rec_vram_gb=2.0,
        min_ram_gb=3.0,  rec_ram_gb=4.0,
        use_cases=["chat", "summarisation", "edge devices"],
        description="Google's newest tiny model - strong quality-to-size ratio, runs almost anywhere.",
        ollama_tag="gemma3:1b", context_length=32768, released_year=2025,
    ),

    # -- Small models (2-6B) --------------------------------------------------
    LLMModel(
        name="Llama 3.2 3B",
        family="Llama", parameters_b=3.0,
        min_vram_gb=2.5, rec_vram_gb=4.0,
        min_ram_gb=4.0,  rec_ram_gb=6.0,
        use_cases=["chat", "summarisation", "mobile"],
        description="Small but capable Llama 3.2 model. Punches above its size.",
        ollama_tag="llama3.2:3b", context_length=131072, released_year=2024,
    ),
    LLMModel(
        name="Phi-4 Mini 3.8B",
        family="Phi", parameters_b=3.8,
        min_vram_gb=3.0, rec_vram_gb=4.5,
        min_ram_gb=5.0,  rec_ram_gb=7.0,
        use_cases=["chat", "reasoning", "code"],
        description="Microsoft's compact successor to Phi-3.5 Mini - sharper reasoning, same footprint.",
        ollama_tag="phi4-mini", context_length=128000, released_year=2025,
    ),
    LLMModel(
        name="Qwen3 4B",
        family="Qwen", parameters_b=4.0,
        min_vram_gb=3.0, rec_vram_gb=4.5,
        min_ram_gb=5.0,  rec_ram_gb=7.0,
        use_cases=["chat", "reasoning", "code", "multilingual"],
        description="Hybrid thinking/non-thinking model - toggle deep reasoning on demand.",
        ollama_tag="qwen3:4b", context_length=32768, released_year=2025,
    ),
    LLMModel(
        name="Gemma 3 4B",
        family="Gemma", parameters_b=4.0,
        min_vram_gb=3.0, rec_vram_gb=4.5,
        min_ram_gb=5.0,  rec_ram_gb=7.0,
        use_cases=["chat", "vision", "summarisation"],
        description="Multimodal Gemma 3 - understands images as well as text at this size.",
        ollama_tag="gemma3:4b", context_length=128000, released_year=2025,
    ),

    # -- Mid-small models (7-9B) ----------------------------------------------
    LLMModel(
        name="Llama 3.1 8B",
        family="Llama", parameters_b=8.0,
        min_vram_gb=5.0, rec_vram_gb=8.0,
        min_ram_gb=8.0,  rec_ram_gb=12.0,
        use_cases=["chat", "reasoning", "code", "general"],
        description="Meta's popular workhorse. Excellent quality-to-size ratio.",
        ollama_tag="llama3.1:8b", context_length=131072, released_year=2024,
    ),
    LLMModel(
        name="Mistral 7B",
        family="Mistral", parameters_b=7.0,
        min_vram_gb=4.5, rec_vram_gb=7.0,
        min_ram_gb=7.0,  rec_ram_gb=10.0,
        use_cases=["chat", "reasoning", "code"],
        description="Mistral AI's flagship 7B - very fast and highly capable.",
        ollama_tag="mistral:7b", context_length=32768, released_year=2023,
    ),
    LLMModel(
        name="Qwen3 8B",
        family="Qwen", parameters_b=8.0,
        min_vram_gb=5.0, rec_vram_gb=8.0,
        min_ram_gb=8.0,  rec_ram_gb=12.0,
        use_cases=["chat", "code", "multilingual", "math"],
        description="Strong all-rounder with switchable reasoning mode and broad language support.",
        ollama_tag="qwen3:8b", context_length=32768, released_year=2025,
    ),
    LLMModel(
        name="Qwen2.5-Coder 7B",
        family="Qwen", parameters_b=7.0,
        min_vram_gb=4.5, rec_vram_gb=8.0,
        min_ram_gb=7.0,  rec_ram_gb=10.0,
        use_cases=["code", "code completion", "debugging"],
        description="State-of-the-art small coding model. Competes with much larger models.",
        ollama_tag="qwen2.5-coder:7b", context_length=131072, released_year=2024,
    ),
    LLMModel(
        name="DeepSeek-R1 Distill 7B",
        family="DeepSeek", parameters_b=7.0,
        min_vram_gb=4.5, rec_vram_gb=8.0,
        min_ram_gb=7.0,  rec_ram_gb=10.0,
        use_cases=["reasoning", "math", "code", "STEM"],
        description="Distilled version of DeepSeek-R1. Exceptional reasoning and math.",
        ollama_tag="deepseek-r1:7b", context_length=65536, released_year=2025,
    ),

    # -- Medium models (9-16B) ------------------------------------------------
    LLMModel(
        name="Gemma 3 12B",
        family="Gemma", parameters_b=12.0,
        min_vram_gb=7.5, rec_vram_gb=14.0,
        min_ram_gb=10.0, rec_ram_gb=16.0,
        use_cases=["chat", "vision", "reasoning", "code"],
        description="Multimodal Gemma 3 - a strong daily-driver size with a 128K context window.",
        ollama_tag="gemma3:12b", context_length=128000, released_year=2025,
    ),
    LLMModel(
        name="Mistral Nemo 12B",
        family="Mistral", parameters_b=12.0,
        min_vram_gb=7.5, rec_vram_gb=14.0,
        min_ram_gb=10.0, rec_ram_gb=16.0,
        use_cases=["chat", "reasoning", "code"],
        description="Mistral's larger model with extended context. Very versatile.",
        ollama_tag="mistral-nemo:12b", context_length=128000, released_year=2024,
    ),
    LLMModel(
        name="Phi-4 14B",
        family="Phi", parameters_b=14.0,
        min_vram_gb=8.5, rec_vram_gb=16.0,
        min_ram_gb=12.0, rec_ram_gb=20.0,
        use_cases=["reasoning", "math", "code", "STEM"],
        description="Microsoft Phi-4 - remarkable reasoning quality for 14B parameters.",
        ollama_tag="phi4:14b", context_length=16384, released_year=2024,
    ),
    LLMModel(
        name="Qwen3 14B",
        family="Qwen", parameters_b=14.0,
        min_vram_gb=8.5, rec_vram_gb=16.0,
        min_ram_gb=12.0, rec_ram_gb=20.0,
        use_cases=["chat", "code", "multilingual", "math"],
        description="Well-rounded 14B with switchable deep-reasoning mode.",
        ollama_tag="qwen3:14b", context_length=32768, released_year=2025,
    ),
    LLMModel(
        name="DeepSeek-R1 Distill 14B",
        family="DeepSeek", parameters_b=14.0,
        min_vram_gb=8.5, rec_vram_gb=16.0,
        min_ram_gb=12.0, rec_ram_gb=20.0,
        use_cases=["reasoning", "math", "code", "STEM"],
        description="Distilled R1 reasoning model. Excellent at complex problem solving.",
        ollama_tag="deepseek-r1:14b", context_length=65536, released_year=2025,
    ),

    # -- Medium-large models (20-34B) -----------------------------------------
    LLMModel(
        name="Mistral Small 3.1 24B",
        family="Mistral", parameters_b=24.0,
        min_vram_gb=14.0, rec_vram_gb=20.0,
        min_ram_gb=18.0,  rec_ram_gb=28.0,
        use_cases=["chat", "vision", "reasoning", "code"],
        description="Multimodal, low-latency Mistral model that rivals much larger models.",
        ollama_tag="mistral-small3.1:24b", context_length=128000, released_year=2025,
    ),
    LLMModel(
        name="Gemma 3 27B",
        family="Gemma", parameters_b=27.0,
        min_vram_gb=16.0, rec_vram_gb=24.0,
        min_ram_gb=20.0,  rec_ram_gb=32.0,
        use_cases=["chat", "vision", "reasoning", "code"],
        description="Google's flagship single-GPU model - one of the best open-weight models at this scale.",
        ollama_tag="gemma3:27b", context_length=128000, released_year=2025,
    ),
    LLMModel(
        name="Qwen3 32B",
        family="Qwen", parameters_b=32.0,
        min_vram_gb=19.0, rec_vram_gb=24.0,
        min_ram_gb=24.0,  rec_ram_gb=40.0,
        use_cases=["chat", "code", "multilingual", "math"],
        description="Qwen3's dense flagship - competitive with much larger 2024-era models.",
        ollama_tag="qwen3:32b", context_length=131072, released_year=2025,
    ),
    LLMModel(
        name="Qwen3 30B-A3B",
        family="Qwen", parameters_b=30.5,
        min_vram_gb=18.0, rec_vram_gb=24.0,
        min_ram_gb=20.0,  rec_ram_gb=32.0,
        use_cases=["chat", "reasoning", "agentic", "multilingual"],
        description="MoE model, only 3B active params per token - near-8B speed with 32B-class quality.",
        ollama_tag="qwen3:30b-a3b", context_length=131072, released_year=2025,
    ),
    LLMModel(
        name="Qwen3-Coder 30B-A3B",
        family="Qwen", parameters_b=30.5,
        min_vram_gb=18.0, rec_vram_gb=24.0,
        min_ram_gb=20.0,  rec_ram_gb=32.0,
        use_cases=["code", "agentic coding", "debugging"],
        description="MoE coding specialist, 3B active params - fast agentic/tool-use coding.",
        ollama_tag="qwen3-coder:30b-a3b", context_length=131072, released_year=2025,
    ),
    LLMModel(
        name="gpt-oss 20B",
        family="GPT-OSS", parameters_b=20.9,
        min_vram_gb=12.0, rec_vram_gb=16.0,
        min_ram_gb=14.0,  rec_ram_gb=20.0,
        use_cases=["chat", "reasoning", "code", "agentic"],
        description="OpenAI's open-weight MoE model (3.6B active) - tuned for tool use and reasoning traces.",
        ollama_tag="gpt-oss:20b", context_length=131072, released_year=2025,
    ),
    LLMModel(
        name="DeepSeek-R1 Distill 32B",
        family="DeepSeek", parameters_b=32.0,
        min_vram_gb=19.0, rec_vram_gb=24.0,
        min_ram_gb=24.0,  rec_ram_gb=40.0,
        use_cases=["reasoning", "math", "code", "STEM"],
        description="Powerful reasoning model. Near frontier-level on math and science.",
        ollama_tag="deepseek-r1:32b", context_length=65536, released_year=2025,
    ),

    # -- Large models (70-120B) ------------------------------------------------
    LLMModel(
        name="Llama 3.3 70B",
        family="Llama", parameters_b=70.0,
        min_vram_gb=40.0, rec_vram_gb=48.0,
        min_ram_gb=44.0,  rec_ram_gb=64.0,
        use_cases=["chat", "reasoning", "code", "general"],
        description="Meta's refreshed 70B - matches the old 405B model on many benchmarks.",
        ollama_tag="llama3.3", context_length=131072, released_year=2024,
    ),
    LLMModel(
        name="DeepSeek-R1 Distill 70B",
        family="DeepSeek", parameters_b=70.0,
        min_vram_gb=40.0, rec_vram_gb=48.0,
        min_ram_gb=44.0,  rec_ram_gb=64.0,
        use_cases=["reasoning", "math", "code", "STEM"],
        description="Frontier-level reasoning. Competes with o1-mini on STEM benchmarks.",
        ollama_tag="deepseek-r1:70b", context_length=65536, released_year=2025,
    ),
    LLMModel(
        name="Mixtral 8x7B",
        family="Mixtral", parameters_b=46.7,
        min_vram_gb=26.0, rec_vram_gb=48.0,
        min_ram_gb=30.0,  rec_ram_gb=48.0,
        use_cases=["chat", "reasoning", "code", "multilingual"],
        description="MoE architecture - 8 experts, 2 active. Fast and very capable.",
        ollama_tag="mixtral:8x7b", context_length=32768, released_year=2024,
    ),
    LLMModel(
        name="Llama 4 Scout",
        family="Llama", parameters_b=109.0,
        min_vram_gb=61.0, rec_vram_gb=80.0,
        min_ram_gb=66.0,  rec_ram_gb=90.0,
        use_cases=["chat", "vision", "long-context", "general"],
        description="MoE model (17B active), natively multimodal with an industry-leading 10M token context.",
        ollama_tag="llama4:scout", context_length=10000000, released_year=2025,
    ),
    LLMModel(
        name="gpt-oss 120B",
        family="GPT-OSS", parameters_b=116.8,
        min_vram_gb=66.0, rec_vram_gb=92.0,
        min_ram_gb=70.0,  rec_ram_gb=100.0,
        use_cases=["chat", "reasoning", "code", "agentic"],
        description="OpenAI's larger open-weight MoE (5.1B active) - near frontier reasoning quality.",
        ollama_tag="gpt-oss:120b", context_length=131072, released_year=2025,
    ),

    # -- Very large models (200B+) ----------------------------------------------
    LLMModel(
        name="Qwen3 235B-A22B",
        family="Qwen", parameters_b=235.0,
        min_vram_gb=132.0, rec_vram_gb=176.0,
        min_ram_gb=140.0,  rec_ram_gb=200.0,
        use_cases=["chat", "reasoning", "code", "research"],
        description="Qwen3's flagship MoE (22B active) - matches or beats many closed frontier models.",
        ollama_tag="qwen3:235b-a22b", context_length=131072, released_year=2025,
    ),
    LLMModel(
        name="Llama 4 Maverick",
        family="Llama", parameters_b=400.0,
        min_vram_gb=227.0, rec_vram_gb=316.0,
        min_ram_gb=236.0,  rec_ram_gb=395.0,
        use_cases=["chat", "vision", "reasoning", "research"],
        description="MoE model (17B active), Meta's natively multimodal flagship - needs server-grade hardware.",
        ollama_tag="llama4:maverick", context_length=1000000, released_year=2025,
    ),
    LLMModel(
        name="Llama 3.1 405B",
        family="Llama", parameters_b=405.0,
        min_vram_gb=230.0, rec_vram_gb=320.0,
        min_ram_gb=240.0,  rec_ram_gb=400.0,
        use_cases=["chat", "reasoning", "code", "research"],
        description="Meta's largest dense open model. Requires server-grade hardware.",
        ollama_tag="llama3.1:405b", context_length=131072, released_year=2024,
    ),
    LLMModel(
        name="DeepSeek-R1 671B",
        family="DeepSeek", parameters_b=671.0,
        min_vram_gb=380.0, rec_vram_gb=530.0,
        min_ram_gb=396.0,  rec_ram_gb=660.0,
        use_cases=["reasoning", "math", "code", "research"],
        description="The full DeepSeek-R1 MoE (37B active) - frontier-class reasoning, datacenter-scale hardware only.",
        ollama_tag="deepseek-r1:671b", context_length=131072, released_year=2025,
    ),
]
