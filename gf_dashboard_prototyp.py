
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="GF Controlling Dashboard – Prototyp",
    page_icon="📊",
    layout="wide",
)

# ---------- Helper ----------
def euro(value: float) -> str:
    return f"{value:,.0f} €".replace(",", "X").replace(".", ",").replace("X", ".")

def pct(value: float) -> str:
    return f"{value:.1f}%".replace(".", ",")

def month_label(value: str) -> str:
    return value if value else "—"

# ---------- Default data ----------
default_rows = pd.DataFrame(
    {
        "Monat": ["Jan 26", "Feb 26", "Mrz 26"],
        "Einnahmen": [124000, 124000, 124000],
        "Gesamtkosten": [90000, 110000, 125000],
        "Liquide Mittel Ende": [99000, 113000, 112000],
        "Offene Verbindlichkeiten": [141505, 135000, 130000],
        "Anfragen": [8, 9, 7],
    }
)

if "rows" not in st.session_state:
    st.session_state.rows = default_rows.copy()

if "current_month" not in st.session_state:
    st.session_state.current_month = "Mrz 26"

if "schueler_gesamt" not in st.session_state:
    st.session_state.schueler_gesamt = 44

if "block_78" not in st.session_state:
    st.session_state.block_78 = 8

if "pk_quote" not in st.session_state:
    st.session_state.pk_quote = 76.6

if "liquiditaetsreichweite" not in st.session_state:
    st.session_state.liquiditaetsreichweite = 0.9

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .main-title {
        background: #1f5a91;
        color: white;
        padding: 14px 18px;
        border-radius: 10px;
        text-align: center;
        font-size: 34px;
        font-weight: 700;
        margin-bottom: 18px;
    }
    .kpi-card {
        border: 1px solid #d0d7de;
        border-radius: 10px;
        overflow: hidden;
        background: white;
        box-shadow: 0 1px 4px rgba(0,0,0,.04);
    }
    .kpi-head {
        background: #2f73b3;
        color: white;
        font-weight: 700;
        text-align: center;
        padding: 8px 10px;
        font-size: 16px;
    }
    .kpi-body {
        padding: 18px 10px;
        text-align: center;
        font-size: 22px;
        font-weight: 700;
    }
    .small-note {
        color: #6b7280;
        font-size: 13px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">GF Controlling Dashboard – Waldorfschule Villach</div>', unsafe_allow_html=True)

# ---------- Input area ----------
with st.expander("Eingabefelder / Testdaten", expanded=True):
    left, right = st.columns([1, 2])

    with left:
        st.markdown("### KPI-Eingaben")
        st.session_state.current_month = st.text_input("Aktueller Monat", value=st.session_state.current_month)
        st.session_state.schueler_gesamt = st.number_input("Schüler gesamt", min_value=0, value=int(st.session_state.schueler_gesamt), step=1)
        st.session_state.block_78 = st.number_input("Block 7/8", min_value=0, value=int(st.session_state.block_78), step=1)
        st.session_state.pk_quote = st.number_input("PK-Quote (%)", min_value=0.0, max_value=300.0, value=float(st.session_state.pk_quote), step=0.1)
        st.session_state.liquiditaetsreichweite = st.number_input("Liquiditätsreichweite", min_value=0.0, value=float(st.session_state.liquiditaetsreichweite), step=0.1)

    with right:
        st.markdown("### Monatsdaten")
        edited = st.data_editor(
            st.session_state.rows,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "Monat": st.column_config.TextColumn("Monat"),
                "Einnahmen": st.column_config.NumberColumn("Einnahmen", format="%d €"),
                "Gesamtkosten": st.column_config.NumberColumn("Gesamtkosten", format="%d €"),
                "Liquide Mittel Ende": st.column_config.NumberColumn("Liquide Mittel Ende", format="%d €"),
                "Offene Verbindlichkeiten": st.column_config.NumberColumn("Offene Verbindlichkeiten", format="%d €"),
                "Anfragen": st.column_config.NumberColumn("Anfragen", format="%d"),
            },
            key="editor_rows",
        )
        st.session_state.rows = pd.DataFrame(edited)

rows = st.session_state.rows.copy()

# ---------- Derived values ----------
if rows.empty:
    current_result = 0
    current_liquidity_end = 0
    current_liabilities = 0
    current_requests = 0
else:
    latest = rows.iloc[-1]
    current_result = float(latest["Einnahmen"]) - float(latest["Gesamtkosten"])
    current_liquidity_end = float(latest["Liquide Mittel Ende"])
    current_liabilities = float(latest["Offene Verbindlichkeiten"])
    current_requests = int(latest["Anfragen"])

# ---------- KPI cards ----------
c1, c2, c3, c4 = st.columns(4)
cards = [
    ("Aktueller Monat", month_label(st.session_state.current_month)),
    ("Operatives Ergebnis", euro(current_result)),
    ("PK-Quote", pct(st.session_state.pk_quote)),
    ("Liquiditätsreichweite*", f"{st.session_state.liquiditaetsreichweite:.1f}".replace(".", ",")),
]
for col, (title, value) in zip([c1, c2, c3, c4], cards):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-head">{title}</div>
                <div class="kpi-body">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

c5, c6, c7, c8 = st.columns(4)
cards_2 = [
    ("Schüler gesamt", f"{int(st.session_state.schueler_gesamt)}"),
    ("Block 7/8", f"{int(st.session_state.block_78)}"),
    ("Offene Verbindlichkeiten", euro(current_liabilities)),
    ("Schulanfragen", f"{int(current_requests)}"),
]
for col, (title, value) in zip([c5, c6, c7, c8], cards_2):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-head">{title}</div>
                <div class="kpi-body">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.caption("* letzter verfügbarer Liquiditätswert")

# ---------- Tables + chart ----------
left, center, right = st.columns([1.1, 1.1, 1.8])

with left:
    st.markdown("#### Einnahmen / Kosten / Ergebnis")
    tbl = rows[["Monat", "Einnahmen", "Gesamtkosten"]].copy()
    tbl["Ergebnis"] = tbl["Einnahmen"] - tbl["Gesamtkosten"]
    st.dataframe(tbl, use_container_width=True, hide_index=True)

with center:
    st.markdown("#### Liquidität / Verbindlichkeiten")
    tbl2 = rows[["Monat", "Liquide Mittel Ende", "Offene Verbindlichkeiten"]].copy()
    st.dataframe(tbl2, use_container_width=True, hide_index=True)

with right:
    st.markdown("#### Einnahmen vs. Gesamtkosten")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rows["Monat"],
        y=rows["Einnahmen"],
        mode="lines+markers",
        name="Einnahmen",
    ))
    fig.add_trace(go.Scatter(
        x=rows["Monat"],
        y=rows["Gesamtkosten"],
        mode="lines+markers",
        name="Gesamtkosten",
    ))
    fig.update_layout(
        height=360,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        yaxis_title=None,
        xaxis_title=None,
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.markdown("### Was dieser Prototyp verifiziert")
st.markdown(
    """
    - **Machbarkeit:** KPI-Kacheln, Eingabefelder, Tabellen und Chart lassen sich in Python schnell als Weboberfläche abbilden.  
    - **Usability:** Daten werden nur einmal eingegeben und aktualisieren die Ansicht sofort.  
    - **Performance:** Für diesen Umfang reagiert die Oberfläche in der Regel sehr schnell.  
    - **Nächster Schritt:** Bei positiver Bewertung kann daraus eine echte browserbasierte Anwendung mit Login, Datenbank und Mehrbenutzerbetrieb entstehen.
    """
)
