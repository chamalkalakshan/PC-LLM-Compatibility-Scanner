from dataclasses import dataclass
from enum import Enum
from typing import List

from .hardware import SystemInfo
from .llm_database import LLM_DATABASE, LLMModel


class RunTier(Enum):
    RUNS  = "RUNS"
    SLOW  = "SLOW"
    NO_GO = "NO-GO"


TIER_EMOJI = {RunTier.RUNS: "✅", RunTier.SLOW: "🐌", RunTier.NO_GO: "❌"}
TIER_LABEL = {
    RunTier.RUNS:  "Runs on your hardware",
    RunTier.SLOW:  "Slow – CPU only",
    RunTier.NO_GO: "Insufficient hardware",
}


@dataclass
class Recommendation:
    model: LLMModel
    tier: RunTier
    run_mode: str
    notes: List[str]
    ollama_cmd: str


def _score_model(model: LLMModel, hw: SystemInfo) -> Recommendation:
    total_vram = sum(g.vram_gb for g in hw.gpus)
    total_ram  = hw.ram.total_gb

    if total_vram >= model.min_vram_gb:
        return Recommendation(
            model=model, tier=RunTier.RUNS, run_mode="GPU",
            notes=[f"Fits in {total_vram:.0f} GB VRAM"],
            ollama_cmd=f"ollama run {model.ollama_tag}",
        )
    elif total_ram >= model.min_ram_gb:
        return Recommendation(
            model=model, tier=RunTier.SLOW, run_mode="CPU",
            notes=["CPU inference -- slow but usable"],
            ollama_cmd=f"ollama run {model.ollama_tag}",
        )
    else:
        return Recommendation(
            model=model, tier=RunTier.NO_GO, run_mode="--",
            notes=[f"Need {model.min_ram_gb:.0f} GB RAM minimum"],
            ollama_cmd=f"ollama run {model.ollama_tag}",
        )


def get_recommendations(hw: SystemInfo) -> List[Recommendation]:
    recs = [_score_model(m, hw) for m in LLM_DATABASE]
    tier_order = [RunTier.RUNS, RunTier.SLOW, RunTier.NO_GO]
    recs.sort(key=lambda r: (tier_order.index(r.tier), -r.model.parameters_b))
    return recs


def get_summary_stats(recs):
    counts = {t: 0 for t in RunTier}
    for r in recs:
        counts[r.tier] += 1
    return {"total": len(recs), "by_tier": {t.value: counts[t] for t in RunTier}}
