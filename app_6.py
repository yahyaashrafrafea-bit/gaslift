# =============================================================
#  Continuous Gas Lift Design Tool  (Altair version)
#  Petroleum Engineering | Artificial Lift - Chapter 3
#  NOTE: Uses Altair (built into Streamlit) - NO plotly needed.
# =============================================================

import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(page_title="Gas Lift Design Tool", page_icon="fuel", layout="wide")

st.title("Continuous Gas Lift Design Tool")
st.caption(
    "Designs unloading valve spacing, depths, required gas volume and "
    "injection pressure for a continuous-flow gas lift well "
    "(Analytical Method, balanced valves)."
)

# ============================ CORE LOGIC ============================
def design_gas_lift(Pko, Pso, Pwh, Gs, Gu, dP, min_spacing,
                    inj_depth, well_depth, Psurf_first, Psurf_rest):
    valves = []
    DV1 = (Pko - 50 - Psurf_first) / Gs
    valves.append({
        "Valve": "V1 (Top)",
        "Depth (ft)": round(DV1, 1),
        "Surface Op. Pressure (psi)": round(Pso, 1),
        "Spacing from previous (ft)": round(DV1, 1),
    })
    Pso_n = Pso
    DV_prev = DV1
    n = 1
    while True:
        Pso_n = Pso_n - dP
        increment = (Pso_n - Gu * DV_prev - Psurf_rest) / Gs
        DV_new = DV_prev + increment
        if DV_new >= inj_depth or increment < min_spacing:
            break
        n += 1
        valves.append({
            "Valve": f"V{n}",
            "Depth (ft)": round(DV_new, 1),
            "Surface Op. Pressure (psi)": round(Pso_n, 1),
            "Spacing from previous (ft)": round(increment, 1),
        })
        DV_prev = DV_new
    valves.append({
        "Valve": "Operating",
        "Depth (ft)": round(inj_depth, 1),
        "Surface Op. Pressure (psi)": round(Pso_n, 1),
        "Spacing from previous (ft)": round(inj_depth - DV_prev, 1),
    })
    df = pd.DataFrame(valves)
    results = {"n_valves": len(df), "n_unloading": len(df) - 1, "deepest_unloading": DV_prev}
    return df, results


def gas_volume_required(glr_inj, inj_depth, q):
    return glr_inj * (inj_depth / 1000.0) * q


def injection_pressure_at_depth(Ps_psig, gamma_g, L, T_avg_R, Z):
    Ps_psia = Ps_psig + 14.7
    PL_psia = Ps_psia * np.exp((gamma_g * L) / (53.34 * T_avg_R * Z))
    return PL_psia - 14.7


# ============================ SIDEBAR ============================
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

with st.sidebar.expander("Gas Properties (for volume & pressure)"):
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

# ============================ VALIDATION ============================
errors = []
if Pso >= Pko:
    errors.append("Surface operating pressure (Pso) should be lower than kick-off pressure (Pko).")
if Gu >= Gs:
    errors.append("Unloading gradient (Gu) must be smaller than kill-fluid gradient (Gs).")
if inj_depth > well_depth:
    errors.append("Injection depth cannot be deeper than the well depth.")
if errors:
    for e in errors:
        st.error(e)
    st.stop()

# ============================ CALCULATE ============================
df, res = design_gas_lift(Pko, Pso, Pwh, Gs, Gu, dP, min_spacing,
                          inj_depth, well_depth, Psurf_first, Psurf_rest)
T_avg_R = T_avg_F + 460.0
Vg = gas_volume_required(glr_inj, inj_depth, q)
PL = injection_pressure_at_depth(Pso, gamma_g, inj_depth, T_avg_R, Z)

# ============================ METRICS ============================
st.subheader("Design Results")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Valves", res["n_valves"])
c2.metric("Unloading Valves", res["n_unloading"])
c3.metric("Gas Volume Required", f"{Vg/1e6:.2f} MMscf/d")
c4.metric("Inj. Pressure @ Depth", f"{PL:,.0f} psi")

# ============================ TABS ============================
tab1, tab2 = st.tabs(["Valve Schedule", "Design Diagram"])

with tab1:
    st.dataframe(df, use_container_width=True, hide_index=True)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download valve schedule (CSV)", csv, "valve_schedule.csv", "text/csv")

with tab2:
    depths = np.linspace(0, well_depth, 50)
    line_df = pd.DataFrame({
        "Depth (ft)": np.concatenate([depths, depths]),
        "Pressure (psi)": np.concatenate([Psurf_rest + Gs * depths, Pso + 0.03 * depths]),
        "Line": (["Kill-fluid gradient"] * len(depths) + ["Gas injection pressure"] * len(depths)),
    })
    lines = (alt.Chart(line_df).mark_line().encode(
        x=alt.X("Pressure (psi):Q"),
        y=alt.Y("Depth (ft):Q", scale=alt.Scale(reverse=True)),
        color=alt.Color("Line:N", legend=alt.Legend(orient="top"))))
    valve_plot = df.rename(columns={"Surface Op. Pressure (psi)": "Pressure (psi)"})
    points = (alt.Chart(valve_plot).mark_point(size=160, shape="triangle-down", filled=True, color="green").encode(
        x="Pressure (psi):Q",
        y=alt.Y("Depth (ft):Q", scale=alt.Scale(reverse=True)),
        tooltip=["Valve", "Depth (ft)", "Pressure (psi)"]))
    labels = (alt.Chart(valve_plot).mark_text(align="left", dx=10, fontSize=11).encode(
        x="Pressure (psi):Q",
        y=alt.Y("Depth (ft):Q", scale=alt.Scale(reverse=True)),
        text="Valve"))
    chart = (lines + points + labels).properties(height=600).interactive()
    st.altair_chart(chart, use_container_width=True)

with st.expander("About & Verification (Example 4)"):
    st.markdown(
        "**Default values reproduce textbook Example 4** (Chapter 3): "
        "Well 5,000 ft, q = 1,200 BOPD, WC 80%, Injection depth 3,921 ft, "
        "Min spacing 250 ft, Balanced valve dP 25 psi, unloaded to pit (first valve).\n\n"
        "Equations (Analytical Method):\n"
        "- First valve:  DV1 = (Pko - 50 - Psurf) / Gs\n"
        "- Next valves:  DVn+1 = DVn + (Pso_n - Gu*DVn - Psurf) / Gs\n"
        "- Gas volume:   Vg = GLR_inj x (D_inj / 1000) x q\n"
        "- Inj. pressure: PL = Ps * exp(gamma_g*L / (53.34*Tavg*Z))"
    )
