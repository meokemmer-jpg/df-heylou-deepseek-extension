# df-heylou-deepseek-extension — Output [CRUX-MK]
*Autonom aktiviert 2026-06-05T09:50:06.626177+00:00 | ollama-local/qwen2.5:14b-instruct*

# df-heylou-deepseek-extension [CRUX-MK]

## Welle-39 LLM Sub-Funktion Extension: HeyLou als DeepSeek Function-Callin
Function-Calling

### Überblick

**Stack:** DeepSeek API-Plugin / Function-Calling.

HeyLou wird als Sub-Funktionalität für DeepSeek eingebunden, um Funktionen 
wie Hotel-Suche, Rate-Ermittlung und Buchungen direkt durch den HeyLou Trav
Travel-Knowledge Graph zu unterstützen. Diese Integration erweitert die Rei
Reichweite von HeyLou auf die Nutzerbasis von DeepSeek.

### HeyLou Capability Set (5 Functions)

| Function | Beschreibung | Backend |
|---|---|---|
| `search_hotels(location, dates, preferences)` | Hotel-Suche im Travel-Kno
Travel-Knowledge-Graph | df-heylou-travel-domain |
| `get_rates(hotel_id, date_range)` | PMS/RMS-Rates pro Hotel | df-pms-mews
df-pms-mews-adapter (Welle 36) |
| `compare_otas(hotel_id, dates)` | OTA-Spreading | df-ota-* (Welle 37) |
| `book_direct(hotel_id, room_type, guest, dates)` | Direct-Buchung via Hey
HeyLou (kommissionsfrei) | df-heylou-travel-domain |
| `optimize_revenue(hotel_id)` | Revenue-Optimizer Stub | Welle 40 (vorläuf
(vorläufig) |

### Provider-API-Pattern

Der DeepSeek Client ruft Funktionen auf, die durch das HeyLou System abgear
abgearbeitet werden. Die Aufrufe erfolgen über ein JSON-Schema, das Tool-De
Tool-Declarations enthält.

```python
tools = [{"function_declarations": HEYLOU_FUNCTION_DEFINITIONS}]
response = deepseek_client.generate_content(prompt, tools=tools)
for part in response.candidates[0].content.parts:
    if part.function_call:
        result = extension.handle_function_call(part.function_call)
```

### Sandbox-Default

- `DF_HEYLOU_DEEPSEEK_EXT_ENABLED=false`: Mock-Antworten (synthetische Trav
Travel-Knowledge Graph).
- `DF_HEYLOU_DEEPSEEK_EXT_ENABLED=true`, `PHRONESIS_TICKET` und `DEEPSEEK_A
`DEEPSEEK_API_KEY`: Real-Mode.

### Architektur

```
DeepSeek-LLM → functionCall → DeepSeekExtension.handle_function_call()
                              ├── search_hotels    → mock | df-heylou-trave
df-heylou-travel-domain
                              ├── get_rates        → mock | df-pms-mews-ada
df-pms-mews-adapter
                              ├── compare_otas     → mock | df-ota-booking-
df-ota-booking-adapter
                              ├── book_direct      → mock | df-heylou-trave
df-heylou-travel-domain (K_0)
                              └── optimize_revenue → mock | W40-Stub
                              ↓
                          AuditLogger (HMAC-SHA256 JSONL)
```

### Tests

```bash
pytest tests/ -v
```

### Cross-DF-Coupling (Welle 36/Welle 37 Backends)

Für eine funktionsfähige Integration sind die entsprechenden Backends von W
Welle 36 und Welle 37 erforderlich. Aktuell sind Lazy-Import-Stubs implemen
implementiert, um die Interoperabilität zu gewährleisten.

### Sandbox-Konfiguration

Die Konfigurationsdatei `config.yaml` bietet die notwendigen Einstellungen 
für den Betrieb in der Sandbox-Umgebung und im Real-Modus. K13-Vorprüfungen
K13-Vorprüfungen via `auth_handler.verify_phronesis_ticket()` sorgen für Au
Authentifizierung, während K16 mkdir-Mutex-Behandlungsmechanismen sicherste
sicherstellen, dass Schreibkonflikte vermieden werden.

### LaunchAgent

Die Konfiguration des LaunchAgents ermöglicht den Hintergrundbetrieb der Da
Dark-Factory. Der Plist `com.kemmer.df-heylou-deepseek-extension.plist` wir
wird bei jedem Systemstart ausgeführt und übernimmt das Warten auf neue Auf
Aufrufe von DeepSeek.

---

Diese Dokumentation bietet eine umfassende Beschreibung des `df-heylou-deep
`df-heylou-deepseek-extension`, einschließlich seiner Architektur, Funktion
Funktionen und Integrationsdetails.