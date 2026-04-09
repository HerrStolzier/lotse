# AI Memory Search Model Shortlist

**Status**: Draft for Sprint 1  
**Date**: 2026-04-09

## Zweck
Dieses Dokument sammelt die ersten Modellkandidaten fuer die Erinnerungssuche in Kurier.

Wichtig: Das ist noch keine Endentscheidung. Es ist eine Shortlist fuer den lokalen Praxisvergleich.

## Auswahlkriterien fuer Kurier
Ein Modell ist fuer Kurier nicht deshalb gut, weil es allgemein beliebt ist, sondern wenn es diese Aufgaben lokal zuverlaessig erledigt:

1. freie deutsche Nutzerbeschreibung verstehen
2. saubere Suchvarianten erzeugen
3. strukturierte JSON-Ausgabe stabil liefern
4. moegliche Filter erkennen wie Firma, Zeitraum, Dokumenttyp
5. kurz und vorsichtig erklaeren, warum ein Treffer passt

Zusatzkriterien:

- lokal realistisch nutzbar
- brauchbare Geschwindigkeit
- vernuenftige Lizenz
- mehrsprachig genug fuer deutsche Dokumente mit englischen Begriffen

## Kandidaten-Shortlist

### 1. Qwen/Qwen3-4B-Instruct-2507
- **Link**: [Qwen/Qwen3-4B-Instruct-2507](https://hf.co/Qwen/Qwen3-4B-Instruct-2507)
- **Groesse**: ca. 4B Parameter
- **Lizenz**: Apache-2.0
- **Warum auf der Liste**:
  - moderne kleine Instruct-Variante
  - wirkt stark fuer lokales Query-Rewriting und strukturierte Antworten
  - gute Balance aus Groesse und Benchmark-Signal
- **Benchmark-Signale aus der Modellkarte**:
  - IFEval: `83.4`
  - BFCL-v3: `61.9`
  - MultiIF: `69.0`
  - MMLU-redux: `77.8`
- **Praktische Erwartung fuer Kurier**:
  - sehr interessanter Startkandidat fuer den lokalen Standard
  - koennte besonders stark bei Instruktionsbefolgung und kompaktem JSON sein
- **Offene Frage**:
  - noch lokal gegen echte deutsche Kurier-Faelle pruefen

### 2. Qwen/Qwen2.5-7B-Instruct
- **Link**: [Qwen/Qwen2.5-7B-Instruct](https://hf.co/Qwen/Qwen2.5-7B-Instruct)
- **Groesse**: ca. 7.6B Parameter
- **Lizenz**: Apache-2.0
- **Warum auf der Liste**:
  - bereits der aktuelle Default in Kurier-nahem Setup
  - sehr verbreitet
  - wahrscheinlich der fairste Referenzpunkt gegen "neueres Modell vs. bestehender Standard"
- **Signale aus der Modellkarte**:
  - lange Kontextlaenge
  - starke Verbreitung und gute lokale Verfuegbarkeit
- **Praktische Erwartung fuer Kurier**:
  - sehr guter Baseline-Kandidat
  - sollte auf jeden Fall im Vergleich bleiben, auch wenn spaeter ein anderes Modell gewinnt
- **Offene Frage**:
  - wie stabil ist das Modell bei strengem JSON im Vergleich zu neueren Kandidaten?

### 3. meta-llama/Llama-3.1-8B-Instruct
- **Link**: [meta-llama/Llama-3.1-8B-Instruct](https://hf.co/meta-llama/Llama-3.1-8B-Instruct)
- **Groesse**: ca. 8B Parameter
- **Lizenz**: Llama 3.1 Community License
- **Sprachen laut Modellkarte**:
  - unter anderem `de`, `en`, `fr`, `it`, `es`, `pt`
- **Warum auf der Liste**:
  - starker Referenzkandidat fuer Instruct-Qualitaet
  - gutes Signal bei Tool- und Funktions-nahem Verhalten
  - deutsche Sprachunterstuetzung ist ausdruecklich sichtbar
- **Benchmark-Signale aus der Modellkarte**:
  - IFEval: `80.4`
  - BFCL: `76.1`
  - API-Bank: `82.6`
  - Multilingual MGSM: `68.9`
  - German MMLU: `60.59`
- **Praktische Erwartung fuer Kurier**:
  - sehr guter Referenzpunkt fuer "starkes 8B-Modell"
  - vor allem interessant, wenn sauberes strukturiertes Verhalten wichtiger ist als Minimalgroesse
- **Offene Frage**:
  - Lizenz und Gating sind unbequemer als bei Qwen

### 4. mistralai/Ministral-3-8B-Instruct-2512
- **Link**: [mistralai/Ministral-3-8B-Instruct-2512](https://hf.co/mistralai/Ministral-3-8B-Instruct-2512)
- **Groesse**: knapp 9B Parameter
- **Lizenz**: Apache-2.0
- **Sprachen laut Modellkarte**:
  - unter anderem `de`, `en`, `fr`, `es`, `it`, `pt`, `nl`
- **Warum auf der Liste**:
  - moderner multilingualer 8B-Kandidat
  - potentiell stark fuer europaeische Sprachen
  - interessante Alternative, falls Qwen lokal nicht sauber genug liefert
- **Signal-Lage**:
  - in der Hub-Ansicht ist die Sprachabdeckung sichtbar
  - Benchmark-Signale sind in der oeffentlichen Kurzanzeige weniger bequem als bei Qwen oder Llama sichtbar
- **Praktische Erwartung fuer Kurier**:
  - lohnender Challenger-Kandidat
  - sollte vor allem dann getestet werden, wenn Deutsch und strukturierte Extraktion zusammen stark sein muessen

## Vorlaeufige Priorisierung fuer den lokalen Praxisvergleich

### Primaere Testgruppe
Diese drei Modelle sollten zuerst gegeneinander laufen:

1. `Qwen/Qwen3-4B-Instruct-2507`
2. `Qwen/Qwen2.5-7B-Instruct`
3. `meta-llama/Llama-3.1-8B-Instruct`

### Sekundaere Testgruppe
- `mistralai/Ministral-3-8B-Instruct-2512`

## Warum diese Reihenfolge sinnvoll ist
- **Qwen3-4B** testet, ob ein kleiner moderner Kandidat schon stark genug ist.
- **Qwen2.5-7B** ist die faire Baseline gegen den heutigen Kurier-Nahestand.
- **Llama-3.1-8B** ist der starke Referenzkandidat fuer Instruct-Qualitaet und strukturierte Disziplin.
- **Ministral-3-8B** ist der Herausforderer mit multilingualem Fokus.

## Benchmark-Signale richtig lesen
Die hier genannten Zahlen sind nuetzlich, aber nicht automatisch fair vergleichbar.

Gruende:

- Modellkarten verwenden nicht immer dieselben Benchmark-Sets
- einzelne Werte messen oft nur indirekt, was Kurier wirklich braucht
- "gute Benchmarks" heissen noch nicht "gutes deutsches Query-Rewriting fuer lokale Dokumentsuche"

Darum gilt fuer Kurier:

**Allgemeine HF-Signale dienen nur zur Vorauswahl.  
Die eigentliche Entscheidung muss ueber einen kleinen Kurier-eigenen Benchmark laufen.**

## Relevante Benchmark-Arten fuer Kurier
Diese Arten von Benchmarks sind fuer die spaetere Bewertung besonders wichtig:

- **Instruction Following**
  - wichtig fuer korrektes Befolgen des JSON-Formats
- **Tool / Function Calling Naehe**
  - wichtig fuer strukturierte Extraktion statt Freitext-Geschwaetz
- **Mehrsprachige Leistung**
  - wichtig fuer deutsche Suchanfragen und gemischte Dokumente
- **Kleine Modellgroesse bei brauchbarer Leistung**
  - wichtig fuer lokale Nutzbarkeit

## Erste Arbeitsannahme
Wenn heute eine Vorab-Wette noetig waere, dann waere sie:

- **wahrscheinlich bester Startkandidat**: `Qwen/Qwen3-4B-Instruct-2507`
- **wichtigste Baseline**: `Qwen/Qwen2.5-7B-Instruct`
- **staerkster Referenzkandidat**: `meta-llama/Llama-3.1-8B-Instruct`

Das ist bewusst noch keine Produktentscheidung, sondern die Startaufstellung fuer den lokalen Vergleich.

## Naechster Schritt
Der naechste sinnvolle Schritt ist jetzt nicht weitere Modellkarten zu lesen, sondern:

1. Kurier-Mini-Benchmark mit echten Suchfaellen anlegen
2. JSON-Stabilitaet und Laufzeit messen
3. danach erst das Startmodell fuer den MVP festlegen

## Quellenhinweise
- Qwen3-4B-Instruct-2507 Modellkarte: [https://hf.co/Qwen/Qwen3-4B-Instruct-2507](https://hf.co/Qwen/Qwen3-4B-Instruct-2507)
- Qwen2.5-7B-Instruct Modellkarte: [https://hf.co/Qwen/Qwen2.5-7B-Instruct](https://hf.co/Qwen/Qwen2.5-7B-Instruct)
- Llama-3.1-8B-Instruct Modellkarte: [https://hf.co/meta-llama/Llama-3.1-8B-Instruct](https://hf.co/meta-llama/Llama-3.1-8B-Instruct)
- Ministral-3-8B-Instruct-2512 Modellkarte: [https://hf.co/mistralai/Ministral-3-8B-Instruct-2512](https://hf.co/mistralai/Ministral-3-8B-Instruct-2512)
- Hugging Face Leaderboard-Daten-Doku: [https://huggingface.co/docs/hub/leaderboard-data-guide](https://huggingface.co/docs/hub/leaderboard-data-guide)
