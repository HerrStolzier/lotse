# AI Memory Search MVP Decision

**Status**: Aktualisierte lokale Modellentscheidung  
**Date**: 2026-05-13

## Worum es in diesem Dokument geht
Dieses Dokument legt fest, wie Sprint 2 praktisch starten soll.

Wichtig:
- Das ist noch keine finale Produktfreigabe.
- Das ist die **Arbeitsentscheidung**, mit der wir sinnvoll in die Implementierung gehen koennen.

## Kurzentscheidung
Sprint 2 soll mit einem **kontrollierten Retrieval-first-MVP** starten.

Das bedeutet:
1. zuerst Datenmodell und Suchsignale verbessern
2. dann Query-Verstehen ueber ein lokales LLM anschliessen
3. erst danach optionale Treffer-Erklaerung

Die erste Version soll **kein freier Chat ueber alle Dokumente** sein.

## Modellentscheidung fuer den Start

### Primaerer Zielkandidat
- **Qwen/Qwen2.5-7B-Instruct**

### Vergleichskandidaten fuer spaetere Laeufe
- **mistralai/Mistral-7B-Instruct-v0.3**
- **microsoft/Phi-4-mini-instruct**
- **meta-llama/Llama-3.1-8B-Instruct**, falls Lizenz/Gating akzeptabel sind

## Warum genau diese Wahl

### Warum Qwen2.5-7B als primaerer Zielkandidat
- liegt dem aktuellen Kurier-Setup schon nah
- ist verbreitet und lokal leicht nachvollziehbar
- ist ein klassisches Instruct-Modell ohne lange sichtbare Reasoning-Ausgabe
- liefert im Kurier-Benchmark stabile strukturierte Antworten
- passt auf dem lokalen System zu 24 GB RAM

### Wichtiger Realitaetshinweis
Diese Entscheidung ist eine **Praxisentscheidung fuer den aktuellen Demo-RC**, keine endgueltige Siegerkrone.

Der Kurier-Benchmark vom 2026-05-13 empfiehlt `ollama:qwen2.5:7b` mit ca. 83% Gesamtqualitaet und ca. 4,1 Sekunden pro Fall. Qwen3/Qwen3.5-Modelle wurden vorher als unpassend einsortiert, weil sie bei einfachen JSON-Aufgaben in lange Denk-Ausgaben und Timeouts abdriften koennen.

## Architekturentscheidung fuer den MVP

### Fester Grundsatz
**Retrieval first, LLM second.**

### Das heisst konkret
- Das LLM versteht die Nutzeranfrage.
- Es erzeugt Suchvarianten und moegliche Filter.
- Die bestehende Hybrid-Suche holt echte Treffer.
- Optional erklaert ein schmaler zweiter Schritt, warum ein Treffer passt.

### Das heisst ausdruecklich nicht
- kein Modell, das frei ueber alle Dokumente "nachdenkt"
- kein Agent, der Dokumente selbststaendig durchsucht
- keine freie textuelle Antwort ohne Retrieval-Basis

## Sicherheitsentscheidung fuer den MVP
Die erste Version muss folgende Leitplanken haben:

1. Das LLM bekommt zuerst nur die Nutzeranfrage, nicht den kompletten Dokumentbestand.
2. Treffer-Erklaerungen duerfen nur auf kleinen, kontrollierten Datenstuecken basieren.
3. Dokumenttext bleibt Datenquelle, nicht Instruktionsquelle.
4. Such- und API-Ausgabe wird minimiert.
5. KI-Ausgaben werden als untrusted behandelt und nur als Text gerendert.

## Datenmodellentscheidung fuer Sprint 2
Sprint 2 soll nicht nur an der Suchlogik bauen, sondern zuerst an den Suchsignalen.

### Pflichtfelder fuer den MVP
- `suggested_filename`
- `destination_name`
- `display_title`

### Warum diese Felder Pflicht sind
- Nutzer erinnern sich oft an den sprechenden Dateinamen.
- Vollstaendige Pfade sind fuer Suche oft unnoetig und privacy-technisch schlechter.
- `display_title` macht CLI, API und Dashboard konsistenter.

## MVP-Scope fuer Sprint 2

### In Scope
- DB-/Index-Erweiterung fuer neue Suchsignale
- Such-Response als minimiertes DTO
- Query-Assist ueber lokales LLM
- mehrere Suchvarianten pro Anfrage
- Hybrid-Suche + Trefferfusion
- kurze Match-Begruendung in sicherem Textformat
- zuerst CLI und API, dann Dashboard

### Bewusst nicht in Scope
- Rueckfragen-Dialog
- lernendes Feedback-System
- persoenliche Suchempfehlungen
- cloudbasierte Modellorchestrierung
- freier Dokument-Chat

## Reihenfolge fuer Sprint 2
1. Schema und Index erweitern
2. Suchausgabe minimieren
3. Query-Assist einbauen
4. Retrieval-Fusion anbinden
5. sichere Treffer-Erklaerung ergaenzen
6. dann UI nachziehen

## Go-/No-Go-Kriterien

### Go
- JSON-Ausgabe des Modells ist stabil
- Suchvarianten sind brauchbar
- keine zusaetzlichen grossen Privacy-Leaks
- Treffer wirken fuer echte Kurier-Faelle nachvollziehbar

### No-Go
- das Modell halluziniert zu stark
- Treffer-Erklaerung braucht zu viel Rohtext
- lokale Laufzeit ist fuer Alltag zu traege
- API/UI geben weiter rohe oder ueberbreite Daten aus

## Praktischer Sprint-2-Startsatz
Wenn wir Sprint 2 morgen anfangen, dann lautet die Arbeitsanweisung sinngemaess:

> Erweitere zuerst das Datenmodell um sprechende Suchsignale und baue danach einen lokalen Query-Assist auf Basis von Qwen3-4B, mit Qwen2.5-7B als Fallback. Halte die Suche retrieval-first, reduziere die Datenausgabe und behandle alle KI-Ausgaben defensiv.
>
> Aktualisierung 2026-05-13: Nutze fuer den lokalen Demo-RC zuerst Qwen2.5-7B-Instruct. Es ist auf diesem System installiert, vom Kurier-Benchmark empfohlen und vermeidet die fuer Kurier unpraktischen langen Reasoning-Ausgaben.
