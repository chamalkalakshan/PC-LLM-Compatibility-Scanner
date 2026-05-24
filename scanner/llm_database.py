from dataclasses import dataclass, field
from typing import List


@dataclass
class LLMModel:
    name: str
    family: str
    parameters_b: float
    min_vram_gb: float
    rec_vram_gb: float
    min_ram_gb: float
    rec_ram_gb: float
    use_cases: List[str]
    description: str
    ollama_tag: str
    context_length: int
    released_year: int


LLM_DATABASE: List[LLMModel] = [

    # ── Tiny models (< 2B) ─────────────────────────────────────────────────
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
        name="Llama 3.2 3B",
        family="Llama", parameters_b=3.0,
        min_vram_gb=2.5, rec_vram_gb=4.0,
        min_ram_gb=4.0,  rec_ram_gb=6.0,
        use_cases=["chat", "summarisation", "mobile"],
        description="Small but capable Llama 3.2 model. Punches above its size.",
        ollama_tag="llama3.2:3b", context_length=131072, released_year=2024,
    ),
    LLMModel(
        name="Phi-3.5 Mini 3.8B",
        family="Phi", parameters_b=3.8,
        min_vram_gb=3.0, rec_vram_gb=4.5,
        min_ram_gb=5.0,  rec_ram_gb=7.0,
        use_cases=["chat", "reasoning", "code"],
        description="Microsoft's compact powerhouse -- exceptional reasoning for its size.",
        ollama_tag="phi3.5", context_length=128000, released_year=2024,
    ),
    LLMModel(
        name="Gemma 2 2B",
        family="Gemma", parameters_b=2.0,
        min_vram_gb=2.0, rec_vram_gb=3.0,
        min_ram_gb=3.5,  rec_ram_gb=5.0,
        use_cases=["chat", "summarisation"],
        description="Google's efficient small model with strong benchmark scores.",
        ollama_tag="gemma2:2b", context_length=8192, released_year=2024,
    ),
    LLMModel(
        name="Qwen2.5 1.5B",
        family="Qwen", parameters_b=1.5,
        min_vram_gb=1.5, rec_vram_gb=2.5,
        min_ram_gb=3.0,  rec_ram_gb=4.0,
        use_cases=["chat", "multilingual"],
        description="Alibaba's multilingual mini model.",
        ollama_tag="qwen2.5:1.5b", context_length=32768, released_year=2024,
    ),
    LLMModel(
        name="Qwen2.5 3B",
        family="Qwen", parameters_b=3.0,
        min_vram_gb=2.5, rec_vram_gb=4.0,
        min_ram_gb=4.0,  rec_ram_gb=6.0,
        use_cases=["chat", "code", "multilingual"],
        description="Compact and surprisingly capable multilingual model.",
        ollama_tag="qwen2.5:3b", context_length=32768, released_year=2024,
    ),

    # ── Small models (3-9B) ────────────────────────────────────────────────
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
        description="Mistral AI's flagship 7B -- very fast and highly capable.",
        ollama_tag="mistral:7b", context_length=32768, released_year=2023,
    ),
    LLMModel(
        name="Gemma 2 9B",
        family="Gemma", parameters_b=9.0,
        min_vram_gb=5.5, rec_vram_gb=10.0,
        min_ram_gb=9.0,  rec_ram_gb=14.0,
        use_cases=["chat", "reasoning", "code"],
        description="Google's 9B model -- top-tier quality for its parameter count.",
        ollama_tag="gemma2:9b", context_length=8192, released_year=2024,
    ),
    LLMModel(
        name="Qwen2.5 7B",
        family="Qwen", parameters_b=7.0,
        min_vram_gb=4.5, rec_vram_gb=8.0,
        min_ram_gb=7.0,  rec_ram_gb=10.0,
        use_cases=["chat", "code", "multilingual", "math"],
        description="Strong at coding and math. Excellent multilingual support.",
        ollama_tag="qwen2.5:7b", context_length=131072, released_year=2024,
    ),
    LLMModel(
        name="CodeLlama 7B",
        family="CodeLlama", parameters_b=7.0,
        min_vram_gb=4.5, rec_vram_gb=7.0,
        min_ram_gb=7.0,  rec_ram_gb=10.0,
        use_cases=["code", "code completion", "debugging"],
        description="Meta's code-specialised model. Great for programming tasks.",
        ollama_tag="codellama:7b", context_length=16384, released_year=2023,
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
    LLMModel(
        name="DeepSeek-R1 Distill 14B",
        family="DeepSeek", parameters_b=14.0,
        min_vram_gb=8.5, rec_vram_gb=16.0,
        min_ram_gb=12.0, rec_ram_gb=20.0,
        use_cases=["reasoning", "math", "code", "STEM"],
        description="Distilled R1 reasoning model. Excellent at complex problem solving.",
        ollama_tag="deepseek-r1:14b", context_length=65536, released_year=2025,
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
    # ── Medium models (9-30B) ──────────────────────────────────────────────
    LLMModel(
        name="Phi-4 14B",
        family="Phi", parameters_b=14.0,
        min_vram_gb=8.5, rec_vram_gb=16.0,
        min_ram_gb=12.0, rec_ram_gb=20.0,
        use_cases=["reasoning", "math", "code", "STEM"],
        description="Microsoft Phi-4 -- remarkable reasoning quality for 14B parameters.",
        ollama_tag="phi4:14b", context_length=16384, released_year=2024,
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
        name="Qwen2.5 14B",
        family="Qwen", parameters_b=14.0,
        min_vram_gb=8.5, rec_vram_gb=16.0,
        min_ram_gb=12.0, rec_ram_gb=20.0,
        use_cases=["chat", "code", "multilingual", "math"],
        description="Well-rounded 14B with great coding and multilingual abilities.",
        ollama_tag="qwen2.5:14b", context_length=131072, released_year=2024,
    ),
    LLMModel(
        name="Gemma 2 27B",
        family="Gemma", parameters_b=27.0,
        min_vram_gb=16.0, rec_vram_gb=24.0,
        min_ram_gb=20.0,  rec_ram_gb=32.0,
        use_cases=["chat", "reasoning", "code"],
        description="Google's 27B model -- one of the best open-weight models at this scale.",
        ollama_tag="gemma2:27b", context_length=8192, released_year=2024,
    ),
    LLMModel(
        name="Qwen2.5 32B",
        family="Qwen", parameters_b=32.0,
        min_vram_gb=19.0, rec_vram_gb=24.0,
        min_ram_gb=24.0,  rec_ram_gb=40.0,
        use_cases=["chat", "code", "multilingual", "math"],
        description="Qwen's strong 32B -- competitive with GPT-4 on many benchmarks.",
        ollama_tag="qwen2.5:32b", context_length=131072, released_year=2024,
    ),
    LLMModel(
        name="CodeLlama 34B",
        family="CodeLlama", parameters_b=34.0,
        min_vram_gb=20.0, rec_vram_gb=24.0,
        min_ram_gb=24.0,  rec_ram_gb=40.0,
        use_cases=["code", "code completion", "debugging"],
        description="Meta's large code model. Excellent for complex programming tasks.",
        ollama_tag="codellama:34b", context_length=16384, released_year=2023,
    ),
]
