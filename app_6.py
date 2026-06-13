# =============================================================
#  Gas Lift Design Tool  -  Control-Room Edition
#  Petroleum Engineering | Artificial Lift - Chapter 3
#  Single file. No plotly. Uses Altair (bundled with Streamlit).
# =============================================================

import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(page_title="Gas Lift Design", page_icon="🛢️", layout="wide")

# ------------------------------------------------------------------
#  THEME  (control-room instrument panel:
#          amber = produced fluid/oil, cyan = injected gas)
# ------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Saira+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap');

:root{
  --bg:#0E1822; --surface:#16242F; --surface-2:#1C2E3A;
  --line:#243845; --line-soft:#182530;
  --amber:#E8A23D; --amber-soft:#F2C879; --cyan:#4FB6C4;
  --text:#EDE6DB; --muted:#8298A4;
}

.stApp{
  background:
    radial-gradient(1100px 560px at 82% -12%, rgba(79,182,196,.07), transparent 60%),
    radial-gradient(900px 520px at -10% 112%, rgba(232,162,61,.07), transparent 60%),
    var(--bg);
  color:var(--text);
  font-family:'IBM Plex Sans',sans-serif;
}
header[data-testid="stHeader"]{ background:transparent; }

section[data-testid="stSidebar"]{ background:var(--surface); border-right:1px solid var(--line); }
section[data-testid="stSidebar"] *{ color:var(--text); }
section[data-testid="stSidebar"] h2{
  font-family:'Saira Condensed',sans-serif!important; text-transform:uppercase;
  letter-spacing:1.5px; font-size:18px; color:var(--amber);
}

h1,h2,h3{ font-family:'Saira Condensed',sans-serif!important; letter-spacing:.5px; }

/* ---- Nameplate header ---- */
.nameplate{
  display:flex; align-items:center; gap:18px; padding:22px 26px; margin-bottom:8px;
  background:linear-gradient(135deg,var(--surface-2),var(--surface));
  border:1px solid var(--line); border-radius:14px; position:relative; overflow:hidden;
}
.nameplate::after{ content:""; position:absolute; left:0; right:0; bottom:0; height:3px;
  background:linear-gradient(90deg,var(--amber),var(--cyan)); }
.nameplate .mono{
  width:56px; height:56px; border-radius:12px; flex:none;
  display:flex; align-items:center; justify-content:center;
  background:#0E1822; border:1px solid var(--line);
  font-family:'Saira Condensed'; font-weight:700; font-size:24px; color:var(--amber);
}
.nameplate h1{ margin:0; font-size:36px; font-weight:700; text-transform:uppercase; line-height:1; }
.nameplate .sub{ color:var(--muted); font-size:13px; margin-top:4px; }
.chip{ margin-left:auto; font-family:'IBM Plex Mono'; font-size:11px; color:var(--cyan);
  border:1px solid var(--line); padding:7px 13px; border-radius:999px;
  text-transform:uppercase; letter-spacing:1.5px; white-space:nowrap; }

/* ---- Gauge / metric cards ---- */
.gauge-row{ display:flex; gap:16px; flex-wrap:wrap; margin:18px 0 6px; }
.gauge{ flex:1; min-width:170px; background:var(--surface); border:1px solid var(--line);
  border-radius:12px; padding:16px 18px 18px; position:relative; overflow:hidden; }
.gauge::before{ content:""; position:absolute; top:0; left:0; width:100%; height:3px; background:var(--accent); }
.gauge .label{ font-size:11px; text-transform:uppercase; letter-spacing:1.5px; color:var(--muted); }
.gauge .value{ font-family:'IBM Plex Mono'; font-size:30px; font-weight:600; color:var(--text);
  margin-top:8px; line-height:1; }
.gauge .unit{ font-family:'IBM Plex Sans'; font-size:13px; color:var(--muted); margin-left:5px; }

/* ---- Section label ---- */
.eyebrow{ font-family:'IBM Plex Mono'; font-size:11px; letter-spacing:2px; text-transform:uppercase;
  color:var(--cyan); margin:26px 0 2px; }

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"]{ gap:4px; border-bottom:1px solid var(--line); }
.stTabs [data-baseweb="tab"]{ font-family:'Saira Condensed'; text-transform:uppercase;
  letter-spacing:1.2px; font-size:15px; color:var(--muted); }
