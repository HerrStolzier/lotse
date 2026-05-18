# Kurier Anti-Scheitern-Plan

Stand: 2026-05-18

Umsetzungsstand: Die erste praktische Haertungsrunde ist gestartet. Import, Suche, Review, Status/Doctor und Beta-Bericht wurden auf mehr Alltagssprache und klarere naechste Schritte ausgerichtet. Offen bleibt der echte 5-Tage-Alltagstest mit realen Dokumenten.

Dieser Plan beschreibt, woran Kurier in den naechsten Monaten am wahrscheinlichsten scheitert und wie wir das frueh verhindern. Der Fokus liegt zuerst auf echter Alltagsnutzung durch den Hauptnutzer, nicht auf einer breiten Produktfreigabe.

Die zentrale Produktregel lautet:

> Kurier muss zuerst Vertrauen schaffen. Neue Funktionen sind nur dann wertvoll, wenn der Nutzer sicher versteht, was passiert ist, wo ein Dokument liegt und wie ein Fehler schnell korrigiert wird.

## 5-Tage-Alltagstest

Der naechste Reife-Schritt ist ein kleiner, wiederholbarer Alltagstest:

1. An fuenf Nutzungstagen mindestens ein echtes Dokument verarbeiten oder eine echte Suche ausfuehren.
2. Keine perfekten manuellen Notizen fuehren.
3. Bei Frust, Unsicherheit oder falschem Ergebnis im Dashboard kurz "Problem melden" nutzen.
4. Am Ende `kurier beta report` ausfuehren.
5. Die haeufigsten Stolperer werden zur naechsten Produkt-Haertung.

Das Ziel ist nicht, moeglichst viele Features zu testen. Das Ziel ist, zu sehen, wo Kurier Vertrauen verliert.

## Produktmetriken

| Frage | Signal | Warum es wichtig ist |
| --- | --- | --- |
| Kann ich dem Ergebnis vertrauen? | `category_corrected`, `low_confidence_review`, `classification_confirmed` | Viele Korrekturen oder unsichere Einordnungen zeigen, dass der Nutzer kontrollieren muss. |
| Weiss ich nach dem Import, was passiert ist? | Import-Erfolg mit Zielort, Kategorie, Dateiname und Status | Ohne klare Erfolgskontrolle fuehlt sich Kurier wie eine Blackbox an. |
| Finde ich Dokumente mit Alltagssprache wieder? | `search_no_results`, Treffer mit Begruendung | Suche ist nur brauchbar, wenn leere oder unklare Ergebnisse erklaert werden. |
| Wo stolpert die Bedienung? | `manual_feedback` | Manuelles Feedback sammelt genau die Reibung, die automatische Signale nicht erkennen. |
| Laeuft die lokale Technik verlaesslich? | `upload_failed`, offene Webhook-Retrys, Doctor-/Status-Hinweise | Lokale Dienste duerfen nicht wie Bastelarbeit wirken. |

## Risiko 1: Zu viel Bastelgefuehl

**Status:** Teilweise umgesetzt.

**Symptom im Alltag:** Der Nutzer denkt an Pi, n8n, Ollama, Ports, Keys und Dienste statt an "Dokument rein, spaeter wiederfinden".

**Gegenmassnahme:** Kurier trennt Kernprodukt und Integrationen klar. Der Kern muss lokal ohne n8n nutzbar sein. Integrationen werden als Zusatznutzen gezeigt, nicht als Voraussetzung.

**Messsignal:** Doctor-/Status-Ausgaben zeigen "bereit / nicht bereit / naechster Schritt" in Alltagssprache. Webhook-Retrys werden sichtbar, ohne den Kernfluss zu blockieren.

**Akzeptanzkriterium:** Ein Nutzer kann erkennen, ob Kurier grundsaetzlich funktioniert, auch wenn n8n oder ein externer Dienst gerade nicht erreichbar ist.

## Risiko 2: Unklare Erfolgskontrolle

**Status:** Erste Haertung umgesetzt.

**Symptom im Alltag:** Nach dem Ablegen einer Datei bleibt offen, ob sie verarbeitet wurde, wo sie liegt und wie sie heisst.

**Gegenmassnahme:** Jede Import-Rueckmeldung beantwortet vier Fragen: Was wurde erkannt? Wie sicher ist Kurier? Wo liegt die Datei? Was kann ich tun, wenn es falsch ist?

**Messsignal:** Erfolgreiche Imports enthalten Kategorie, Ziel, Dateiname und Status. Unsichere Imports erzeugen Review-Hinweise.

**Akzeptanzkriterium:** Nach einem Import muss kein Terminalwissen noetig sein, um den Zustand der Datei zu verstehen.

## Risiko 3: Fehler sind nicht handhabbar genug

**Status:** Erste Haertung umgesetzt.

