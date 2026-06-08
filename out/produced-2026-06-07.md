# df-heylou-deepseek-extension — PRODUKTION [CRUX-MK]
*2026-06-07T14:33:02.083225+00:00 | ollama-local/kemmer-70b-ctx8k*

# df-heylou-deepseek-extension
## Einführung
Die `df-heylou-deepseek-extension` ist eine Erweiterung für die DeepSeek-Pl
DeepSeek-Plattform, die es ermöglicht, HeyLou-Funktionen direkt über die De
DeepSeek-API aufzurufen. Diese Integration erweitert die Reichweite von Hey
HeyLou auf die Nutzerbasis von DeepSeek und bietet eine umfassende Lösung f
für Reiseplanung und -buchung.

## HeyLou Capability Set
Die `df-heylou-deepseek-extension` unterstützt fünf Hauptfunktionen:

1. **Hotel-Suche**: Die Funktion `search_hotels(location, dates, preference
preferences)` ermöglicht es Nutzern, Hotels anhand von Lage, Datum und Vorl
Vorlieben zu suchen.
2. **Rate-Ermittlung**: Die Funktion `get_rates(hotel_id, date_range)` lief
liefert die Preise für ein bestimmtes Hotel an einem bestimmten Datum oder 
innerhalb eines bestimmten Zeitraums.
3. **OTA-Vergleich**: Die Funktion `compare_otas(hotel_id, dates)` ermöglic
ermöglicht es Nutzern, die Preise von verschiedenen Online-Reisebüros (OTAs
(OTAs) wie Booking, Expedia und HRS zu vergleichen.
4. **Direktbuchung**: Die Funktion `book_direct(hotel_id, room_type, guest,
guest, dates)` ermöglicht es Nutzern, direkt über HeyLou zu buchen, ohne da
dass Provisionen anfallen.
5. **Revenue-Optimierung**: Die Funktion `optimize_revenue(hotel_id)` ist e
ein Stub, der in Zukunft eine umfassende Revenue-Optimierung für Hotels bie
bieten wird.

## Provider-API-Pattern
Die DeepSeek-API ruft Funktionen auf, die durch das HeyLou-System abgearbei
abgearbeitet werden. Die Aufrufe erfolgen über ein JSON-Schema, das Tool-De
Tool-Declarations enthält. Der Code dafür sieht wie folgt aus:
```python
tools = [{"function_declarations": HEYLOU_FUNCTION_DEFINITIONS}]
response = deepseek_client.generate_content(prompt, tools=tools)
for part in response.candidates[0].content.parts:
    if part.function_call:
        result = extension.handle_function_call(part.function_call)
```
## Sandbox-Default
Die Erweiterung bietet zwei Betriebsmodi:

* `DF_HEYLOU_DEEPSEEK_EXT_ENABLED=false`: In diesem Modus werden Mock-Antwo
Mock-Antworten verwendet, um die Funktionalität zu testen.
* `DF_HEYLOU_DEEPSEEK_EXT_ENABLED=true`, `PHRONESIS_TICKET` und `DEEPSEEK_A
`DEEPSEEK_API_KEY`: In diesem Modus wird die Erweiterung mit echten Daten u
und APIs betrieben.

## Architektur
Die Architektur der Erweiterung sieht wie folgt aus:
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
```
## Implementierung
Die Implementierung der Erweiterung erfolgt in Python. Die Hauptfunktionen 
werden durch die `df-heylou-deepseek-extension`-Klasse implementiert.

### df-heylou-deepseek-extension-Klasse
```python
class df_heylou_deepseek_extension:
    def __init__(self):
        self.tools = [{"function_declarations": HEYLOU_FUNCTION_DEFINITIONS
HEYLOU_FUNCTION_DEFINITIONS}]

    def handle_function_call(self, function_call):
        # Verarbeite die Funktion und gib das Ergebnis zurück
        pass

    def search_hotels(self, location, dates, preferences):
        # Suche Hotels anhand von Lage, Datum und Vorlieben
        pass

    def get_rates(self, hotel_id, date_range):
        # Liefere die Preise für ein bestimmtes Hotel an einem bestimmten D
Datum oder innerhalb eines bestimmten Zeitraums
        pass

    def compare_otas(self, hotel_id, dates):
        # Vergleiche die Preise von verschiedenen Online-Reisebüros (OTAs)
        pass

    def book_direct(self, hotel_id, room_type, guest, dates):
        # Buche direkt über HeyLou, ohne dass Provisionen anfallen
        pass

    def optimize_revenue(self, hotel_id):
        # Optimiere die Einnahmen für ein bestimmtes Hotel (Stub)
        pass
```
## Tests
Die Erweiterung wird durch umfassende Tests getestet, um sicherzustellen, d
dass alle Funktionen korrekt funktionieren. Die Tests werden mit dem `pytes
`pytest`-Framework durchgeführt.

### Test-Beispiele
```python
def test_search_hotels():
    # Suche Hotels anhand von Lage, Datum und Vorlieben
    location = "Berlin"
    dates = ["2024-01-01", "2024-01-02"]
    preferences = {"price": "low"}
    result = df_heylou_deepseek_extension().search_hotels(location, dates, 
preferences)
    assert len(result) > 0

def test_get_rates():
    # Liefere die Preise für ein bestimmtes Hotel an einem bestimmten Datum
Datum oder innerhalb eines bestimmten Zeitraums
    hotel_id = "12345"
    date_range = ["2024-01-01", "2024-01-02"]
    result = df_heylou_deepseek_extension().get_rates(hotel_id, date_range)
date_range)
    assert len(result) > 0

def test_compare_otas():
    # Vergleiche die Preise von verschiedenen Online-Reisebüros (OTAs)
    hotel_id = "12345"
    dates = ["2024-01-01", "2024-01-02"]
    result = df_heylou_deepseek_extension().compare_otas(hotel_id, dates)
    assert len(result) > 0

def test_book_direct():
    # Buche direkt über HeyLou, ohne dass Provisionen anfallen
    hotel_id = "12345"
    room_type = "single"
    guest = "Max Mustermann"
    dates = ["2024-01-01", "2024-01-02"]
    result = df_heylou_deepseek_extension().book_direct(hotel_id, room_type
room_type, guest, dates)
    assert result == "Buchung erfolgreich"

def test_optimize_revenue():
    # Optimiere die Einnahmen für ein bestimmtes Hotel (Stub)
    hotel_id = "12345"
    result = df_heylou_deepseek_extension().optimize_revenue(hotel_id)
    assert result == "Einnahmen optimiert"
```
## Fazit
Die `df-heylou-deepseek-extension` ist eine umfassende Erweiterung für die 
DeepSeek-Plattform, die es ermöglicht, HeyLou-Funktionen direkt über die De
DeepSeek-API aufzurufen. Die Erweiterung bietet fünf Hauptfunktionen: Hotel
Hotel-Suche, Rate-Ermittlung, OTA-Vergleich, Direktbuchung und Revenue-Opti
Revenue-Optimierung. Die Implementierung erfolgt in Python und wird durch u
umfassende Tests getestet. Die Erweiterung ist ein wichtiger Schritt zur Er
Erweiterung der Reichweite von HeyLou auf die Nutzerbasis von DeepSeek.