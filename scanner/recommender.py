from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from .hardware import SystemInfo
from .llm_database import LLM_DATABASE, LLMModel


class RunTier(Enum):
    EXCELLENT = "EXCELLENT"
    GOOD      = "GOOD"
    POSSIBLE  = "POSSIBLE"
    SLOW      = "SLOW"
    NO_GO     = "NO-GO"


TIER_EMOJI = {
    RunTier.EXCELLENT: "🚀",
    RunTier.GOOD:      "✅",
    RunTier.POSSIBLE:  "⚡",
    RunTier.SLOW:      "🐌",
    RunTier.NO_GO:     "❌",
}

TIER_LABEL = {
    RunTier.EXCELLENT: "Excellent – GPU, fast",
    RunTier.GOOD:      "Good – GPU fits",
    RunTier.POSSIBLE:  "Possible – partial offload / CPU",
    RunTier.SLOW:      "Slow – CPU only",
    RunTier.NO_GO:     "Insufficient hardware",
}


@dataclass
class Recommendation:
    model: LLMModel
    tier: RunTier
    run_mode: str
    notes: List[str]
    ollama_cmd: str


def _total_vram(hw: SystemInfo) -> float:
    return sum(g.vram_gb for g in hw.gpus)


def _score_model(model: LLMModel, hw: SystemInfo) -> Recommendation:
    total_vram = _total_vram(hw)
    total_ram  = hw.ram.total_gb
    notes: List[str] = []

    # GPU path
    if total_vram >= model.rec_vram_gb:
        tier     = RunTier.EXCELLENT
        run_mode = "GPU" if len(hw.gpus) <= 1 else "Multi-GPU"
        notes.append(f"Fits comfortably in {total_vram:.0f} GB VRAM")

    elif total_vram >= model.min_vram_gb:
        tier     = RunTier.GOOD
        run_mode = "GPU"
        notes.append(f"Fits in {total_vram:.0f} GB VRAM (tight – close smaller apps)")

    # Partial GPU offload
    elif total_vram > 0 and total_ram >= model.min_ram_gb:
        tier     = RunTier.POSSIBLE
        run_mode = "Partial GPU"
        offload_pct = min(int((total_vram / model.min_vram_gb) * 100), 99)
        notes.append(f"~{offload_pct}% of layers can offload to GPU VRAM")
        notes.append("Remaining layers run on CPU/RAM – slower than full GPU")

    # CPU-only
    elif total_ram >= model.rec_ram_gb:
        tier     = RunTier.POSSIBLE
        run_mode = "CPU"
        notes.append(f"CPU inference with {total_ram:.0f} GB RAM")
        notes.append("Expect 2–8 tokens/sec depending on CPU")

    elif total_ram >= model.min_ram_gb:
        tier     = RunTier.SLOW
        run_mode = "CPU"
        notes.append(f"Fits in RAM ({total_ram:.0f} GB) but very tight")
        notes.append("Expect < 2 tokens/sec – usable but sluggish")

    else:
        tier     = RunTier.NO_GO
        run_mode = "—"
        shortage = model.min_ram_gb - total_ram
        notes.append(f"Need ~{model.min_ram_gb:.0f} GB RAM; you have {total_ram:.0f} GB")
        notes.append(f"Upgrade RAM by at least {shortage:.0f} GB to run CPU inference")

    if tier != RunTier.NO_GO:
        if hw.storage.free_gb < model.min_vram_gb * 2.5:
            notes.append(
                f"⚠ Low free disk space ({hw.storage.free_gb:.0f} GB) – "
                f"download may need {model.min_vram_gb * 2:.0f}+ GB"
            )
        if hw.cpu.is_apple_silicon:
            notes.append("Apple Silicon: unified memory counts as both RAM and VRAM")

    return Recommendation(
        model=model,
        tier=tier,
        run_mode=run_mode,
        notes=notes,
        ollama_cmd=f"ollama run {model.ollama_tag}",
    )


def get_recommendations(hw: SystemInfo) -> List[Recommendation]:
    recs = [_score_model(m, hw) for m in LLM_DATABASE]
    tier_order = [RunTier.EXCELLENT, RunTier.GOOD, RunTier.POSSIBLE, RunTier.SLOW, RunTier.NO_GO]
    recs.sort(key=lambda r: (tier_order.index(r.tier), -r.model.parameters_b))
    return recs


def get_summary_stats(recs: List[Recommendation]) -> dict:
    counts = {t: 0 for t in RunTier}
    for r in recs:
        counts[r.tier] += 1
    return {
        "total": len(recs),
        "runnable": sum(counts[t] for t in [RunTier.EXCELLENT, RunTier.GOOD, RunTier.POSSIBLE, RunTier.SLOW]),
        "excellent_good": counts[RunTier.EXCELLENT] + counts[RunTier.GOOD],
        "by_tier": {t.value: counts[t] for t in RunTier},
    }