**Symptom im Alltag:** Eine falsche Kategorie fuehrt zu Nacharbeit, Unsicherheit oder erneutem Auftauchen in der Pruefliste.

**Gegenmassnahme:** Review-Korrekturen muessen schnell sein und danach als bestaetigt gelten. Die Oberflaeche soll Fehlerkorrektur als normalen Teil des Systems behandeln, nicht als Ausnahme.

**Messsignal:** `category_corrected` und `classification_confirmed` zeigen, wie oft Nutzer eingreifen. Wiederkehrende Korrekturen fuer gleiche Kategorien werden priorisiert.

**Akzeptanzkriterium:** Eine falsche Einordnung ist in wenigen Sekunden korrigierbar und taucht nach Bestaetigung nicht wieder als offen auf.

## Risiko 4: Suchqualitaet ist schwer zu vertrauen

**Status:** Erste Haertung umgesetzt.

**Symptom im Alltag:** Die Suche ist manchmal stark, manchmal leer, und der Nutzer weiss nicht warum.

**Gegenmassnahme:** Treffer bekommen kurze Begruendungen. Leere Ergebnisse werden als Produktsignal behandelt, nicht nur als "keine Daten".

**Messsignal:** `search_no_results` zeigt Suchbegriffe, bei denen Kurier nicht geholfen hat. Treffergruende zeigen, ob die Suche nachvollziehbar ist.

**Akzeptanzkriterium:** Bei einer erfolglosen Suche weiss der Nutzer, ob er anders suchen sollte, ob keine passenden Dokumente vorhanden sind oder ob Kurier verbessert werden muss.

## Risiko 5: Zu fruehe technische Optimierung

**Status:** Laufende Produktregel.

**Symptom im Alltag:** Benchmarks, Provider und Integrationen wachsen schneller als der Kernnutzen.

**Gegenmassnahme:** Modell- und Integrationsarbeit wird an Nutzerfragen gekoppelt: schneller finden, sicherer einordnen, klarer korrigieren.

**Messsignal:** Benchmark-Ergebnisse werden nur produktrelevant, wenn sie Import, Suche oder Review messbar verbessern.

**Akzeptanzkriterium:** Jede neue technische Optimierung kann einem echten Alltagsproblem aus dem Beta-Bericht zugeordnet werden.

## Risiko 6: Kein echter Nutzungsrhythmus

**Status:** Noch offen.

**Symptom im Alltag:** Kurier bleibt ein Projekt, das man manchmal testet, statt ein Werkzeug, das man automatisch nutzt.

**Gegenmassnahme:** Der 5-Tage-Test macht Nutzung klein und konkret. Es reicht ein Dokument oder eine Suche pro Tag.

**Messsignal:** Beta-Bericht zeigt echte Signale aus mehreren Tagen statt nur einmalige Demo-Faelle.

**Akzeptanzkriterium:** Nach fuenf Nutzungstagen gibt es mindestens eine klare Entscheidung: weiter haerten, Flow vereinfachen oder ein Risiko zurueckstellen.

## Risiko 7: Setup bleibt zu fragil

**Status:** Teilweise umgesetzt.

**Symptom im Alltag:** Kurier funktioniert nur, wenn man sich an versteckte Dienste, Pfade, Ports oder Befehle erinnert.

**Gegenmassnahme:** `kurier status`, `kurier doctor` und Dashboard muessen den Betriebszustand in normaler Sprache zeigen. Kritische Zusatzdienste werden benannt und mit naechsten Schritten versehen.

**Messsignal:** Status zeigt Dokumentbestand, Suche, Texterkennung und offene Webhook-Auslieferungen. Doctor erklaert fehlende Bausteine ohne rohe Entwicklerbegriffe.

**Akzeptanzkriterium:** Der Nutzer kann den naechsten sinnvollen Schritt erkennen, ohne Logdateien oder Quellcode zu lesen.

## Priorisierung nach dem Beta-Bericht

Nach dem 5-Tage-Test gilt:

1. Datenverlust- oder Vertrauensprobleme zuerst.
2. Danach Korrektur- und Review-Reibung.
3. Danach Suchqualitaet und Treffererklaerung.
4. Danach Setup-/Betriebsruhe.
5. Danach neue Integrationen oder Modelloptimierungen.

Kurier ist erst dann bereit fuer breitere Nutzer, wenn diese Reihenfolge nicht mehr regelmaessig durch Alltagsprobleme unterbrochen wird.

## Naechste Haertungsrunde

1. Fuenf Tage echte Nutzung durchfuehren.
2. Danach `kurier beta report --days 7 --limit 10` auswerten.
3. Die hoechste priorisierte Produktaufgabe als naechsten kleinen Block umsetzen.
4. Erst danach neue Integrationen, Modellwechsel oder groessere Architekturarbeit starten.
