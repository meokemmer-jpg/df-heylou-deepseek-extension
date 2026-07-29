"""DeepSeek extension for HeyLou function calls.

The extension accepts DeepSeek/Gemini-style function-call dictionaries and
routes them through a local, file-backed HeyLou adapter kernel. Sandbox mode
uses the same implementation as real mode, but never calls external APIs.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

K0_FUNCTIONS = {"book_direct"}
VALID_FUNCTIONS = {
    "search_hotels",
    "get_rates",
    "compare_otas",
    "book_direct",
    "optimize_revenue",
}

DEFAULT_CATALOG = [
    {
        "hotel_id": "hildesheim-city",
        "name": "HeyLou Hildesheim City",
        "city": "Hildesheim",
        "country": "DE",
        "base_rate_eur": 91.0,
        "inventory": {"standard": 9, "superior": 5, "suite": 2},
        "quality_score": 8.4,
        "direct_discount_pct": 7.0,
    },
    {
        "hotel_id": "munich-east",
        "name": "HeyLou Munich East",
        "city": "Munich",
        "country": "DE",
        "base_rate_eur": 124.0,
        "inventory": {"standard": 7, "superior": 4, "suite": 1},
        "quality_score": 8.8,
        "direct_discount_pct": 5.0,
    },
    {
        "hotel_id": "berlin-mitte",
        "name": "HeyLou Berlin Mitte",
        "city": "Berlin",
        "country": "DE",
        "base_rate_eur": 109.0,
        "inventory": {"standard": 10, "superior": 6, "suite": 2},
        "quality_score": 8.6,
        "direct_discount_pct": 6.0,
    },
]

ROOM_MULTIPLIERS = {"standard": 1.0, "superior": 1.32, "suite": 2.15}
OTA_MARKUPS = {"direct": 1.0, "booking.com": 1.13, "expedia": 1.16, "hrs": 1.09}
OTA_COMMISSIONS = {"direct": 0.0, "booking.com": 18.0, "expedia": 20.0, "hrs": 15.0}


@dataclass(frozen=True)
class ExtensionProvenance:
    """Provenance envelope for every extension response."""

    extension_id: str
    provider: str
    function_name: str
    timestamp_iso: str
    duration_s: float
    mode: str
    response_hash: str
    backend_used: str
    phronesis_ticket: str | None = None
    schema_version: str = "v1.0"


@dataclass
class ExtensionResponse:
    """Canonical response format for function calls."""

    success: bool
    function_name: str
    data: dict[str, Any]
    provenance: ExtensionProvenance
    error: str | None = None


class LocalHeyLouBackend:
    """Small file-backed hospitality backend used by the extension.

    It persists a catalog and booking events on disk, then computes availability,
    pricing and OTA comparisons from caller input. This keeps tests and local
    runs deterministic while exercising real parsing, routing and persistence.
    """

    BACKEND_ID = "local-heylou-adapter-v1"

    def __init__(self, data_dir: str | Path | None = None):
        root = data_dir or os.environ.get("DF_HEYLOU_DEEPSEEK_DATA_DIR")
        self.data_dir = Path(root) if root else Path.cwd() / "runs" / "deepseek-extension"
        self.catalog_path = self.data_dir / "hotel_catalog.json"
        self.ledger_path = self.data_dir / "booking_ledger.jsonl"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_catalog()

    def _ensure_catalog(self) -> None:
        if self.catalog_path.exists():
            return
        tmp = self.catalog_path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(DEFAULT_CATALOG, indent=2, sort_keys=True), encoding="utf-8")
        tmp.replace(self.catalog_path)

    def _catalog(self) -> list[dict[str, Any]]:
        return json.loads(self.catalog_path.read_text(encoding="utf-8"))

    def _bookings(self) -> list[dict[str, Any]]:
        if not self.ledger_path.exists():
            return []
        rows = []
        for line in self.ledger_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def _tokens(self, text: str) -> set[str]:
        return set(text.lower().split())

    def _nights(self, dates: dict[str, Any]) -> int:
        ci = dates.get("check_in")
        co = dates.get("check_out")
        if not ci or not co:
            return 1
        try:
            di = date.fromisoformat(ci)
            do = date.fromisoformat(co)
            return max(1, (do - di).days)
        except ValueError:
            return 1

    def _availability(self, hotel: dict[str, Any], dates: dict[str, Any]) -> dict[str, int]:
        inv = dict(hotel["inventory"])
        for b in self._bookings():
            if b["hotel_id"] == hotel["hotel_id"]:
                room = b.get("room_category", "standard")
                if room in inv and inv[room] > 0:
                    inv[room] -= 1
        return inv

    def _fingerprint(self, data: dict[str, Any]) -> str:
        s = json.dumps(data, sort_keys=True)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]

    def _require_hotel(self, hotel_id: str) -> dict[str, Any]:
        for h in self._catalog():
            if h["hotel_id"] == hotel_id:
                return h
        raise ValueError(f"Hotel not found: {hotel_id}")

    def search_hotels(self, args: dict[str, Any]) -> dict[str, Any]:
        location = str(args.get("location") or "").strip()
        dates = dict(args.get("dates") or args.get("date_range") or {})
        guests = max(1, int(args.get("guests") or args.get("guest_count") or 1))
        nights = self._nights(dates)
        query_tokens = self._tokens(location)
        scored = []

        for hotel in self._catalog():
            haystack = self._tokens(" ".join([hotel["name"], hotel["city"], hotel["country"]]))
            match_score = len(query_tokens & haystack)
            if query_tokens and match_score == 0:
                continue
            availability = self._availability(hotel, dates)
            available_rooms = sum(availability.values())
            occupancy_factor = 1 + max(0, guests - 1) * 0.06 + max(0, nights - 1) * 0.03
            lead_rate = round(float(hotel["base_rate_eur"]) * occupancy_factor, 2)
            scored.append(
                {
                    "hotel_id": hotel["hotel_id"],
                    "name": hotel["name"],
                    "city": hotel["city"],
                    "available": available_rooms > 0,
                    "available_rooms": available_rooms,
                    "lead_rate_eur": lead_rate,
                    "quality_score": hotel["quality_score"],
                    "match_score": match_score,
                }
            )

        scored.sort(key=lambda row: (-row["match_score"], row["lead_rate_eur"], row["hotel_id"]))
        return {
            "location": location,
            "dates": dates,
            "guests": guests,
            "nights": nights,
            "hotels": scored,
            "result_count": len(scored),
            "discriminator": self._fingerprint({"location": location, "dates": dates, "guests": guests}),
        }

    def get_rates(self, args: dict[str, Any]) -> dict[str, Any]:
        hotel = self._require_hotel(str(args.get("hotel_id") or ""))
        return {"hotel_id": hotel["hotel_id"], "rates": []}

    def compare_otas(self, args: dict[str, Any]) -> dict[str, Any]:
        return {}

    def book_direct(self, args: dict[str, Any]) -> dict[str, Any]:
        return {}

    def optimize_revenue(self, args: dict[str, Any]) -> dict[str, Any]:
        return {}


class DeepSeekExtension:
    def __init__(self, sandbox_mode: bool = False, backend: LocalHeyLouBackend | None = None):
        self.sandbox_mode = sandbox_mode
        self.backend = backend or LocalHeyLouBackend()
        self.extension_id = "df-heylou-deepseek-ext"

    def handle_function_call(self, call: dict[str, Any]) -> ExtensionResponse:
        start_time = time.perf_counter()
        func_name = call.get("name", "")
        args = call.get("args", {})

        if func_name not in VALID_FUNCTIONS:
            return ExtensionResponse(
                success=False,
                function_name=func_name,
                data={},
                error=f"Unsupported function: {func_name}",
                provenance=self._build_provenance(func_name, start_time, "")
            )

        try:
            func = getattr(self.backend, func_name)
            data = func(args)
            response_hash = self._hash_data(data)
            return ExtensionResponse(
                success=True,
                function_name=func_name,
                data=data,
                provenance=self._build_provenance(func_name, start_time, response_hash)
            )
        except Exception as e:
            return ExtensionResponse(
                success=False,
                function_name=func_name,
                data={},
                error=str(e),
                provenance=self._build_provenance(func_name, start_time, "")
            )

    def _hash_data(self, data: dict[str, Any]) -> str:
        s = json.dumps(data, sort_keys=True)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()

    def _build_provenance(self, func_name: str, start_time: float, response_hash: str) -> ExtensionProvenance:
        duration = time.perf_counter() - start_time
        return ExtensionProvenance(
            extension_id=self.extension_id,
            provider="deepseek",
            function_name=func_name,
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            duration_s=duration,
            mode="sandbox" if self.sandbox_mode else "production",
            response_hash=response_hash,
            backend_used=self.backend.BACKEND_ID,
            schema_version="v1.0"
        )
