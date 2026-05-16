# AI Memory Search Model Shortlist

**Status**: Aktualisierte Shortlist nach lokalem Kurier-Benchmark  
**Date**: 2026-05-13

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

### 1. Qwen/Qwen2.5-7B-Instruct
- **Link**: [Qwen/Qwen2.5-7B-Instruct](https://hf.co/Qwen/Qwen2.5-7B-Instruct)
- **Groesse**: ca. 7.6B Parameter
- **Lizenz**: Apache-2.0
- **Warum auf der Liste**:
  - aktueller praktischer Default fuer Kurier
  - sehr verbreitet
  - klassisches Instruct-Modell ohne lange sichtbare Reasoning-Ausgabe
  - lokal bereits ueber Ollama verfuegbar
- **Lokaler Kurier-Benchmark vom 2026-05-13**:
  - Gesamtqualitaet im Einzeltest: ca. `83%`
  - Gesamtqualitaet im Dreiervergleich: ca. `80%`
  - durchschnittliche Laufzeit im Dreiervergleich: ca. `4651 ms` pro Fall
  - Dokumente erkennen: `79%`
  - Suchanfragen verstehen: `61%`
  - richtige Treffer finden: `100%`
- **Praktische Erwartung fuer Kurier**:
  - beste aktuelle Wahl fuer den Demo-RC
  - stabil genug fuer lokale Klassifikation und Retrieval-Erklaerung
- **Offene Frage**:
  - Suchanfragen-Verstehen bleibt der schwaechste gemessene Bereich und sollte mit besseren Prompts/Testfaellen weiter verbessert werden

### 2. mistralai/Mistral-7B-Instruct-v0.3
- **Link**: [mistralai/Mistral-7B-Instruct-v0.3](https://hf.co/mistralai/Mistral-7B-Instruct-v0.3)
- **Groesse**: ca. 7.2B Parameter
- **Lizenz**: Apache-2.0
- **Warum auf der Liste**:
  - klassisches Instruct-Modell
  - gute lokale Verfuegbarkeit ueber GGUF/Ollama-nahe Setups
  - sinnvoller Challenger gegen Qwen2.5-7B
- **Praktische Erwartung fuer Kurier**:
  - guter Vergleichskandidat, falls Qwen2.5 bei einzelnen deutschen Dokumenttypen schwankt
- **Offene Frage**:
  - im Benchmark stark bei Dokumentklassifikation, aber fuer den Gesamtnutzen noch nicht besser als Qwen2.5-7B
- **Lokaler Kurier-Benchmark vom 2026-05-13**:
  - Dokumente erkennen: `100%`
  - Suchanfragen verstehen: `57%`
  - richtige Treffer finden: `75%`
  - durchschnittliche Laufzeit: ca. `6298 ms` pro Fall

### 3. microsoft/Phi-4-mini-instruct
- **Link**: [microsoft/Phi-4-mini-instruct](https://hf.co/microsoft/Phi-4-mini-instruct)
- **Groesse**: Mini-Klasse
- **Lizenz**: MIT
- **Sprachen laut Hub**:
  - multilingual, unter anderem `de` und `en`
- **Warum auf der Liste**:
  - klein und potentiell schnell
  - permissive Lizenz
  - kein primaeres Reasoning-Modell
- **Praktische Erwartung fuer Kurier**:
  - interessanter Speed-Kandidat fuer spaetere Laeufe
- **Offene Frage**:
  - schnell, aber im aktuellen Benchmark bei Such-/Treffer-Aufgaben zu schwach fuer den Default
- **Lokaler Kurier-Benchmark vom 2026-05-13**:
  - Dokumente erkennen: `88%`
  - Suchanfragen verstehen: `48%`
  - richtige Treffer finden: `50%`
  - durchschnittliche Laufzeit: ca. `3366 ms` pro Fall

### 4. Qwen/Qwen3-4B-Instruct-2507
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
  - bleibt fachlich interessant, ist aber nicht mehr der Startkandidat
  - Qwen3/Qwen3.5-nahe lokale Tests zeigten bei Kurier-Aufgaben ein Risiko fuer lange Denk-Ausgaben und Timeouts
- **Offene Frage**:
  - nur wieder aufnehmen, wenn Reasoning-Ausgaben sicher deaktivierbar sind und der Kurier-Benchmark sauber durchlaeuft

### 5. meta-llama/Llama-3.1-8B-Instruct
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

### 6. mistralai/Ministral-3-8B-Instruct-2512
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

1. `Qwen/Qwen2.5-7B-Instruct`
2. `mistralai/Mistral-7B-Instruct-v0.3`
3. `microsoft/Phi-4-mini-instruct`

### Sekundaere Testgruppe
- `meta-llama/Llama-3.1-8B-Instruct`
- `mistralai/Ministral-3-8B-Instruct-2512`
- `Qwen/Qwen3-4B-Instruct-2507`, nur wenn Reasoning-Ausgaben sicher kurz gehalten werden koennen

## Warum diese Reihenfolge sinnvoll ist
- **Qwen2.5-7B** ist der lokal bewiesene Startpunkt und vom Kurier-Benchmark empfohlen.
- **Mistral-7B-Instruct-v0.3** ist bei Dokumentklassifikation stark, verliert aber im aktuellen Kurier-Gesamtlauf gegen Qwen2.5-7B.
- **Phi-4-mini-instruct** ist schneller, verliert aber aktuell zu viel Qualitaet bei Suchanfragen und Trefferwahl.
- **Llama-3.1-8B** bleibt stark, ist aber wegen Gating/Lizenz unbequemer fuer den Default.

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

- **bester aktueller Startkandidat**: `Qwen/Qwen2.5-7B-Instruct`
- **wichtigste Challenger**: `mistralai/Mistral-7B-Instruct-v0.3` und `microsoft/Phi-4-mini-instruct`
- **staerkster Referenzkandidat**: `meta-llama/Llama-3.1-8B-Instruct`

Das ist eine Produktnahe Entscheidung fuer den Demo-RC, aber noch keine endgueltige Langfrist-Festlegung.

## Naechster Schritt
Der naechste sinnvolle Schritt ist jetzt nicht weitere Modellkarten zu lesen, sondern:

1. Qwen2.5-7B fuer den Demo-RC als lokalen Default nutzen
2. Suchanfragen-Verstehen mit besseren Prompts oder Testfaellen verbessern
3. Mistral-7B-Instruct-v0.3 und Phi-4-mini-instruct erst wieder in Betracht ziehen, wenn der Such-/Retrieval-Prompt ueberarbeitet wurde

## Quellenhinweise
- Qwen3-4B-Instruct-2507 Modellkarte: [https://hf.co/Qwen/Qwen3-4B-Instruct-2507](https://hf.co/Qwen/Qwen3-4B-Instruct-2507)
- Qwen2.5-7B-Instruct Modellkarte: [https://hf.co/Qwen/Qwen2.5-7B-Instruct](https://hf.co/Qwen/Qwen2.5-7B-Instruct)
- Mistral-7B-Instruct-v0.3 Modellkarte: [https://hf.co/mistralai/Mistral-7B-Instruct-v0.3](https://hf.co/mistralai/Mistral-7B-Instruct-v0.3)
- Phi-4-mini-instruct Modellkarte: [https://hf.co/microsoft/Phi-4-mini-instruct](https://hf.co/microsoft/Phi-4-mini-instruct)
- Llama-3.1-8B-Instruct Modellkarte: [https://hf.co/meta-llama/Llama-3.1-8B-Instruct](https://hf.co/meta-llama/Llama-3.1-8B-Instruct)
- Ministral-3-8B-Instruct-2512 Modellkarte: [https://hf.co/mistralai/Ministral-3-8B-Instruct-2512](https://hf.co/mistralai/Ministral-3-8B-Instruct-2512)
- Hugging Face Leaderboard-Daten-Doku: [https://huggingface.co/docs/hub/leaderboard-data-guide](https://huggingface.co/docs/hub/leaderboard-data-guide)
