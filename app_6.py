# =============================================================
#  GAS LIFT DESIGN TOOL  -  Continuous Flow
#  Petroleum Engineering | Artificial Lift - Chapter 3
#
#  Fully computed from equations (validated vs source Examples 1-3):
#   * Gs   : OTIS salt water-oil chart (API + water cut)   [API35/SW90 -> 0.455]
#   * Pwf  : PI method  Pwf = Pr - q/PI  (or entered directly)   [Ex1 -> 2867]
#   * SFL  : static fluid level  = D - Pr/Gs                     [Ex1 -> 3407]
#   * WFL  : working fluid level = D - Pwf/Gs                    [Ex1 -> 3699]
#   * Gpko,Gpso : gas-column gradients from Pko,Pso & gas gravity[Ex1 -> 25,22]
#   * Pko@D,Pso@D : casing pressures at well depth              [Ex1 -> 1200,1026]
#   * DPOI : point of balance (Pso gas line vs Gfb) minus valve dP
#   * Valve spacing: graphical construction using Gs + gas lines (NO Gu)
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
.gauge-row{ display:flex; gap:13px; flex-wrap:wrap; margin:6px 0; }
.gauge{ flex:1; min-width:145px; background:var(--card); border:2px solid var(--ink);
  border-radius:16px; padding:15px 17px; position:relative; }
.gauge.solid{ background:var(--yellow); }
.gauge .star{ position:absolute; top:13px; right:14px; color:var(--yellow); font-size:13px; }
.gauge.solid .star{ color:var(--ink); }
.gauge .label{ font-size:10.5px; text-transform:uppercase; letter-spacing:.7px; color:var(--ink-soft); font-weight:600; }
.gauge.solid .label{ color:var(--ink); }
.gauge .value{ font-family:'Archivo'; font-weight:800; font-size:25px; color:var(--ink);
  margin-top:8px; line-height:1; font-variant-numeric:tabular-nums; }
.gauge .unit{ font-family:'Inter'; font-weight:500; font-size:11px; color:var(--ink-soft); margin-left:3px; }
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
.pill{ display:inline-block; background:var(--yellow); border:2px solid var(--ink); border-radius:999px;
  padding:3px 12px; font-family:'Archivo'; font-weight:700; font-size:12px; text-transform:uppercase;
  letter-spacing:.5px; }
.foot{ background:var(--ink); color:#fff; border-radius:16px; padding:22px; margin-top:34px; text-align:center;
  font-family:'Archivo'; font-weight:600; text-transform:uppercase; letter-spacing:1.5px; font-size:11.5px; }
