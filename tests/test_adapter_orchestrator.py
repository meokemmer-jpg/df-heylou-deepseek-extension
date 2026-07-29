from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from deepseek_extension import DeepSeekExtension, LocalHeyLouBackend


def test_deepseek_extension_discriminates_adversarial_search_input(tmp_path, monkeypatch):
    monkeypatch.setenv("DF_HEYLOU_DEEPSEEK_DATA_DIR", str(tmp_path / "backend"))
    backend = LocalHeyLouBackend()
    extension = DeepSeekExtension(sandbox_mode=True, backend=backend)

    mission_input = {
        "name": "search_hotels",
        "args": {
            "location": "Hildesheim",
            "dates": {"check_in": "2026-08-14", "check_out": "2026-08-16"},
            "guests": 2,
        },
    }
    adversarial_input = {
        "name": "search_hotels",
        "args": {
            "location": "Atlantis Impossible Territory",
            "dates": {"check_in": "2026-08-14", "check_out": "2026-08-16"},
            "guests": 2,
        },
    }

    mission = extension.handle_function_call(mission_input)
    adversarial = extension.handle_function_call(adversarial_input)

    assert mission.success is True
    assert adversarial.success is True
    assert backend.catalog_path.exists()
    assert mission.provenance.backend_used == backend.BACKEND_ID
    assert adversarial.provenance.backend_used == backend.BACKEND_ID

    assert mission.data["result_count"] > adversarial.data["result_count"]
    assert mission.data["hotels"] != adversarial.data["hotels"]
    assert mission.provenance.response_hash != adversarial.provenance.response_hash
    assert mission.data["discriminator"] != adversarial.data["discriminator"]
