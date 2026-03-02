from datetime import date, timedelta
import json
import requests
from nicegui import ui
import plotly.graph_objects as go
import csv
from io import StringIO

HISTORY_FILE = "sprit_history.json"
API_URL = "https://www.benzinpreis-aktuell.de/api.v2.php?data=nationwide"

# Globale Variable für Dark/Light-Modus (wird vom Toggle-Button gesteuert)
dark_mode = True

def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return sorted(data, key=lambda x: x["date"])
    except FileNotFoundError:
        sample = [
            {"date": "2026-01-01", "super": 1.732, "e10": 1.688, "diesel": 1.645},
            {"date": "2026-02-01", "super": 1.812, "e10": 1.758, "diesel": 1.712},
            {"date": (date.today() - timedelta(days=1)).isoformat(), "super": 1.895, "e10": 1.845, "diesel": 1.815},
        ]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
        return sample

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def fetch_current():
    try:
        r = requests.get(API_URL, timeout=10)
        r.raise_for_status()
        data = r.json()
        today = data["date"][:10]  # nur YYYY-MM-DD
        return {
            "date": today,
            "super": float(data["super"]),
            "e10": float(data["e10"]),
            "diesel": float(data["diesel"]),
        }
    except Exception as e:
        ui.notify(f"API-Fehler → Fallback-Werte ({e})", type="warning")
        return {
            "date": date.today().isoformat(),
            "super": 1.900,
            "e10": 1.850,
            "diesel": 1.820,
        }

def update_history():
    current = fetch_current()
    history = load_history()
    today = current["date"]

    updated = False
    for entry in history:
        if entry["date"] == today:
            if (entry["super"] != current["super"] or
                entry["e10"] != current["e10"] or
                entry["diesel"] != current["diesel"]):
                entry.update(current)
                updated = True
            break
    else:
        history.append(current)
        updated = True

    if updated:
        cutoff = (date.today() - timedelta(days=730)).isoformat()
        history = [e for e in history if e["date"] >= cutoff]
        save_history(history)
        ui.notify(f"{today} aktualisiert & gespeichert", type="positive")
    else:
        ui.notify(f"{today} – keine Preisänderung", type="info")

    refresh_charts(history)

def auto_refresh():
    update_history()

def export_csv():
    history = load_history()
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["date", "super", "e10", "diesel"])
    writer.writeheader()
    writer.writerows(history)
    ui.download(
        content=output.getvalue().encode("utf-8"),
        filename=f"spritpreise_{date.today().isoformat()}.csv"
    )

def create_chart(history, days, title):
    if not history:
        return go.Figure()

    recent = history[-days:] if days else history
    dates = [d["date"] for d in recent]
    super_p = [d["super"] for d in recent]
    e10_p = [d["e10"] for d in recent]
    diesel_p = [d["diesel"] for d in recent]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=super_p, name="Super", line=dict(color="#1f77b4")))
    fig.add_trace(go.Scatter(x=dates, y=e10_p, name="E10", line=dict(color="#ff7f0e")))
    fig.add_trace(go.Scatter(x=dates, y=diesel_p, name="Diesel", line=dict(color="#2ca02c")))

    fig.update_layout(
        title=title,
        xaxis_title="Datum",
        yaxis_title="€ / Liter",
        hovermode="x unified",
        height=480,
        template="plotly_dark" if dark_mode else "plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def refresh_charts(history=None):
    if history is None:
        history = load_history()

    chart1.figure = create_chart(history, 7,   "Letzte 7 Tage")
    chart2.figure = create_chart(history, 30,  "Letzte 30 Tage")
    chart3.figure = create_chart(history, None, "Gesamthistorie")

    if history:
        latest = history[-1]
        lbl_super.text = f"Super:   {latest['super']:.3f} €"
        lbl_e10.text   = f"E10:     {latest['e10']:.3f} €"
        lbl_diesel.text = f"Diesel:  {latest['diesel']:.3f} €"

def toggle_dark_mode():
    global dark_mode
    dark_mode = not dark_mode
    ui.notify(f"Dark Mode: {'AN' if dark_mode else 'AUS'}", type="info")
    refresh_charts()

# ──────────────────────────────────────────────── UI ────────────────────────────────────────────────

ui.label("Spritpreise Deutschland – Bundesdurchschnitt").classes("text-2xl font-bold text-center mt-6")
ui.label("Quelle: benzinpreis-aktuell.de • Auto-Update alle 15 Min").classes("text-center text-gray-500 mb-4")

# Aktuelle Preise Card
with ui.card().classes("w-full max-w-md mx-auto shadow-xl"):
    ui.label("Aktuelle Preise").classes("text-xl font-semibold text-center mb-3")
    lbl_super  = ui.label("Super:   -- €").classes("text-2xl font-mono")
    lbl_e10    = ui.label("E10:     -- €").classes("text-2xl font-mono")
    lbl_diesel = ui.label("Diesel:  -- €").classes("text-2xl font-mono")

    with ui.row().classes("justify-center gap-4 mt-6"):
        ui.button("Jetzt aktualisieren", on_click=update_history, icon="refresh") \
            .props("color=green flat")
        ui.button("Dark/Light", on_click=toggle_dark_mode, icon="brightness_6") \
            .props("color=primary flat")

ui.separator().classes("my-6")

# Charts + Export
with ui.row().classes("justify-center gap-4 mb-4"):
    ui.button("CSV exportieren", on_click=export_csv, icon="download") \
        .props("color=blue flat outline")

with ui.tabs().classes("w-full max-w-5xl mx-auto"):
    with ui.tab("7 Tage"):
        chart1 = ui.plotly(go.Figure()).classes("w-full")
    with ui.tab("30 Tage"):
        chart2 = ui.plotly(go.Figure()).classes("w-full")
    with ui.tab("Gesamt"):
        chart3 = ui.plotly(go.Figure()).classes("w-full")

# ──────────────────────────────────────────────── Start ────────────────────────────────────────────────

history = load_history()
refresh_charts(history)

# Auto-Refresh alle 15 Minuten
ui.timer(900, auto_refresh)

ui.run(
    title="Spritpreise DE Live",
    port=8080,
    dark=dark_mode,
    reload=True,
    show_welcome_message=False
)