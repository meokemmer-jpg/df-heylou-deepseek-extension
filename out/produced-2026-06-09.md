# df-heylou-deepseek-extension — PRODUKTION [CRUX-MK]
*2026-06-09T17:04:39.755026+00:00 | ollama-local/kemmer-14b-ctx8k*

# df-heylou-deepseek-extension [CRUX-MK]

## Einleitung

Die Dark-Factory `df-heylou-deepseek-extension` integriert HeyLou als Sub-Funktion in DeepSeek's Function-Calling-API, um das Portfolio an Dienstleistungen für Hotellerie und Business Travel zu erweitern. Diese Integration ermöglicht es dem LLM (Large Language Model), direkt auf Daten im HeyLou Travel-Knowledge Graph zuzugreifen, um präzisere Antworten zur Verfügung zu stellen.

## Welle-39 LLM Sub-Funktion Extension

### Überblick
Die Welle-39 der DeepSeek-Funktionalität bringt eine neue Dimension für die Integration von externen Systemen wie HeyLou. Die Erweiterung ermöglicht es dem Modell, Funktionen aufzurufen, die speziell für den Travel-Bereich entwickelt wurden und direkt in das System integriert sind.

### Stack
- **DeepSeek API-Plugin:** Die Grundlage, um externe Funktionen aufrufen zu können.
- **Function-Calling:** Mechanismus zur Durchführung von Funktionsaufrufen innerhalb des LLMs.

## HeyLou Capability Set

HeyLou bietet fünf verschiedene Funktionen, die durch das DeepSeek LLM aufgerufen werden können:

| Function | Beschreibung | Backend |
|---|---|---|
| `search_hotels(location, dates, preferences)` | Sucht Hotels im Bereich des Travel-Knowledge Graphs. | df-heylou-travel-domain |
| `get_rates(hotel_id, date_range)` | Ruft die Preise für ein Hotel ab, basierend auf der angegebenen Zeitraum. | df-pms-mews-adapter (Welle 36) |
| `compare_otas(hotel_id, dates)` | Vergleicht die Bookings durch verschiedene OTAs (Online Travel Agents). | df-ota-* (Welle 37) |
| `book_direct(hotel_id, room_type, guest, dates)` | Führt eine Buchung direkt über HeyLou ohne Kommissionierung aus. | df-heylou-travel-domain |
| `optimize_revenue(hotel_id)` | Berechnet ein Revenue-Optimierungsmodell für ein Hotel (vorläufig). | Welle 40 (vorläufig) |

### Beispiele für Funktionsaufrufe
1. **Hotel-Suche:**
   ```python
   tools = [{"function_declarations": HEYLOU_FUNCTION_DEFINITIONS}]
   response = deepseek_client.generate_content(prompt="Find hotels in Berlin for July 2026 with a preference for budget hotels.", tools=tools)
   ```
   
2. **Rate-Ermittlung:**
   ```python
   result = extension.handle_function_call({"function": "get_rates", "hotel_id": "H12345", "date_range": ["2026-07-01", "2026-07-15"]})
   ```
   
3. **OTA-Spreading:**
   ```python
   response = deepseek_client.generate_content(prompt="Compare OTA bookings for Hotel H12345 in June 2026.", tools=tools)
   ```

## Provider-API-Pattern

### JSON-Schema für Funktionenaufrufe
Das DeepSeek-Modell verwendet ein JSON-Schema, um Tool-Deklarationen zu definieren. Dieses Schema wird dann von der Extension genutzt, um Funktionsanrufe an das entsprechende Backend weiterzuleiten.

```python
tools = [{"function_declarations": HEYLOU_FUNCTION_DEFINITIONS}]
response = deepseek_client.generate_content(prompt=prompt_text, tools=tools)
```

### Beispiel für den JSON-Schema-Content
Hier ist ein Beispiel für die Deklaration der `search_hotels` Funktion:
```json
{
  "name": "search_hotels",
  "description": "Sucht Hotels im Bereich des Travel-Knowledge Graphs.",
  "parameters": {
    "type": "object",
    "properties": {
      "location": { "type": "string" },
      "dates": { "type": "array", "items": { "type": "string", "format": "date" } },
      "preferences": { "type": "object", "description": "Zusätzliche Präferenzen wie Preisbereich, Sternezahl usw." }
    }
  }
}
```

## Sandbox-Default
Um Entwicklung und Testzwecke zu unterstützen, gibt es zwei Betriebsmodi:
- **Mock-Modus:** Wenn `DF_HEYLOU_DEEPSEEK_EXT_ENABLED=false`, werden synthetische Antworten basierend auf einem mockten Travel-Knowledge Graph bereitgestellt.
- **Real-Modus:** Mit aktivierten Umgebungsvariablen (`DF_HEYLOU_DEEPSEEK_EXT_ENABLED=true`), `PHRONESIS_TICKET` und `DEEPSEEK_API_KEY`, werden echte Anfragen an das HeyLou System gesendet.

## Architektur

Die Architektur ist modelliert, um eine robuste Kommunikation zwischen dem LLM und den externen Backend-Systemen sicherzustellen:

```
DeepSeek-LLM → functionCall → DeepSeekExtension.handle_function_call()
                              ├── search_hotels    → df-heylou-travel-domain
                              ├── get_rates        → df-pms-mews-adapter
                              ├── compare_otas     → df-ota-* (Welle 37)
                              ├── book_direct      → df-heylou-travel-domain
                              └── optimize_revenue → Welle 40 (vorläufig)
                              ↓
                          AuditLogger (HMAC-SHA256 JSONL)
```

## Security und Compliance

- **Pre-Action Verification:** Der `auth_handler.verify_phronesis_ticket()` Mechanismus wird verwendet, um sicherzustellen, dass jeder Funktionsaufruf autorisiert ist.
- **Audit Logging:** Alle Anrufe werden in einem audit-log überwacht, der HMAC-SHA256 verwendet, um die Integrität zu sichern.

## Deployment und Verwaltung

### Sandbox-Mitglieder
Für den Betrieb im Sandbox-Modus wird ein Plist-Datei bereitgestellt:
```bash
scripts/com.kemmer.df-heylou-deepseek-extension.plist
```
Die Startinterval ist auf 7200 Sekunden (2 Stunden) eingestellt, um Ressourcen zu sparen.

### Tests
Um die Funktionalität und Stabilität der Erweiterung sicherzustellen, sind automatisierte Tests integriert:
```bash
pytest tests/ -v
```

## Cross-DF-Coupling (Welle 36/Welle 37 Backends)

Die Extension arbeitet eng mit anderen Dark-Factories zusammen, um ein komplexes System von Dienstleistungen und Datenquellen zu erstellen. Insbesondere:

- **df-pms-mews-adapter** für die Kommunikation mit den Property Management Systems.
- **df-ota-* (Welle 37)** für das Analysieren der OTA Buchungsdaten.

## Zusammenfassung

Die Integration von HeyLou in DeepSeek erweitert die Funktionalitäten des LLMs und bietet Anwendern präzisere, personalisierte Dienstleistungen im Bereich des Business Travels. Durch eine klare Architektur und Sicherheitsmaßnahmen wird sichergestellt, dass diese Integration robust und sicher ist.

---

Diese Dokumentation deckt die wesentlichen Aspekte der Dark-Factory `df-heylou-deepseek-extension` ab und bereitet den Weg für die effektive Nutzung dieser Technologie in produktiven Projekten.