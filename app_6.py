# =============================================================
#  Gas Lift Design Tool  -  "Bold Cream & Yellow" edition
#  Petroleum Engineering | Artificial Lift - Chapter 3
#  Single file. No plotly. Uses Altair (bundled with Streamlit).
# =============================================================

import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(page_title="Gas Lift Design", page_icon="🛢️", layout="wide")

# ------------------------------------------------------------------
#  THEME
# ------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600&display=swap');

:root{
  --bg:#F1EDE4; --card:#FFFFFF; --ink:#161616; --ink-soft:#5A554C;
  --yellow:#FFD60A; --yellow-soft:#FFE765; --grid:#E3DDD0; --hair:#E7E1D4;
}

.stApp{ background:var(--bg); color:var(--ink); font-family:'Inter',sans-serif; }
header[data-testid="stHeader"]{ background:transparent; }

h1,h2,h3{ font-family:'Archivo',sans-serif!important; color:var(--ink); }

/* sidebar */
section[data-testid="stSidebar"]{ background:var(--card); border-right:2px solid var(--ink); }
section[data-testid="stSidebar"] h2{
  font-family:'Archivo',sans-serif!important; text-transform:uppercase;
  letter-spacing:1px; font-weight:800; font-size:18px; color:var(--ink); }
section[data-testid="stSidebar"] label{ color:var(--ink-soft)!important; font-weight:500; }

.hl{ background:linear-gradient(transparent 55%, var(--yellow) 55%); padding:0 3px; }

/* ---- Nameplate ---- */
.nameplate{ display:flex; align-items:center; gap:22px; padding:26px 30px; margin-bottom:0;
  background:var(--card); border:2px solid var(--ink); border-radius:18px; }
.nameplate .mono{ width:64px; height:64px; border-radius:50%; flex:none;
  background:var(--yellow); border:2px solid var(--ink);
  display:flex; align-items:center; justify-content:center;
  font-family:'Archivo'; font-weight:900; font-size:25px; color:var(--ink); }
.nameplate h1{ margin:0; font-size:38px; font-weight:800; text-transform:uppercase; line-height:1.02; }
.nameplate .sub{ color:var(--ink-soft); font-size:13.5px; margin-top:7px; font-weight:500; }

/* ---- Black marquee strip (signature, from reference) ---- */
.marquee{ background:var(--ink); color:#fff; border-radius:12px; padding:13px 22px; margin:14px 0 4px;
  display:flex; flex-wrap:wrap; gap:16px; align-items:center; justify-content:center;
  font-family:'Archivo'; font-weight:600; text-transform:uppercase; letter-spacing:1.5px; font-size:12.5px; }
.marquee .star{ color:var(--yellow); }

/* ---- Eyebrow ---- */
.eyebrow{ font-family:'Archivo'; font-weight:700; font-size:12px; letter-spacing:1.5px;
  text-transform:uppercase; color:var(--ink-soft); margin:26px 0 6px; }
.eyebrow .star{ color:var(--yellow); margin-right:7px; }

/* ---- Gauge cards ---- */
.gauge-row{ display:flex; gap:16px; flex-wrap:wrap; margin:6px 0; }
.gauge{ flex:1; min-width:175px; background:var(--card); border:2px solid var(--ink);
  border-radius:16px; padding:18px 20px; position:relative; }
.gauge.solid{ background:var(--yellow); }
.gauge .star{ position:absolute; top:15px; right:17px; color:var(--yellow); font-size:15px; }
.gauge.solid .star{ color:var(--ink); }
.gauge .label{ font-size:11.5px; text-transform:uppercase; letter-spacing:1px; color:var(--ink-soft); font-weight:600; }
.gauge.solid .label{ color:var(--ink); }
.gauge .value{ font-family:'Archivo'; font-weight:800; font-size:34px; color:var(--ink);
  margin-top:10px; line-height:1; font-variant-numeric:tabular-nums; }
.gauge .unit{ font-family:'Inter'; font-weight:500; font-size:13px; color:var(--ink-soft); margin-left:5px; }

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"]{ gap:8px; border-bottom:2px solid var(--ink); }
.stTabs [data-baseweb="tab"]{ font-family:'Archivo'; font-weight:700; text-transform:uppercase;
  letter-spacing:1px; font-size:15px; color:var(--ink-soft); }
.stTabs [aria-selected="true"]{ color:var(--ink)!important; }
.stTabs [data-baseweb="tab-highlight"]{ background:var(--yellow)!important; height:3px; }

/* ---- Table ---- */
.tablewrap{ border:2px solid var(--ink); border-radius:14px; overflow:hidden; background:var(--card); margin-top:4px; }
.vtable{ width:100%; border-collapse:collapse; }
.vtable th{ background:var(--ink); color:#fff; text-transform:uppercase; font-size:11px;
  letter-spacing:1px; font-family:'Archivo'; font-weight:700; padding:13px 16px; text-align:right; }
.vtable th:first-child{ text-align:left; }
.vtable td{ padding:13px 16px; border-bottom:1px solid var(--hair); font-family:'Inter';
  font-weight:500; font-size:14px; text-align:right; color:var(--ink); font-variant-numeric:tabular-nums; }
