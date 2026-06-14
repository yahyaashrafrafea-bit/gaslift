# =============================================================
#  GAS LIFT DESIGN TOOL  -  Continuous Flow
#  Petroleum Engineering | Artificial Lift - Chapter 3
#
#  VALVE-SPACING METHOD: Analytical method (source: Chapter 3).
#  The source lists two methods only: (1) Analytical, (2) Graphical
#  (balanced valve with design wellhead pressure). This app uses (1).
#
#  -------------------- INPUTS (sidebar) --------------------
#   Well       : well depth, tubing size, flow rate q, water cut, gas inj. depth
#   Reservoir  : static BHP / reservoir pressure (Pr), productivity index (PI)
#   Pressures  : kick-off (Pko), surface operating (Pso), wellhead (Pwh)
#   Gradients  : kill-fluid (Gs), unloading (Gu, from OTIS chart), dP, min spacing
#   Unloading  : pit / wellhead / separator
#   Gas        : gravity, avg temperature, Z, injection GLR
#
#  -------------------- OUTPUTS (main panel) ----------------
#   - Valve schedule: depth + operating pressure of each valve
#   - Total / unloading valve count, gas volume required, inj. pressure at depth
#   - Flowing bottomhole pressure Pwf  (straight-line IPR: Pwf = Pr - q/PI)
#   - Pressure-traverse / valve-spacing diagram + wellbore schematic
#
#  NOTE: The analytical valve-spacing method does NOT itself need PI or BHP
#  (source: "can be used when BHP and PI are unknown"). Pr and PI are used
#  only for the IPR (Pwf) and the flowing/static traverse lines in the diagram.
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
:root{ --bg:#F1EDE4; --card:#FFFFFF; --ink:#161616; --ink-soft:#5A554C;
  --yellow:#FFD60A; --grid:#E3DDD0; --hair:#E7E1D4; }
.stApp{ background:var(--bg); color:var(--ink); font-family:'Inter',sans-serif; }
header[data-testid="stHeader"]{ background:transparent; }
h1,h2,h3{ font-family:'Archivo',sans-serif!important; color:var(--ink); }
section[data-testid="stSidebar"]{ background:var(--card); border-right:2px solid var(--ink); }
section[data-testid="stSidebar"] h2{ font-family:'Archivo',sans-serif!important; text-transform:uppercase;
  letter-spacing:1px; font-weight:800; font-size:18px; color:var(--ink); }
section[data-testid="stSidebar"] label{ color:var(--ink-soft)!important; font-weight:500; }
.hl{ background:linear-gradient(transparent 55%, var(--yellow) 55%); padding:0 3px; }
.nameplate{ display:flex; align-items:center; gap:22px; padding:26px 30px;
  background:var(--card); border:2px solid var(--ink); border-radius:18px; }
.nameplate .mono{ width:64px; height:64px; border-radius:50%; flex:none; background:var(--yellow);
  border:2px solid var(--ink); display:flex; align-items:center; justify-content:center;
  font-family:'Archivo'; font-weight:900; font-size:25px; color:var(--ink); }
.nameplate h1{ margin:0; font-size:38px; font-weight:800; text-transform:uppercase; line-height:1.02; }
.nameplate .sub{ color:var(--ink-soft); font-size:13.5px; margin-top:7px; font-weight:500; }
.marquee{ background:var(--ink); color:#fff; border-radius:12px; padding:13px 22px; margin:14px 0 4px;
  display:flex; flex-wrap:wrap; gap:16px; align-items:center; justify-content:center;
  font-family:'Archivo'; font-weight:600; text-transform:uppercase; letter-spacing:1.5px; font-size:12.5px; }
.marquee .star{ color:var(--yellow); }
.eyebrow{ font-family:'Archivo'; font-weight:700; font-size:12px; letter-spacing:1.5px;
  text-transform:uppercase; color:var(--ink-soft); margin:26px 0 6px; }
.eyebrow .star{ color:var(--yellow); margin-right:7px; }
.gauge-row{ display:flex; gap:14px; flex-wrap:wrap; margin:6px 0; }
.gauge{ flex:1; min-width:160px; background:var(--card); border:2px solid var(--ink);
  border-radius:16px; padding:16px 18px; position:relative; }
.gauge.solid{ background:var(--yellow); }
.gauge .star{ position:absolute; top:14px; right:15px; color:var(--yellow); font-size:14px; }
.gauge.solid .star{ color:var(--ink); }
.gauge .label{ font-size:11px; text-transform:uppercase; letter-spacing:.8px; color:var(--ink-soft); font-weight:600; }
.gauge.solid .label{ color:var(--ink); }
.gauge .value{ font-family:'Archivo'; font-weight:800; font-size:30px; color:var(--ink);
  margin-top:9px; line-height:1; font-variant-numeric:tabular-nums; }
.gauge .unit{ font-family:'Inter'; font-weight:500; font-size:12px; color:var(--ink-soft); margin-left:4px; }
.stTabs [data-baseweb="tab-list"]{ gap:8px; border-bottom:2px solid var(--ink); }
.stTabs [data-baseweb="tab"]{ font-family:'Archivo'; font-weight:700; text-transform:uppercase;
  letter-spacing:1px; font-size:15px; color:var(--ink-soft); }
.stTabs [aria-selected="true"]{ color:var(--ink)!important; }
.stTabs [data-baseweb="tab-highlight"]{ background:var(--yellow)!important; height:3px; }
.tablewrap{ border:2px solid var(--ink); border-radius:14px; overflow:hidden; background:var(--card); margin-top:4px; }
.vtable{ width:100%; border-collapse:collapse; }
.vtable th{ background:var(--ink); color:#fff; text-transform:uppercase; font-size:11px; letter-spacing:1px;
  font-family:'Archivo'; font-weight:700; padding:13px 16px; text-align:right; }
.vtable th:first-child{ text-align:left; }
.vtable td{ padding:13px 16px; border-bottom:1px solid var(--hair); font-family:'Inter'; font-weight:500;
  font-size:14px; text-align:right; color:var(--ink); font-variant-numeric:tabular-nums; }
.vtable td:first-child{ text-align:left; font-weight:600; }
.vtable tbody tr:hover td{ background:#FBF7EC; }
.vtable tbody tr:last-child td{ background:var(--yellow); font-weight:700; }
.vtable tbody tr:last-child:hover td{ background:var(--yellow); }
.schematic{ background:var(--card); border:2px solid var(--ink); border-radius:16px; padding:14px;
  display:flex; justify-content:center; }
.stDownloadButton button, .stButton button{ background:var(--yellow)!important; color:var(--ink)!important;
  border:2px solid var(--ink)!important; border-radius:999px!important; font-family:'Archivo'; font-weight:700;
  text-transform:uppercase; letter-spacing:1px; padding:8px 24px!important; }
.stDownloadButton button:hover, .stButton button:hover{ background:var(--ink)!important; color:#fff!important; }
.note{ background:var(--card); border:2px solid var(--ink); border-radius:14px; padding:16px 20px;
  font-size:13.5px; line-height:1.6; }
.note b{ font-family:'Archivo'; }
.foot{ background:var(--ink); color:#fff; border-radius:16px; padding:22px; margin-top:34px; text-align:center;
  font-family:'Archivo'; font-weight:600; text-transform:uppercase; letter-spacing:1.5px; font-size:11.5px; }
.foot .star{ color:var(--yellow); margin:0 8px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ==================================================================
#  CORE ENGINEERING LOGIC
# ==================================================================
def design_gas_lift(Pko, Pso, Gs, Gu, dP, min_spacing, inj_depth, Psurf_first, Psurf_rest):
    """ANALYTICAL valve-spacing method (Chapter 3). Inputs are pressures/gradients
    only - PI and BHP are NOT required by this method."""
    valves = []
    DV1 = (Pko - 50 - Psurf_first) / Gs                       # first (top) valve
    valves.append({"Valve": "V1 (Top)", "Depth (ft)": round(DV1, 1),
                   "Surface Op. Pressure (psi)": round(Pso, 1),
                   "Spacing from previous (ft)": round(DV1, 1)})
    Pso_n, DV_prev, n = Pso, DV1, 1
    while True:
        Pso_n = Pso_n - dP
        increment = (Pso_n - Gu * DV_prev - Psurf_rest) / Gs   # consequent valves
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
    return df, {"n_valves": len(df), "n_unloading": len(df) - 1}


def flowing_bhp(Pr, PI, q):
    """Straight-line IPR (source data list: 'PI or flowing BHP'):  Pwf = Pr - q/PI"""
    return Pr - q / PI


def gas_volume_required(glr_inj, inj_depth, q):
    return glr_inj * (inj_depth / 1000.0) * q


def injection_pressure_at_depth(Ps_psig, gamma_g, L, T_avg_R, Z):
    Ps_psia = Ps_psig + 14.7
    return Ps_psia * np.exp((gamma_g * L) / (53.34 * T_avg_R * Z)) - 14.7


def wellbore_svg(df, well_depth, inj_depth):
    W, H = 470, 660
    top, bot = 66, 34
    usable = H - top - bot
    def y(d): return top + (d / well_depth) * usable
    cx = 116; cas_l, cas_r = cx - 34, cx + 34; tub_l, tub_r = cx - 17, cx + 17
    p = []; sy = top; td = y(well_depth); iy = y(inj_depth)
    p.append(f'<line x1="34" y1="{sy}" x2="{W-18}" y2="{sy}" stroke="#161616" stroke-width="2.5"/>')
    for hx in range(40, W - 24, 15):
        p.append(f'<line x1="{hx}" y1="{sy}" x2="{hx-8}" y2="{sy+9}" stroke="#161616" stroke-width="1"/>')
    p.append(f'<text x="34" y="{sy-7}" font-family="Inter,sans-serif" font-size="10" fill="#5A554C">0 ft</text>')
    p.append(f'<rect x="{tub_l-7}" y="{sy-28}" width="{(tub_r-tub_l)+14}" height="28" fill="#FFD60A" stroke="#161616" stroke-width="2.5" rx="3"/>')
    p.append(f'<text x="{cx}" y="{sy-9}" text-anchor="middle" font-family="Archivo,sans-serif" font-weight="800" font-size="10" fill="#161616">WELLHEAD</text>')
    p.append(f'<line x1="{cas_l}" y1="{sy}" x2="{cas_l}" y2="{td}" stroke="#161616" stroke-width="2.5"/>')
    p.append(f'<line x1="{cas_r}" y1="{sy}" x2="{cas_r}" y2="{td}" stroke="#161616" stroke-width="2.5"/>')
    p.append(f'<line x1="{cas_l}" y1="{td}" x2="{cas_r}" y2="{td}" stroke="#161616" stroke-width="2.5"/>')
    p.append(f'<rect x="{tub_l}" y="{sy}" width="{tub_r-tub_l}" height="{td-sy}" fill="#FFFFFF" stroke="#161616" stroke-width="2"/>')
    ax = (cas_r + tub_r) / 2
    p.append(f'<text x="{cas_r+6}" y="{sy+13}" font-family="Archivo,sans-serif" font-weight="700" font-size="10" fill="#E07B00">GAS IN</text>')
    gy = sy + 26
    while gy < iy - 14:
        p.append(f'<line x1="{ax}" y1="{gy}" x2="{ax}" y2="{gy+16}" stroke="#E07B00" stroke-width="2"/>')
        p.append(f'<path d="M{ax-3},{gy+11} L{ax},{gy+17} L{ax+3},{gy+11} Z" fill="#E07B00"/>')
        gy += 38
    for _, r in df.iterrows():
        d = float(r["Depth (ft)"]); vy = y(d); name = r["Valve"]; op = (name == "Operating")
        p.append(f'<rect x="{tub_r-5}" y="{vy-7}" width="10" height="14" fill="#FFD60A" stroke="#161616" stroke-width="1.6"/>')
        p.append(f'<line x1="{tub_r+5}" y1="{vy}" x2="{tub_r+42}" y2="{vy}" stroke="#161616" stroke-width="1" stroke-dasharray="2,2"/>')
        w = "800" if op else "600"
        p.append(f'<text x="{tub_r+46}" y="{vy-2}" font-family="Archivo,sans-serif" font-weight="{w}" font-size="11.5" fill="#161616">{name}</text>')
        p.append(f'<text x="{tub_r+46}" y="{vy+11}" font-family="Inter,sans-serif" font-size="10" fill="#5A554C">{d:.0f} ft</text>')
    p.append(f'<circle cx="{tub_r}" cy="{iy}" r="10" fill="none" stroke="#E07B00" stroke-width="2.2"/>')
    p.append(f'<text x="34" y="{td+17}" font-family="Inter,sans-serif" font-size="10" fill="#5A554C">TD {well_depth:.0f} ft</text>')
    return f'<svg viewBox="0 0 {W} {H}" width="100%" style="max-width:470px;">' + "".join(p) + '</svg>'

# ==================================================================
#  INPUTS  (sidebar)
# ==================================================================
st.sidebar.header("Inputs")

with st.sidebar.expander("Well Data", expanded=True):
    well_depth = st.number_input("Well depth (ft)", value=5000.0, min_value=100.0, step=100.0)
    tubing = st.selectbox("Tubing size (in)", ["2", "2.5", "3"], index=1)
    q = st.number_input("Design flow rate, q (bbl/d)", value=1200.0, min_value=1.0, step=50.0)
    wc = st.number_input("Water cut (%)", value=80.0, min_value=0.0, max_value=100.0, step=5.0)
    inj_depth = st.number_input("Gas injection depth (ft)", value=3921.0, min_value=100.0, step=50.0)

with st.sidebar.expander("Reservoir / IPR", expanded=True):
    Pr = st.number_input("Static BHP / reservoir pressure, Pr (psi)", value=2500.0, min_value=0.0, step=50.0)
    PI = st.number_input("Productivity index, PI (bbl/d/psi)", value=1.0, min_value=0.001, step=0.1, format="%.3f")
    st.caption("Used for IPR (Pwf = Pr - q/PI) and the traverse lines. "
               "Not required by the analytical valve-spacing method.")

with st.sidebar.expander("Pressures", expanded=True):
    Pko = st.number_input("Kick-off pressure, Pko (psi)", value=900.0, min_value=0.0, step=10.0)
    Pso = st.number_input("Surface operating pressure, Pso (psi)", value=850.0, min_value=0.0, step=10.0)
    Pwh = st.number_input("Wellhead pressure, Pwh (psi)", value=200.0, min_value=0.0, step=10.0)

with st.sidebar.expander("Gradients & Valves", expanded=True):
    Gs = st.number_input("Kill-fluid gradient, Gs (psi/ft)", value=0.5, min_value=0.001, step=0.01, format="%.3f")
    Gu = st.number_input("Design unloading gradient, Gu (psi/ft)", value=0.125, min_value=0.001, step=0.005, format="%.3f")
    st.caption("Gu is read from the OTIS unloading-gradient chart (Chapter 3) "
               "using your tubing size and design rate.")
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
        <h1>Gas <span class="hl">Lift</span> Design</h1>
        <div class="sub">Continuous-flow valve spacing &amp; pressure traverse - Analytical Method (Chapter 3)</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('<div class="marquee"><span>Continuous Flow</span><span class="star">&#10038;</span>'
            '<span>Balanced Valve</span><span class="star">&#10038;</span>'
            '<span>Analytical Method</span><span class="star">&#10038;</span>'
            '<span>Unloading Design</span></div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
#  VALIDATION
# ------------------------------------------------------------------
T_avg_R = T_avg_F + 460.0
Pwf = flowing_bhp(Pr, PI, q)
errors = []
if Pso >= Pko:
    errors.append("Surface operating pressure (Pso) must be lower than kick-off pressure (Pko).")
if Gu >= Gs:
    errors.append("Unloading gradient (Gu) must be smaller than kill-fluid gradient (Gs).")
if inj_depth > well_depth:
    errors.append("Injection depth cannot be deeper than the well depth.")
if Pwf <= 0:
    errors.append("Flowing BHP (Pwf = Pr - q/PI) is <= 0. Check reservoir pressure, PI and rate.")
if errors:
    for e in errors:
        st.error(e)
    st.stop()

# ------------------------------------------------------------------
#  CALCULATE OUTPUTS
# ------------------------------------------------------------------
df, res = design_gas_lift(Pko, Pso, Gs, Gu, dP, min_spacing, inj_depth, Psurf_first, Psurf_rest)
Vg = gas_volume_required(glr_inj, inj_depth, q)
PL = injection_pressure_at_depth(Pso, gamma_g, inj_depth, T_avg_R, Z)

# ------------------------------------------------------------------
#  OUTPUTS : GAUGES
# ------------------------------------------------------------------
st.markdown('<div class="eyebrow"><span class="star">&#10038;</span>Outputs</div>', unsafe_allow_html=True)

def gauge(label, value, unit, solid=False):
    cls = "gauge solid" if solid else "gauge"
    u = f'<span class="unit">{unit}</span>' if unit else ""
    return (f'<div class="{cls}"><span class="star">&#10038;</span>'
            f'<div class="label">{label}</div><div class="value">{value}{u}</div></div>')

cards = "".join([
    gauge("Total Valves", res["n_valves"], "", solid=True),
    gauge("Unloading Valves", res["n_unloading"], ""),
    gauge("Gas Volume", f"{Vg/1e6:.2f}", "MMscf/d"),
    gauge("Inj. Pressure @ Depth", f"{PL:,.0f}", "psi"),
    gauge("Flowing BHP (Pwf)", f"{Pwf:,.0f}", "psi"),
])
st.markdown(f'<div class="gauge-row">{cards}</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
#  TABS
# ------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Valve Schedule", "Well Diagram", "Method & Inputs"])

with tab1:
    st.markdown('<div class="eyebrow"><span class="star">&#10038;</span>'
                'Valve placement from surface to injection point</div>', unsafe_allow_html=True)
    head = "".join(f"<th>{c}</th>" for c in df.columns)
    body = "".join("<tr>" + "".join(f"<td>{r[c]}</td>" for c in df.columns) + "</tr>"
                   for _, r in df.iterrows())
    st.markdown(f'<div class="tablewrap"><table class="vtable"><thead><tr>{head}</tr></thead>'
                f'<tbody>{body}</tbody></table></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"),
                       "valve_schedule.csv", "text/csv")

with tab2:
    col_a, col_b = st.columns([1, 1.35])
    with col_a:
        st.markdown('<div class="eyebrow"><span class="star">&#10038;</span>Wellbore schematic</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="schematic">{wellbore_svg(df, well_depth, inj_depth)}</div>',
                    unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="eyebrow"><span class="star">&#10038;</span>'
                    'Pressure traverse &amp; valve spacing</div>', unsafe_allow_html=True)

        def gasP(d, Ps):
            return (Ps + 14.7) * np.exp(gamma_g * d / (53.34 * T_avg_R * Z)) - 14.7

        TD = well_depth
        dd = np.linspace(0, TD, 80)
        dd_u = np.linspace(0, inj_depth, 40)
        dd_b = np.linspace(inj_depth, TD, 30)
        Pinj = float(gasP(inj_depth, Pso))

        rows = []
        for d in dd:   rows.append((float(gasP(d, Pso)), float(d), "Gas inj. pressure (Pso)"))
        for d in dd:   rows.append((float(gasP(d, Pko)), float(d), "Kick-off pressure (Pko)"))
        for d in dd_u: rows.append((Psurf_rest + Gs * float(d), float(d), "Kill-fluid gradient (Gs)"))
        for d in dd_u: rows.append((Pwh + Gu * float(d), float(d), "Unloading gradient (Gu)"))
        # flowing traverse below inj. point -> reaches Pwf at TD
        for d in dd_b:
            frac = (float(d) - inj_depth) / max(TD - inj_depth, 1e-6)
            rows.append((Pinj + frac * (Pwf - Pinj), float(d), "Flowing gradient below inj."))
        # static reservoir gradient anchored at Pr at TD (slope Gs)
        d_top = max(0.0, TD - Pr / Gs)
        for d in np.linspace(d_top, TD, 30):
            rows.append((Pr - Gs * (TD - float(d)), float(d), "Static reservoir gradient"))
        line_df = pd.DataFrame(rows, columns=["Pressure (psi)", "Depth (ft)", "series"])

        order = ["Gas inj. pressure (Pso)", "Kick-off pressure (Pko)", "Kill-fluid gradient (Gs)",
                 "Unloading gradient (Gu)", "Flowing gradient below inj.", "Static reservoir gradient"]
        palette = ["#2BA8E0", "#1B6B3A", "#3FAE4A", "#B0179B", "#E8852B", "#1F6FB2"]

        ay = alt.Y("Depth (ft):Q", scale=alt.Scale(reverse=True), title="Depth (ft)")
        ax = alt.X("Pressure (psi):Q", title="Pressure (psig)")
        lines = alt.Chart(line_df).mark_line(strokeWidth=2.3).encode(
            x=ax, y=ay,
            color=alt.Color("series:N", scale=alt.Scale(domain=order, range=palette),
                            legend=alt.Legend(orient="bottom", title=None, columns=2)))

        vp = df.copy()
        vp["Pressure (psi)"] = [float(gasP(d, ps)) for d, ps
                                in zip(vp["Depth (ft)"], vp["Surface Op. Pressure (psi)"])]
        stair_rows = []
        for d, ps in zip(vp["Depth (ft)"], vp["Surface Op. Pressure (psi)"]):
            xv = float(gasP(d, ps)); xl = Psurf_rest + Gs * float(d)
            stair_rows.append((min(xv, xl), max(xv, xl), float(d)))
        stair_df = pd.DataFrame(stair_rows, columns=["x", "x2", "Depth (ft)"])
        stairs = alt.Chart(stair_df).mark_rule(color="#E0392B", strokeDash=[5, 3],
                strokeWidth=1.3).encode(x="x:Q", x2="x2:Q", y=ay)
        points = alt.Chart(vp).mark_point(size=190, shape="triangle-right", filled=True,
                color="#FFD60A", stroke="#161616", strokeWidth=1.5).encode(
            x="Pressure (psi):Q", y=ay, tooltip=["Valve", "Depth (ft)"])
        vlabels = alt.Chart(vp).mark_text(align="left", dx=11, fontSize=10, color="#161616",
                fontWeight="bold").encode(x="Pressure (psi):Q", y=ay, text="Valve")
        special = pd.DataFrame({"Pressure (psi)": [Pinj, Pwf, Pr],
                                "Depth (ft)": [inj_depth, TD, TD],
                                "tag": ["Injection point", "Pwf", "Pr"]})
        sp = alt.Chart(special).mark_point(size=120, filled=True, color="#161616").encode(
            x="Pressure (psi):Q", y=ay, tooltip=["tag", "Pressure (psi)", "Depth (ft)"])

        chart = (alt.layer(lines, stairs, points, vlabels, sp)
                 .properties(height=660, background="transparent")
                 .configure_axis(labelColor="#5A554C", titleColor="#161616",
                                 gridColor="#E3DDD0", domainColor="#161616")
                 .configure_legend(labelColor="#161616", labelFontSize=11)
                 .configure_view(strokeWidth=0))
        st.altair_chart(chart, use_container_width=True)

with tab3:
    st.markdown('<div class="eyebrow"><span class="star">&#10038;</span>Method, inputs &amp; outputs</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="note">'
        '<b>Valve-spacing method:</b> Analytical method (Chapter 3). The source lists two '
        'methods only - (1) Analytical and (2) Graphical (balanced valve with design wellhead '
        'pressure); this tool uses the Analytical method.<br><br>'
        '<b>Why no PI / BHP in the spacing calculation?</b> The source states the analytical '
        'method "can be used when BHP and PI are unknown, and the method neglects the gas-column '
        'weight." So PI and reservoir pressure are not required to space the valves. They are '
        'used here only for the IPR (flowing bottomhole pressure) and the flowing / static '
        'traverse lines in the diagram.<br><br>'
        '<b>Inputs:</b> well depth, tubing size, rate q, water cut, injection depth, reservoir '
        'pressure Pr, productivity index PI, Pko, Pso, Pwh, kill-fluid gradient Gs, unloading '
        'gradient Gu (from OTIS chart), valve dP, minimum spacing, unloading destination, gas '
        'gravity, temperature, Z, injection GLR.<br><br>'
        '<b>Outputs:</b> valve schedule (depth + operating pressure), valve count, gas volume '
        'required, injection pressure at depth, flowing bottomhole pressure Pwf, and the '
        'pressure-traverse / wellbore diagram.<br><br>'
        '<b>Key equations (Analytical Method):</b><br>'
        '&bull; First valve: DV1 = (Pko - 50 - Psurf) / Gs<br>'
        '&bull; Next valves: DVn+1 = DVn + (Pso_n - Gu&middot;DVn - Psurf) / Gs<br>'
        '&bull; IPR: Pwf = Pr - q / PI<br>'
        '&bull; Gas volume: Vg = GLR_inj &times; (D_inj / 1000) &times; q<br>'
        '&bull; Inj. pressure: PL = Ps &middot; exp(gamma_g&middot;L / (53.34&middot;Tavg&middot;Z))'
        '</div>', unsafe_allow_html=True)

st.markdown('<div class="foot">Continuous Gas Lift Design<span class="star">&#10038;</span>'
            'Artificial Lift Chapter 3<span class="star">&#10038;</span>Analytical Method</div>',
            unsafe_allow_html=True)
