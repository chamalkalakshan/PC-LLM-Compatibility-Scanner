import pytest

from scanner.hardware import CPUInfo, GPUInfo, RAMInfo, StorageInfo, SystemInfo
from scanner.llm_database import LLMModel
from scanner.recommender import RunTier, get_recommendations, get_summary_stats, _score_model


MODEL = LLMModel(
    name="Test Model",
    family="Test", parameters_b=10.0,
    min_vram_gb=8.0, rec_vram_gb=16.0,
    min_ram_gb=12.0, rec_ram_gb=24.0,
    use_cases=["chat"],
    description="A model used only for testing tier boundaries.",
    ollama_tag="test:10b", context_length=8192, released_year=2025,
)


def make_hw(vram_gb=0.0, ram_total_gb=64.0, ram_available_gb=32.0,
            free_disk_gb=500.0, is_apple_silicon=False):
    gpus = [GPUInfo(name="Test GPU", vram_gb=vram_gb, vendor="NVIDIA")] if vram_gb > 0 else []
    return SystemInfo(
        cpu=CPUInfo(
            name="Test CPU", physical_cores=8, logical_cores=16,
            max_freq_ghz=4.0, architecture="x86_64", is_apple_silicon=is_apple_silicon,
        ),
        ram=RAMInfo(total_gb=ram_total_gb, available_gb=ram_available_gb),
        gpus=gpus,
        storage=StorageInfo(total_gb=1000.0, free_gb=free_disk_gb, drive="C:\\"),
        os_name="Windows", os_version="10",
    )


def test_excellent_at_exact_rec_vram():
    hw = make_hw(vram_gb=MODEL.rec_vram_gb)
    rec = _score_model(MODEL, hw)
    assert rec.tier == RunTier.EXCELLENT
    assert rec.run_mode == "GPU"


def test_excellent_above_rec_vram():
    hw = make_hw(vram_gb=MODEL.rec_vram_gb + 8)
    rec = _score_model(MODEL, hw)
    assert rec.tier == RunTier.EXCELLENT


def test_good_at_exact_min_vram():
    hw = make_hw(vram_gb=MODEL.min_vram_gb)
    rec = _score_model(MODEL, hw)
    assert rec.tier == RunTier.GOOD
    assert rec.run_mode == "GPU"


def test_good_just_below_rec_vram():
    hw = make_hw(vram_gb=MODEL.rec_vram_gb - 0.1)
    rec = _score_model(MODEL, hw)
    assert rec.tier == RunTier.GOOD


def test_partial_gpu_when_vram_below_min_but_ram_sufficient():
    hw = make_hw(vram_gb=MODEL.min_vram_gb - 2, ram_total_gb=64.0)
    rec = _score_model(MODEL, hw)
    assert rec.tier == RunTier.POSSIBLE
    assert rec.run_mode == "Partial GPU"


def test_partial_gpu_offload_note_present_below_min_vram():
    hw = make_hw(vram_gb=MODEL.min_vram_gb - 0.01, ram_total_gb=64.0)
    rec = _score_model(MODEL, hw)
    assert any("% of layers" in n for n in rec.notes)


def test_possible_cpu_only_at_rec_ram_with_no_gpu():
    hw = make_hw(vram_gb=0.0, ram_total_gb=MODEL.rec_ram_gb)
    rec = _score_model(MODEL, hw)
    assert rec.tier == RunTier.POSSIBLE
    assert rec.run_mode == "CPU"


def test_slow_when_ram_between_min_and_rec_with_no_gpu():
    hw = make_hw(vram_gb=0.0, ram_total_gb=MODEL.min_ram_gb)
    rec = _score_model(MODEL, hw)
    assert rec.tier == RunTier.SLOW
    assert rec.run_mode == "CPU"


def test_no_go_when_ram_below_min_with_no_gpu():
    hw = make_hw(vram_gb=0.0, ram_total_gb=MODEL.min_ram_gb - 1)
    rec = _score_model(MODEL, hw)
    assert rec.tier == RunTier.NO_GO
    assert rec.run_mode == "—"


def test_no_go_has_no_disk_or_apple_notes():
    hw = make_hw(vram_gb=0.0, ram_total_gb=1.0, free_disk_gb=0.5, is_apple_silicon=True)
    rec = _score_model(MODEL, hw)
    assert rec.tier == RunTier.NO_GO
    assert not any("disk space" in n.lower() for n in rec.notes)
    assert not any("Apple Silicon" in n for n in rec.notes)


def test_low_disk_space_warning_appended_for_runnable_tier():
    hw = make_hw(vram_gb=MODEL.rec_vram_gb, free_disk_gb=1.0)
    rec = _score_model(MODEL, hw)
    assert rec.tier != RunTier.NO_GO
    assert any("Low free disk space" in n for n in rec.notes)


def test_apple_silicon_note_appended_for_runnable_tier():
    hw = make_hw(vram_gb=MODEL.rec_vram_gb, is_apple_silicon=True)
    rec = _score_model(MODEL, hw)
    assert any("unified memory" in n for n in rec.notes)


def test_ollama_cmd_uses_model_tag():
    hw = make_hw(vram_gb=MODEL.rec_vram_gb)
    rec = _score_model(MODEL, hw)
    assert rec.ollama_cmd == f"ollama run {MODEL.ollama_tag}"


def test_get_recommendations_sorts_by_tier_then_size_desc():
    hw = make_hw(vram_gb=0.0, ram_total_gb=8.0)
    recs = get_recommendations(hw)
    tier_order = [RunTier.EXCELLENT, RunTier.GOOD, RunTier.POSSIBLE, RunTier.SLOW, RunTier.NO_GO]
    tier_indices = [tier_order.index(r.tier) for r in recs]
    assert tier_indices == sorted(tier_indices)
    # within a tier, larger models should sort first
    for i in range(len(recs) - 1):
        if recs[i].tier == recs[i + 1].tier:
            assert recs[i].model.parameters_b >= recs[i + 1].model.parameters_b


def test_get_summary_stats_counts_match_total():
    hw = make_hw(vram_gb=12.0, ram_total_gb=32.0)
    recs = get_recommendations(hw)
    stats = get_summary_stats(recs)
    assert stats["total"] == len(recs)
    assert sum(stats["by_tier"].values()) == stats["total"]
    assert stats["runnable"] == stats["total"] - stats["by_tier"][RunTier.NO_GO.value]
    assert stats["excellent_good"] == (
        stats["by_tier"][RunTier.EXCELLENT.value] + stats["by_tier"][RunTier.GOOD.value]
    )