.vtable td:first-child{ text-align:left; font-weight:600; }
.vtable tbody tr:hover td{ background:#FBF7EC; }
.vtable tbody tr:last-child td{ background:var(--yellow); font-weight:700; }
.vtable tbody tr:last-child:hover td{ background:var(--yellow); }

/* ---- Buttons (yellow pill) ---- */
.stDownloadButton button, .stButton button{
  background:var(--yellow)!important; color:var(--ink)!important; border:2px solid var(--ink)!important;
  border-radius:999px!important; font-family:'Archivo'; font-weight:700; text-transform:uppercase;
  letter-spacing:1px; padding:8px 24px!important; }
.stDownloadButton button:hover, .stButton button:hover{ background:var(--ink)!important; color:#fff!important; }

/* ---- Footer (black, from reference) ---- */
.foot{ background:var(--ink); color:#fff; border-radius:16px; padding:22px; margin-top:34px;
  text-align:center; font-family:'Archivo'; font-weight:600; text-transform:uppercase;
  letter-spacing:1.5px; font-size:11.5px; }
.foot .star{ color:var(--yellow); margin:0 8px; }
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
#  HEADER + MARQUEE
# ------------------------------------------------------------------
st.markdown(
    """
    <div class="nameplate">
      <div class="mono">GL</div>
      <div>
        <h1>Gas <span class="hl">Lift</span> Design</h1>
        <div class="sub">Continuous-flow unloading valve spacing, depths, gas volume &amp; injection pressure</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(
    '<div class="marquee">'
    '<span>Continuous Flow</span><span class="star">&#10038;</span>'
    '<span>Balanced Valve</span><span class="star">&#10038;</span>'
    '<span>Analytical Method</span><span class="star">&#10038;</span>'
    '<span>Unloading Design</span>'
    '</div>', unsafe_allow_html=True)

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
st.markdown('<div class="eyebrow"><span class="star">&#10038;</span>Design Output</div>',
            unsafe_allow_html=True)

def gauge(label, value, unit, solid=False):
    cls = "gauge solid" if solid else "gauge"
    u = f'<span class="unit">{unit}</span>' if unit else ""
    return (f'<div class="{cls}"><span class="star">&#10038;</span>'
            f'<div class="label">{label}</div>'
            f'<div class="value">{value}{u}</div></div>')

cards = "".join([
    gauge("Total Valves", res["n_valves"], "", solid=True),
    gauge("Unloading Valves", res["n_unloading"], ""),
    gauge("Gas Volume", f"{Vg/1e6:.2f}", "MMscf/d"),
    gauge("Inj. Pressure @ Depth", f"{PL:,.0f}", "psi"),
])
st.markdown(f'<div class="gauge-row">{cards}</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
#  TABS
# ------------------------------------------------------------------
tab1, tab2 = st.tabs(["Valve Schedule", "Well Diagram"])

with tab1:
    st.markdown('<div class="eyebrow"><span class="star">&#10038;</span>'
                'Valve placement from surface to injection point</div>', unsafe_allow_html=True)
    head = "".join(f"<th>{c}</th>" for c in df.columns)
    body = ""
    for _, r in df.iterrows():
        cells = "".join(f"<td>{r[c]}</td>" for c in df.columns)
        body += f"<tr>{cells}</tr>"
    st.markdown(f'<div class="tablewrap"><table class="vtable">'
                f'<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>',
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "valve_schedule.csv", "text/csv")

with tab2:
    st.markdown('<div class="eyebrow"><span class="star">&#10038;</span>'
                'Pressure vs depth - gradients and valve positions</div>', unsafe_allow_html=True)
    depths = np.linspace(0, well_depth, 60)
    line_df = pd.DataFrame({
        "Depth (ft)": np.concatenate([depths, depths]),
        "Pressure (psi)": np.concatenate([Psurf_rest + Gs * depths, Pso + 0.03 * depths]),
        "Line": (["Produced-fluid gradient"] * len(depths) + ["Gas injection pressure"] * len(depths)),
    })
    ay = alt.Y("Depth (ft):Q", scale=alt.Scale(reverse=True))
    lines = alt.Chart(line_df).mark_line(strokeWidth=2.8).encode(
        x=alt.X("Pressure (psi):Q"), y=ay,
        color=alt.Color("Line:N",
            scale=alt.Scale(domain=["Produced-fluid gradient", "Gas injection pressure"],
                            range=["#161616", "#E07B00"]),
            legend=alt.Legend(orient="top", title=None)))
    vp = df.rename(columns={"Surface Op. Pressure (psi)": "Pressure (psi)"})
    points = alt.Chart(vp).mark_point(size=210, shape="triangle-down", filled=True,
            color="#FFD60A", stroke="#161616", strokeWidth=1.6).encode(
        x="Pressure (psi):Q", y=ay, tooltip=["Valve", "Depth (ft)", "Pressure (psi)"])
    labels = alt.Chart(vp).mark_text(align="left", dx=13, fontSize=12, color="#161616",
            fontWeight="bold").encode(
        x="Pressure (psi):Q", y=ay, text="Valve")
    chart = (alt.layer(lines, points, labels)
             .properties(height=620, background="transparent")
             .configure_axis(labelColor="#5A554C", titleColor="#161616",
                             gridColor="#E3DDD0", domainColor="#161616")
             .configure_legend(labelColor="#161616", titleColor="#5A554C")
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

st.markdown('<div class="foot">Continuous Gas Lift Design'
            '<span class="star">&#10038;</span>Artificial Lift Chapter 3'
            '<span class="star">&#10038;</span>Petroleum Engineering</div>', unsafe_allow_html=True)
