# df-heylou-deepseek-extension — PRODUKTION [CRUX-MK]
*2026-06-07T02:10:08.865994+00:00 | ollama-local/kemmer-70b-ctx8k*

# df-heylou-deepseek-extension
## Übersicht

Die `df-heylou-deepseek-extension` ist eine Erweiterung für die DeepSeek-Pl
DeepSeek-Plattform, die es ermöglicht, Funktionen aus dem HeyLou-Travel-Kno
HeyLou-Travel-Knowledge-Graph direkt in DeepSeek zu integrieren. Diese Inte
Integration ermöglicht es Nutzern, Hotel-Suchen, Rate-Ermittlungen und Buch
Buchungen direkt durch den HeyLou-Service zu unterstützen.

## Funktionen

Die `df-heylou-deepseek-extension` bietet fünf Hauptfunktionen:

1. **Hotel-Suche**: Die Funktion `search_hotels(location, dates, preference
preferences)` ermöglicht es Nutzern, Hotels anhand von Standort, Datum und 
Vorlieben zu suchen.
2. **Rate-Ermittlung**: Die Funktion `get_rates(hotel_id, date_range)` ermö
ermöglicht es Nutzern, die Preise für ein bestimmtes Hotel in einem bestimm
bestimmten Zeitraum zu ermitteln.
3. **OTA-Spreading**: Die Funktion `compare_otas(hotel_id, dates)` ermöglic
ermöglicht es Nutzern, die Preise von verschiedenen Online-Travel-Agencies 
(OTAs) wie Booking, Expedia und HRS zu vergleichen.
4. **Direkte Buchung**: Die Funktion `book_direct(hotel_id, room_type, gues
guest, dates)` ermöglicht es Nutzern, direkt über den HeyLou-Service zu buc
buchen, ohne dass Provisionen anfallen.
5. **Revenue-Optimierung**: Die Funktion `optimize_revenue(hotel_id)` biete
bietet eine Vorläufige Möglichkeit, den Umsatz von Hotels zu optimieren.

## Technische Implementierung

Die `df-heylou-deepseek-extension` wird als DeepSeek-API-Plugin implementie
implementiert. Der DeepSeek-Client ruft die Funktionen auf, die durch das H
HeyLou-System abgearbeitet werden. Die Aufrufe erfolgen über ein JSON-Schem
JSON-Schema, das Tool-Declarations enthält.

```python
tools = [{"function_declarations": HEYLOU_FUNCTION_DEFINITIONS}]
response = deepseek_client.generate_content(prompt, tools=tools)
for part in response.candidates[0].content.parts:
    if part.function_call:
        result = extension.handle_function_call(part.function_call)
```

## Konfiguration

Die `df-heylou-deepseek-extension` kann in zwei Modi konfiguriert werden:

* **Sandbox-Modus**: In diesem Modus werden Mock-Antworten verwendet, um di
die Funktionen zu testen.
* **Real-Modus**: In diesem Modus werden echte Daten aus dem HeyLou-Travel-
HeyLou-Travel-Knowledge-Graph verwendet.

Die Konfiguration erfolgt über Umgebungsvariablen:

* `DF_HEYLOU_DEEPSEEK_EXT_ENABLED`: Aktiviert oder deaktiviert die Erweiter
Erweiterung.
* `PHRONESIS_TICKET`: Authentifizierungstoken für den HeyLou-Service.
* `DEEPSEEK_API_KEY`: API-Schlüssel für die DeepSeek-Plattform.

## Architektur

Die `df-heylou-deepseek-extension` besteht aus folgenden Komponenten:

* **DeepSeek-LLM**: Die LLM-Komponente von DeepSeek, die die Funktionen auf
aufruft.
* **HeyLou-Travel-Knowledge-Graph**: Der Travel-Knowledge-Graph von HeyLou,
HeyLou, der die Daten für die Funktionen bereitstellt.
* **df-heylou-deepseek-extension**: Die Erweiterung selbst, die die Funktio
Funktionen implementiert und mit dem DeepSeek-Client kommuniziert.

```
DeepSeek-LLM → functionCall → df-heylou-deepseek-extension.handle_function_
df-heylou-deepseek-extension.handle_function_call()
                              ├── search_hotels    → mock | HeyLou-Travel-K
HeyLou-Travel-Knowledge-Graph
                              ├── get_rates        → mock | df-pms-mews-ada
df-pms-mews-adapter
                              ├── compare_otas     → mock | df-ota-booking-
df-ota-booking-adapter
                              ├── book_direct      → mock | HeyLou-Travel-K
HeyLou-Travel-Knowledge-Graph (K_0)
                              └── optimize_revenue → mock | W40-Stub
```

## Tests

Die `df-heylou-deepseek-extension` kann mit den folgenden Tests getestet we
werden:

* **Unit-Tests**: Testen der einzelnen Funktionen.
* **Integrationstests**: Testen der Erweiterung als Ganzes.

```bash
pytest tests/ -v
```

## Cross-DF-Coupling

Die `df-heylou-deepseek-extension` ist mit anderen Dark-Factories-Komponent
Dark-Factories-Komponenten gekoppelt:

* **W36**: df-pms-mews-adapter.
* **W37**: df-ota-booking-adapter.

Diese Kopplung ermöglicht es, die Funktionen der Erweiterung zu erweitern u
und neue Features hinzuzufügen.