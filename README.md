# Spritpreis Dashboard – Deutschland Live

Einfaches, lokales Web-Dashboard für **tagesaktuelle Spritpreise** (Bundesdurchschnitt) in Deutschland.

- **Super E5**, **E10** und **Diesel**
- Live-Daten von [benzinpreis-aktuell.de](https://www.benzinpreis-aktuell.de/api.v2.php?data=nationwide)
- Kein API-Key, keine Registrierung, keine Werbung
- Automatisches Update alle 15 Minuten
- Lokale Historie (JSON) → Wochen-, Monats- und Langzeit-Trend
- Schöne interaktive Plotly-Charts mit Trendlinien
- Dark / Light Mode per Button
- CSV-Export der gesamten Historie

## Vorschau

*(Hier kommt bald ein Screenshot – am besten ein 3-Tab-Ansicht mit Preisen und Charts)*

## Features

- Aktuelle Preise (Bundesdurchschnitt) groß dargestellt
- Tabs: Letzte 7 Tage · Letzte 30 Tage · Gesamtverlauf (mit Monatsaggregation)
- Lineare Trendlinien in allen Charts
- Dark/Light-Toggle
- Benachrichtigungen bei Update / Fehler
- Automatischer Start im Browser

## Installation

```bash
# 1. Abhängigkeiten installieren (am besten in virtualenv)
pip install nicegui plotly requests

# 2. Repository clonen oder nur die Datei sprit_dashboard.py speichern
git clone https://github.com/deinusername/spritpreis-dashboard-nicegui.git
cd spritpreis-dashboard-nicegui