.foot .star{ color:var(--yellow); margin:0 8px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ==================================================================
#  CORE ENGINEERING LOGIC
# ==================================================================
def oil_gradient_from_api(api):
    return (141.5 / (131.5 + api)) * 0.433


def gs_from_chart(api, pct_water):
    """OTIS salt water-oil chart. API line: pure-oil gradient (0%) -> 0.465 (100%).
    Validated: API35/SW90 -> 0.455 psi/ft (source Examples 1 & 3)."""
    return oil_gradient_from_api(api) + (pct_water / 100.0) * (0.465 - oil_gradient_from_api(api))


def flowing_bhp_PI(Pr, PI, q):
    """PI method (undersaturated): Pwf = Pr - q/PI. Validated Ex1 -> 2867."""
    return Pr - q / PI


def gas_gradient(Ps_psig, gamma_g, T_avg_R, Z):
    """Weight-of-gas-column gradient, psi/ft:  Gp = Ps*gamma_g / (53.34*Tavg*Z).
    Validated Ex1: Pko1000 -> 25 psi/1000ft, Pso850 -> ~22 psi/1000ft."""
    return Ps_psig * gamma_g / (53.34 * T_avg_R * Z)


def fluid_levels(D, Pr, Pwf, Gs):
    """Static fluid level and working fluid level (source slide 40).
    SFL = D - Pr/Gs ;  WFL = D - Pwf/Gs.  Validated Ex1 -> 3407 / 3699."""
    return D - Pr / Gs, D - Pwf / Gs


def injection_depth(Pso, Gpso, Pwf, Gs, D, dP_op):
    """DPOI: gas line (Pso + Gpso*d) meets flowing line below inj (Pwf - Gs*(D-d))
    at the point of balance (POB); injection = POB pressure - dP_op."""
    denom = Gs - Gpso
    if denom <= 0:
        return None
    d_POB = (Pso - Pwf + Gs * D) / denom
    if not (0.0 < d_POB < D):
        return None
    P_POB = Pso + Gpso * d_POB
    P_inj = P_POB - dP_op
    d_DPOI = D - (Pwf - P_inj) / Gs
    if not (0.0 < d_DPOI < D):
        return None
    return {"DPOI": d_DPOI, "P_inj": P_inj, "POB": d_POB, "P_POB": P_POB}


def design_gas_lift(valve_type, Pko, Pso, Gs, Gpko, Gpso, dP, min_spacing,
                    dpoi, Ptub_first, Ptub):
    """Graphical valve-spacing construction (NO Gu). Uses the kill-fluid gradient
    (Gs) and the descending gas-injection lines (Gpko / Gpso).
      Top valve : kill-fluid line meets kick-off casing line (Pko-50):
                  DV1 = (Pko - 50 - Ptub_first) / (Gs - Gpko)
      Next      : DVn = (Pso_n - Ptub + Gs*DV_prev) / (Gs - Gpso)
                  Pso_n = Pso - (n-1)*dP  (balanced)  or  Pso  (unbalanced)."""
    DV1 = (Pko - 50 - Ptub_first) / (Gs - Gpko)
    valves = [{"Valve": "V1 (Top)", "Depth (ft)": round(DV1, 1),
               "Op. Pressure (psi)": round(Pso, 1), "Spacing (ft)": round(DV1, 1)}]
    DV_prev, n = DV1, 1
    while True:
        n += 1
        Pso_n = Pso - (n - 1) * dP if valve_type == "Balanced" else Pso
        DV_new = (Pso_n - Ptub + Gs * DV_prev) / (Gs - Gpso)
        inc = DV_new - DV_prev
        if DV_new >= dpoi or inc < min_spacing:
            break
        valves.append({"Valve": f"V{n}", "Depth (ft)": round(DV_new, 1),
                       "Op. Pressure (psi)": round(Pso_n, 1), "Spacing (ft)": round(inc, 1)})
        DV_prev = DV_new
    Pso_op = Pso - (len(valves) - 1) * dP if valve_type == "Balanced" else Pso
    valves.append({"Valve": "Operating", "Depth (ft)": round(dpoi, 1),
                   "Op. Pressure (psi)": round(Pso_op, 1), "Spacing (ft)": round(dpoi - DV_prev, 1)})
    df = pd.DataFrame(valves)
    return df, {"n_valves": len(df), "n_unloading": len(df) - 1}


def build_zigzag(valve_type, Pko, Pso, Gs, Gpko, Gpso, dP, min_spacing, dpoi, P_inj):
    """Graphical zigzag valve-spacing construction referenced to the TUBING line
    (straight line from surface (0,0) to the injection point (P_inj, DPOI)).
      - Top valve V1: kill-fluid (Gs) line from surface meets the Pko-50 casing line.
      - Each next valve: from the tubing line, a Gs line meets the Pso casing line
        (Pso reduced by dP per valve for balanced; constant for unbalanced).
      - A horizontal connector returns from each valve to the tubing line (the zigzag).
    Returns valves list plus diagonal/horizontal segment lists for plotting."""
    def Ptub(d):
        return (P_inj / dpoi) * d
    diagonals, horizontals, valves = [], [], []
    d1 = (Pko - 50 - 0.0) / (Gs - Gpko)          # Gs from (0,0) to Pko-50 line
    P1c = (Pko - 50) + Gpko * d1
    diagonals.append(((0.0, 0.0), (P1c, d1)))
    valves.append(("V1 (Top)", d1, P1c))
    horizontals.append(((P1c, d1), (Ptub(d1), d1)))
    d_prev, n = d1, 1
    while True:
        n += 1
        Pso_n = Pso - (n - 1) * dP if valve_type == "Balanced" else Pso
        Pstart = Ptub(d_prev)
        d_new = (Pso_n - Pstart + Gs * d_prev) / (Gs - Gpso)
        if d_new >= dpoi or (d_new - d_prev) < min_spacing:
            break
        Pc = Pso_n + Gpso * d_new
        diagonals.append(((Pstart, d_prev), (Pc, d_new)))
        valves.append((f"V{n}", d_new, Pc))
        horizontals.append(((Pc, d_new), (Ptub(d_new), d_new)))
        d_prev = d_new
    return valves, diagonals, horizontals


def gas_volume_required(glr_inj, dpoi, q):
    return glr_inj * (dpoi / 1000.0) * q


def wellbore_svg(df, well_depth, inj_depth):
    W, H = 470, 660; top, bot = 66, 34; usable = H - top - bot
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

with st.sidebar.expander("Design Method", expanded=True):
    valve_type = st.radio("Valve type", ["Balanced", "Unbalanced"], horizontal=True,
                          help="Balanced: Pso reduced by dP per valve. Unbalanced: Pso constant.")

with st.sidebar.expander("Well Data", expanded=True):
    well_depth = st.number_input("Well depth (ft)", value=8000.0, min_value=100.0, step=100.0)
    q = st.number_input("Design flow rate, q (bbl/d)", value=800.0, min_value=1.0, step=50.0)

with st.sidebar.expander("Fluid Properties (-> Gs)", expanded=True):
    api = st.number_input("Oil gravity (deg API)", value=35.0, min_value=10.0, max_value=60.0, step=1.0)
    water_cut = st.number_input("Water cut / salt water (%)", value=90.0, min_value=0.0, max_value=100.0, step=5.0)
    Gs = gs_from_chart(api, water_cut)
    st.markdown(f'<span class="pill">Gs = {Gs:.3f} psi/ft</span>', unsafe_allow_html=True)
    st.caption("Gs from the OTIS salt water-oil chart (API + water cut).")

with st.sidebar.expander("Reservoir / IPR", expanded=True):
    Pr = st.number_input("Static reservoir pressure, Pr (psi)", value=3000.0, min_value=0.0, step=50.0)
    have_pwf = st.checkbox("I already have Pwf (BHFP)", value=False,
                           help="Tick if Pwf is given; otherwise it is computed by the PI method.")
    if have_pwf:
        Pwf = st.number_input("Flowing BHP, Pwf (psi)", value=2867.0, min_value=0.0, step=50.0)
        PI = None
    else:
        PI = st.number_input("Productivity index, PI (bbl/d/psi)", value=6.0, min_value=0.001, step=0.5, format="%.3f")
        Pwf = flowing_bhp_PI(Pr, PI, q)
        st.markdown(f'<span class="pill">Pwf = {Pwf:,.0f} psi</span>', unsafe_allow_html=True)
        st.caption("PI method: Pwf = Pr - q/PI.")

with st.sidebar.expander("Pressures", expanded=True):
    Pko = st.number_input("Kick-off pressure, Pko (psi)", value=1000.0, min_value=0.0, step=10.0)
    Pso = st.number_input("Surface operating pressure, Pso (psi)", value=850.0, min_value=0.0, step=10.0)
    Pwh = st.number_input("Wellhead pressure, Pwh (psi)", value=100.0, min_value=0.0, step=10.0)

with st.sidebar.expander("Injection Point"):
    dP_op = st.number_input("Operating-valve pressure drop, dP_op (psi)", value=100.0, min_value=0.0, step=10.0,
                            help="Across the operating valve (assume 100 psi if not given).")

with st.sidebar.expander("Valve Spacing Parameters", expanded=True):
    dP = st.number_input("Valve pressure drop, dP (psi/valve)", value=25.0, min_value=1.0, step=5.0,
                         disabled=(valve_type == "Unbalanced"), help="Balanced valves only (15-25 psi).")
    min_spacing = st.number_input("Minimum valve spacing (ft)", value=250.0, min_value=10.0, step=10.0)

with st.sidebar.expander("Unloading Method"):
    unload = st.selectbox("Where is the well unloaded?",
                          ["Pit (first valve only)", "Wellhead", "Separator"])
    Psep = 0.0
    if unload == "Separator":
        Psep = st.number_input("Separator pressure, Psep (psi)", value=50.0, min_value=0.0, step=10.0)

with st.sidebar.expander("Gas Properties"):
    gamma_g = st.number_input("Gas relative density, gamma_g", value=0.70, min_value=0.55, max_value=1.2, step=0.01)
    T_avg_F = st.number_input("Average flowing temperature (degF)", value=140.0, step=5.0)
    st.caption("Z (gas compressibility) fixed at 0.90 and injection GLR at 200 scf/bbl/1000ft "
               "(rule of thumb) - not part of the given data.")

Z = 0.90            # rule-of-thumb assumption (not a given input)
glr_inj = 200       # scf/bbl/1000ft rule of thumb (150-250)

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
        <div class="sub">Continuous-flow injection depth, fluid levels &amp; valve spacing - Analytical Method</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown(f'<div class="marquee"><span>Continuous Flow</span><span class="star">&#10038;</span>'
            f'<span>{valve_type} Valve</span><span class="star">&#10038;</span>'
            f'<span>SFL / WFL</span><span class="star">&#10038;</span>'
            f'<span>Gpko / Gpso</span></div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
#  COMPUTE + VALIDATION
# ------------------------------------------------------------------
T_avg_R = T_avg_F + 460.0
Gpko = gas_gradient(Pko, gamma_g, T_avg_R, Z)   # psi/ft
Gpso = gas_gradient(Pso, gamma_g, T_avg_R, Z)   # psi/ft
Pko_at_D = Pko + Gpko * well_depth
Pso_at_D = Pso + Gpso * well_depth
SFL, WFL = fluid_levels(well_depth, Pr, Pwf, Gs)

errors = []
if Pso >= Pko:
    errors.append("Surface operating pressure (Pso) must be lower than kick-off pressure (Pko).")
if Gpko >= Gs or Gpso >= Gs:
    errors.append("Gas-column gradient exceeds the fluid gradient Gs - check pressures / gas gravity.")
if Pwf <= 0:
    errors.append("Flowing BHP (Pwf) is <= 0. Check reservoir pressure, PI and rate.")

inj = None
if not errors:
    inj = injection_depth(Pso, Gpso, Pwf, Gs, well_depth, dP_op)
    if inj is None:
        errors.append("No gas-lift injection point: the gas-injection line never balances the "
                      "flowing tubing pressure within the well. Increase Pso, or check Pwf and Gs.")
if errors:
    for e in errors:
        st.error(e)
    st.stop()

inj_depth = inj["DPOI"]
P_inj = inj["P_inj"]

# Graphical zigzag construction (tubing line referenced) - drives table AND diagram
zz_valves, zz_diag, zz_hor = build_zigzag(valve_type, Pko, Pso, Gs, Gpko, Gpso,
                                          dP, min_spacing, inj_depth, P_inj)
rows_v = [{"Valve": nm, "Depth (ft)": round(d, 1),
           "Casing Pressure (psi)": round(pc, 1)} for nm, d, pc in zz_valves]
prev = 0.0
for r in rows_v:
    r["Spacing (ft)"] = round(r["Depth (ft)"] - prev, 1); prev = r["Depth (ft)"]
rows_v.append({"Valve": "Operating", "Depth (ft)": round(inj_depth, 1),
               "Casing Pressure (psi)": round(P_inj, 1),
               "Spacing (ft)": round(inj_depth - prev, 1)})
df = pd.DataFrame(rows_v)
res = {"n_valves": len(df), "n_unloading": len(df) - 1}
Vg = gas_volume_required(glr_inj, inj_depth, q)

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
    gauge("Injection Depth (DPOI)", f"{inj_depth:,.0f}", "ft", solid=True),
    gauge("Total Valves", res["n_valves"], ""),
    gauge("Static Fluid Level", f"{SFL:,.0f}", "ft"),
    gauge("Working Fluid Level", f"{WFL:,.0f}", "ft"),
    gauge("Flowing BHP (Pwf)", f"{Pwf:,.0f}", "psi"),
    gauge("Gas Volume", f"{Vg/1e6:.2f}", "MMscf/d"),
])
st.markdown(f'<div class="gauge-row">{cards}</div>', unsafe_allow_html=True)
cards2 = "".join([
    gauge("Gs (chart)", f"{Gs:.3f}", "psi/ft"),
    gauge("Gpko", f"{Gpko*1000:.1f}", "psi/kft"),
    gauge("Gpso", f"{Gpso*1000:.1f}", "psi/kft"),
    gauge("Pko @ depth", f"{Pko_at_D:,.0f}", "psi"),
    gauge("Pso @ depth", f"{Pso_at_D:,.0f}", "psi"),
    gauge("POB", f"{inj['POB']:,.0f}", "ft"),
])
st.markdown(f'<div class="gauge-row">{cards2}</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
#  TABS
# ------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Valve Schedule", "Well Diagram", "Method & Inputs"])

with tab1:
    st.markdown(f'<div class="eyebrow"><span class="star">&#10038;</span>'
                f'{valve_type} valve - placement from surface to injection point</div>',
                unsafe_allow_html=True)
    head = "".join(f"<th>{c}</th>" for c in df.columns)
    body = "".join("<tr>" + "".join(f"<td>{r[c]}</td>" for c in df.columns) + "</tr>"
                   for _, r in df.iterrows())
    st.markdown(f'<div class="tablewrap"><table class="vtable"><thead><tr>{head}</tr></thead>'
                f'<tbody>{body}</tbody></table></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"),
                       "valve_schedule.csv", "text/csv")

with tab2:
    col_a, col_b = st.columns([1, 1.4])
    with col_a:
        st.markdown('<div class="eyebrow"><span class="star">&#10038;</span>Wellbore schematic</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="schematic">{wellbore_svg(df, well_depth, inj_depth)}</div>',
                    unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="eyebrow"><span class="star">&#10038;</span>'
                    'Pressure traverse - injection point &amp; fluid levels</div>', unsafe_allow_html=True)
        TD = well_depth
        ay = alt.Y("Depth (ft):Q", scale=alt.Scale(reverse=True), title="Depth (ft)")
        ax = alt.X("Pressure (psi):Q", title="Pressure (psig)")

        # --- main lines: Pso, Pko (to depth), tubing line (0,0)->DPOI, SFL/WFL gradients ---
        rows = [
            (Pso, 0.0, "Gas inj. pressure (Pso)"), (Pso_at_D, TD, "Gas inj. pressure (Pso)"),
            (Pko, 0.0, "Kick-off pressure (Pko)"), (Pko_at_D, TD, "Kick-off pressure (Pko)"),
            (0.0, 0.0, "Tubing line (-> DPOI)"), (P_inj, inj_depth, "Tubing line (-> DPOI)"),
            (0.0, SFL, "Static gradient (-> Pr)"), (Pr, TD, "Static gradient (-> Pr)"),
            (0.0, WFL, "Flowing gradient (-> Pwf)"), (Pwf, TD, "Flowing gradient (-> Pwf)"),
        ]
        line_df = pd.DataFrame(rows, columns=["Pressure (psi)", "Depth (ft)", "series"])
        order = ["Gas inj. pressure (Pso)", "Kick-off pressure (Pko)", "Tubing line (-> DPOI)",
                 "Static gradient (-> Pr)", "Flowing gradient (-> Pwf)"]
        palette = ["#2BA8E0", "#1B6B3A", "#B0179B", "#1F6FB2", "#E8852B"]
        lines = alt.Chart(line_df).mark_line(strokeWidth=2.3).encode(
            x=ax, y=ay, detail="series:N",
            color=alt.Color("series:N", scale=alt.Scale(domain=order, range=palette),
                            legend=alt.Legend(orient="bottom", title=None, columns=2)))

        # --- zigzag: green Gs transfer diagonals + red dashed horizontal connectors ---
        dgd = []
        for i, (a, b) in enumerate(zz_diag):
            dgd += [(a[0], a[1], i), (b[0], b[1], i)]
        gdiag = alt.Chart(pd.DataFrame(dgd, columns=["Pressure (psi)", "Depth (ft)", "g"])).mark_line(
            strokeWidth=2, color="#3FAE4A").encode(x="Pressure (psi):Q", y=ay, detail="g:N")
        hzd = []
        for i, (a, b) in enumerate(zz_hor):
            hzd += [(a[0], a[1], i), (b[0], b[1], i)]
        ghz = alt.Chart(pd.DataFrame(hzd, columns=["Pressure (psi)", "Depth (ft)", "g"])).mark_line(
            strokeWidth=1.5, color="#E0392B", strokeDash=[5, 3]).encode(
            x="Pressure (psi):Q", y=ay, detail="g:N")

        # --- valve markers on their casing lines ---
        vv = pd.DataFrame([(pc, d, nm) for nm, d, pc in zz_valves],
                          columns=["Pressure (psi)", "Depth (ft)", "Valve"])
        pts = alt.Chart(vv).mark_point(size=175, shape="triangle-right", filled=True,
                color="#FFD60A", stroke="#161616", strokeWidth=1.5).encode(
                x="Pressure (psi):Q", y=ay, tooltip=["Valve", "Depth (ft)"])
        vlab = alt.Chart(vv).mark_text(align="left", dx=11, fontSize=10, color="#161616",
                fontWeight="bold").encode(x="Pressure (psi):Q", y=ay, text="Valve")

        # --- key points: injection, SFL, WFL, Pr, Pwf ---
        key = pd.DataFrame({
            "Pressure (psi)": [P_inj, 0.0, 0.0, Pr, Pwf],
            "Depth (ft)": [inj_depth, SFL, WFL, TD, TD],
            "tag": ["Injection", "SFL", "WFL", "Pr", "Pwf"]})
        kp = alt.Chart(key).mark_point(size=150, filled=True, color="#161616").encode(
            x="Pressure (psi):Q", y=ay, tooltip=["tag", "Pressure (psi)", "Depth (ft)"])
        klab = alt.Chart(key).mark_text(align="left", dx=8, fontSize=10, color="#161616",
            fontWeight="bold").encode(x="Pressure (psi):Q", y=ay, text="tag")

        chart = (alt.layer(lines, gdiag, ghz, pts, vlab, kp, klab)
                 .properties(height=680, background="transparent")
                 .configure_axis(labelColor="#5A554C", titleColor="#161616",
                                 gridColor="#E3DDD0", domainColor="#161616")
                 .configure_legend(labelColor="#161616", labelFontSize=11)
                 .configure_view(strokeWidth=0))
        st.altair_chart(chart, use_container_width=True)

with tab3:
    st.markdown('<div class="eyebrow"><span class="star">&#10038;</span>Method, inputs &amp; outputs</div>',
                unsafe_allow_html=True)
    pwf_src = "entered directly" if have_pwf else "PI method (Pwf = Pr - q/PI)"
    st.markdown(
        '<div class="note">'
        f'<b>Design method:</b> {valve_type} valve.<br><br>'
        '<b>Fluid levels (linked to Pr &amp; Pwf):</b><br>'
        f'&bull; Static fluid level SFL = D - Pr/Gs = {SFL:,.0f} ft<br>'
        f'&bull; Working fluid level WFL = D - Pwf/Gs = {WFL:,.0f} ft<br>'
        'The static gradient line runs from Pr at well depth up to SFL (0 psi); the flowing '
        'gradient (Gfb = Gs) runs from Pwf up to WFL.<br><br>'
        '<b>Gas-column gradients from Pko, Pso &amp; gas gravity:</b><br>'
        f'&bull; Gpko = Pko&middot;gamma_g/(53.34&middot;Tavg&middot;Z) = {Gpko*1000:.1f} psi/1000ft '
        f'-> Pko @ {well_depth:,.0f} ft = {Pko_at_D:,.0f} psi<br>'
        f'&bull; Gpso = Pso&middot;gamma_g/(53.34&middot;Tavg&middot;Z) = {Gpso*1000:.1f} psi/1000ft '
        f'-> Pso @ {well_depth:,.0f} ft = {Pso_at_D:,.0f} psi<br><br>'
        '<b>Injection depth (DPOI):</b> gas line (Pso + Gpso&middot;d) meets the flowing line '
        f'(Pwf - Gs&middot;(D-d)) at POB = {inj["POB"]:,.0f} ft; injection point = POB - dP_op.<br><br>'
        '<b>Valve spacing (NO Gu):</b> graphical construction using Gs and the gas lines.<br>'
        '&bull; Top valve: DV1 = (Pko - 50 - Psurf)/(Gs - Gpko)<br>'
        '&bull; Next: DVn = (Pso_n - Ptub + Gs&middot;DV_prev)/(Gs - Gpso)<br><br>'
        f'<b>Pwf source:</b> {pwf_src}. <b>Gs:</b> OTIS salt water-oil chart (API + water cut).'
        '</div>', unsafe_allow_html=True)

st.markdown(f'<div class="foot">Continuous Gas Lift Design<span class="star">&#10038;</span>'
            f'{valve_type} Valve<span class="star">&#10038;</span>Analytical Method</div>',
            unsafe_allow_html=True)