.stTabs [aria-selected="true"]{ color:var(--amber)!important; }
.stTabs [data-baseweb="tab-highlight"]{ background:var(--amber)!important; }

/* ---- Custom table ---- */
.vtable{ width:100%; border-collapse:collapse; margin-top:6px; }
.vtable th{ text-align:right; color:var(--muted); text-transform:uppercase; font-size:10.5px;
  letter-spacing:1.2px; font-family:'IBM Plex Sans'; padding:10px 16px; border-bottom:1px solid var(--line); }
.vtable th:first-child{ text-align:left; }
.vtable td{ padding:12px 16px; border-bottom:1px solid var(--line-soft); color:var(--text);
  font-family:'IBM Plex Mono'; font-size:13.5px; text-align:right; }
.vtable td:first-child{ text-align:left; font-family:'IBM Plex Sans'; color:var(--muted); }
.vtable tbody tr:hover{ background:var(--surface-2); }
.vtable tbody tr:last-child td{ color:var(--amber); font-weight:600; }
.vtable tbody tr:last-child td:first-child{ color:var(--amber); }

/* ---- Buttons ---- */
.stDownloadButton button, .stButton button{
  background:var(--amber); color:#0E1822; border:none; padding:9px 18px;
  font-family:'Saira Condensed'; font-weight:600; text-transform:uppercase;
  letter-spacing:1px; border-radius:8px; }
.stDownloadButton button:hover, .stButton button:hover{ background:var(--amber-soft); color:#0E1822; }

.foot{ color:var(--muted); font-family:'IBM Plex Mono'; font-size:11px; letter-spacing:.5px;
  text-align:center; margin-top:34px; padding-top:14px; border-top:1px solid var(--line-soft); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ------------------------------------------------------------------
#  CORE ENGINEERING LOGIC  (Analytical Method, Chapter 3)
# ------------------------------------------------------------------
def design_gas_lift(Pko, Pso, Pwh, Gs, Gu, dP, min_spacing,
                    inj_depth, well_depth, Psurf_first, Psurf_rest):
    valves = []
    DV1 = (Pko - 50 - Psurf_first) / Gs
    valves.append({"Valve": "V1 (Top)", "Depth (ft)": round(DV1, 1),
                   "Surface Op. Pressure (psi)": round(Pso, 1),
                   "Spacing from previous (ft)": round(DV1, 1)})
    Pso_n, DV_prev, n = Pso, DV1, 1
    while True:
        Pso_n = Pso_n - dP
        increment = (Pso_n - Gu * DV_prev - Psurf_rest) / Gs
        DV_new = DV_prev + increment
        if DV_new >= inj_depth or increment < min_spacing:
            break
        n += 1
        valves.append({"Valve": f"V{n}", "Depth (ft)": round(DV_new, 1),
                       "Surface Op. Pressure (psi)": round(Pso_n, 1),
                       "Spacing from previous (ft)": round(increment, 1)})
        DV_prev = DV_new
    valves.append({"Valve": "Operating", "Depth (ft)": round(inj_depth, 1),
                   "Surface Op. Pressure (psi)": round(Pso_n, 1),
                   "Spacing from previous (ft)": round(inj_depth - DV_prev, 1)})
    df = pd.DataFrame(valves)
    return df, {"n_valves": len(df), "n_unloading": len(df) - 1, "deepest_unloading": DV_prev}


def gas_volume_required(glr_inj, inj_depth, q):
    return glr_inj * (inj_depth / 1000.0) * q


def injection_pressure_at_depth(Ps_psig, gamma_g, L, T_avg_R, Z):
    Ps_psia = Ps_psig + 14.7
    PL_psia = Ps_psia * np.exp((gamma_g * L) / (53.34 * T_avg_R * Z))
    return PL_psia - 14.7

# ------------------------------------------------------------------
#  SIDEBAR : INPUTS
# ------------------------------------------------------------------
st.sidebar.header("Well & Design Inputs")

with st.sidebar.expander("Well Data", expanded=True):
    well_depth = st.number_input("Well depth (ft)", value=5000.0, min_value=100.0, step=100.0)
    q = st.number_input("Design flow rate, q (bbl/d)", value=1200.0, min_value=1.0, step=50.0)
    wc = st.number_input("Water cut (%)", value=80.0, min_value=0.0, max_value=100.0, step=5.0)
    inj_depth = st.number_input("Gas injection depth (ft)", value=3921.0, min_value=100.0, step=50.0)

with st.sidebar.expander("Pressures", expanded=True):
    Pko = st.number_input("Kick-off pressure, Pko (psi)", value=900.0, min_value=0.0, step=10.0)
    Pso = st.number_input("Surface operating pressure, Pso (psi)", value=850.0, min_value=0.0, step=10.0)
    Pwh = st.number_input("Wellhead pressure, Pwh (psi)", value=200.0, min_value=0.0, step=10.0)

with st.sidebar.expander("Gradients & Valves", expanded=True):
    Gs = st.number_input("Kill-fluid gradient, Gs (psi/ft)", value=0.5, min_value=0.001, step=0.01, format="%.3f")
    Gu = st.number_input("Design unloading gradient, Gu (psi/ft)", value=0.125, min_value=0.001, step=0.005, format="%.3f")
    dP = st.number_input("Valve pressure drop, dP (psi/valve)", value=25.0, min_value=1.0, step=5.0)
    min_spacing = st.number_input("Minimum valve spacing (ft)", value=250.0, min_value=10.0, step=10.0)

with st.sidebar.expander("Unloading Method"):
    unload = st.selectbox("Where is the well unloaded?",
                          ["Pit (first valve only)", "Wellhead", "Separator"])
    Psep = 0.0
    if unload == "Separator":
        Psep = st.number_input("Separator pressure, Psep (psi)", value=100.0, min_value=0.0, step=10.0)

with st.sidebar.expander("Gas Properties"):
    glr_inj = st.slider("Injection GLR (scf/bbl per 1000 ft)", 150, 250, 200, step=10)
    gamma_g = st.number_input("Gas relative density, gamma_g", value=0.65, min_value=0.55, max_value=1.2, step=0.01)
    T_avg_F = st.number_input("Average flowing temperature (degF)", value=140.0, step=5.0)
    Z = st.number_input("Gas compressibility factor, Z", value=0.90, min_value=0.5, max_value=1.2, step=0.01)

if unload == "Pit (first valve only)":
    Psurf_first, Psurf_rest = 0.0, Pwh
elif unload == "Wellhead":
    Psurf_first, Psurf_rest = Pwh, Pwh
else:
    Psurf_first, Psurf_rest = Psep, Psep

# ------------------------------------------------------------------
#  HEADER
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="nameplate">
      <div class="mono">GL</div>
      <div>
        <h1>Gas Lift Design</h1>
        <div class="sub">Continuous-flow unloading valve spacing, depths, gas volume &amp; injection pressure</div>
      </div>
      <div class="chip">Continuous · Balanced Valve · Analytical</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------
#  VALIDATION
# ------------------------------------------------------------------
errors = []
if Pso >= Pko:
    errors.append("Surface operating pressure (Pso) must be lower than kick-off pressure (Pko).")
if Gu >= Gs:
    errors.append("Unloading gradient (Gu) must be smaller than kill-fluid gradient (Gs).")
if inj_depth > well_depth:
    errors.append("Injection depth cannot be deeper than the well depth.")
if errors:
    for e in errors:
        st.error(e)
    st.stop()

# ------------------------------------------------------------------
#  CALCULATE
# ------------------------------------------------------------------
df, res = design_gas_lift(Pko, Pso, Pwh, Gs, Gu, dP, min_spacing,
                          inj_depth, well_depth, Psurf_first, Psurf_rest)
T_avg_R = T_avg_F + 460.0
Vg = gas_volume_required(glr_inj, inj_depth, q)
PL = injection_pressure_at_depth(Pso, gamma_g, inj_depth, T_avg_R, Z)

# ------------------------------------------------------------------
#  GAUGES
# ------------------------------------------------------------------
def gauge(label, value, unit, accent):
    u = f'<span class="unit">{unit}</span>' if unit else ""
    return (f'<div class="gauge" style="--accent:{accent}">'
            f'<div class="label">{label}</div>'
            f'<div class="value">{value}{u}</div></div>')

cards = "".join([
    gauge("Total Valves", res["n_valves"], "", "#4FB6C4"),
    gauge("Unloading Valves", res["n_unloading"], "", "#4FB6C4"),
    gauge("Gas Volume", f"{Vg/1e6:.2f}", "MMscf/d", "#E8A23D"),
    gauge("Inj. Pressure @ Depth", f"{PL:,.0f}", "psi", "#E8A23D"),
])
st.markdown(f'<div class="gauge-row">{cards}</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
#  TABS
# ------------------------------------------------------------------
tab1, tab2 = st.tabs(["Valve Schedule", "Well Diagram"])

with tab1:
    st.markdown('<div class="eyebrow">Valve placement from surface to injection point</div>',
                unsafe_allow_html=True)
    head = "".join(f"<th>{c}</th>" for c in df.columns)
    body = ""
    for _, r in df.iterrows():
        cells = "".join(f"<td>{r[c]}</td>" for c in df.columns)
        body += f"<tr>{cells}</tr>"
    st.markdown(f'<table class="vtable"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>',
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "valve_schedule.csv", "text/csv")

with tab2:
    st.markdown('<div class="eyebrow">Pressure vs depth — gradients and valve positions</div>',
                unsafe_allow_html=True)
    depths = np.linspace(0, well_depth, 60)
    line_df = pd.DataFrame({
        "Depth (ft)": np.concatenate([depths, depths]),
        "Pressure (psi)": np.concatenate([Psurf_rest + Gs * depths, Pso + 0.03 * depths]),
        "Line": (["Produced-fluid gradient"] * len(depths) + ["Gas injection pressure"] * len(depths)),
    })
    ay = alt.Y("Depth (ft):Q", scale=alt.Scale(reverse=True))
    lines = alt.Chart(line_df).mark_line(strokeWidth=2.5).encode(
        x=alt.X("Pressure (psi):Q"), y=ay,
        color=alt.Color("Line:N",
            scale=alt.Scale(domain=["Produced-fluid gradient", "Gas injection pressure"],
                            range=["#E8A23D", "#4FB6C4"]),
            legend=alt.Legend(orient="top", title=None)))
    vp = df.rename(columns={"Surface Op. Pressure (psi)": "Pressure (psi)"})
    points = alt.Chart(vp).mark_point(size=180, shape="triangle-down", filled=True,
            color="#F2C879", stroke="#0E1822", strokeWidth=1.2).encode(
        x="Pressure (psi):Q", y=ay, tooltip=["Valve", "Depth (ft)", "Pressure (psi)"])
    labels = alt.Chart(vp).mark_text(align="left", dx=12, fontSize=12, color="#EDE6DB").encode(
        x="Pressure (psi):Q", y=ay, text="Valve")
    chart = (alt.layer(lines, points, labels)
             .properties(height=620, background="transparent")
             .configure_axis(labelColor="#8298A4", titleColor="#EDE6DB",
                             gridColor="#1A2A35", domainColor="#33454F")
             .configure_legend(labelColor="#EDE6DB", titleColor="#8298A4")
             .configure_view(strokeWidth=0))
    st.altair_chart(chart, use_container_width=True)

with st.expander("About & Verification (Example 4)"):
    st.markdown(
        "**Default values reproduce textbook Example 4** (Chapter 3): "
        "Well 5,000 ft · q = 1,200 BOPD · WC 80% · Injection depth 3,921 ft · "
        "Min spacing 250 ft · Balanced valve dP 25 psi · unloaded to pit (first valve). "
        "Use this case to demonstrate calculation accuracy against the manual hand-solution.\n\n"
        "**Equations (Analytical Method):**\n"
        "- First valve:  DV1 = (Pko - 50 - Psurf) / Gs\n"
        "- Next valves:  DVn+1 = DVn + (Pso_n - Gu*DVn - Psurf) / Gs\n"
        "- Gas volume:   Vg = GLR_inj x (D_inj / 1000) x q\n"
        "- Inj. pressure: PL = Ps * exp(gamma_g*L / (53.34*Tavg*Z))"
    )

st.markdown('<div class="foot">Continuous Gas Lift Design · Artificial Lift Chapter 3 · '
            'amber = produced fluid · cyan = injected gas</div>', unsafe_allow_html=True)
