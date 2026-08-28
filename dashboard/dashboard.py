"""
HB-Eval — Dashboard MVP
Schema (verified 2026-06-03):
  evaluations: id, project_id, agent_id, trajectory_hash,
               pei_score, irs_score, csi_score, frr_score, ti_score,
               verdict, created_at
  edm_memory:  fetched with select("*")
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client

EVAL_TABLE   = "evaluations"
MEMORY_TABLE = "edm_memory"
EVAL_SELECT  = "id,project_id,agent_id,pei_score,irs_score,csi_score,frr_score,ti_score,verdict,created_at"

st.set_page_config(
    page_title="HB-Eval · Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp { background-color: #060c18; }
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 16px;
    }
    h2 { color: #e2e8f0; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# Base layout — NO yaxis here to avoid conflict when charts override it
PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.02)",
    font=dict(color="#94a3b8", family="Inter, sans-serif"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zeroline=False),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zeroline=False),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=0, r=0, t=32, b=0),
)

def plotly_layout(**yaxis_overrides):
    """Return PLOTLY_BASE with optional yaxis overrides merged cleanly."""
    layout = dict(PLOTLY_BASE)
    if yaxis_overrides:
        layout["yaxis"] = {**layout["yaxis"], **yaxis_overrides}
    return layout


@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


@st.cache_data(ttl=60)
def load_evaluations(limit: int = 500) -> pd.DataFrame:
    sb = get_supabase()
    response = (
        sb.table(EVAL_TABLE)
        .select(EVAL_SELECT)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    if not response.data:
        return pd.DataFrame()
    df = pd.DataFrame(response.data)
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df


@st.cache_data(ttl=60)
def load_memory(limit: int = 50) -> pd.DataFrame:
    sb = get_supabase()
    response = (
        sb.table(MEMORY_TABLE)
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    if not response.data:
        return pd.DataFrame()
    df = pd.DataFrame(response.data)
    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(df["created_at"])
    return df


def main():
    st.markdown("## 🛡️ HB-Eval · Reliability Dashboard")
    st.markdown(
        "<p style='color:#64748b; margin-top:-12px;'>Live reliability intelligence · refreshes every 60s</p>",
        unsafe_allow_html=True,
    )

    with st.spinner("Loading..."):
        df_eval   = load_evaluations(limit=500)
        df_memory = load_memory(limit=50)

    if df_eval.empty:
        st.info("No evaluations yet. Run your first `client.evaluate_with_battery()` to see data here.", icon="📭")
        return

    # ── SECTION 1: GLOBAL OVERVIEW ─────────────────────────────────────
    st.markdown("---")
    st.markdown("## 📊 Global Overview")

    total  = len(df_eval)
    safe   = int((df_eval["verdict"] == "SAFE").sum())
    unsafe = int((df_eval["verdict"] == "UNSAFE").sum())
    rate   = safe / total * 100 if total else 0

    avg_pei = df_eval["pei_score"].mean()
    avg_irs = df_eval["irs_score"].mean()
    avg_frr = df_eval["frr_score"].mean()
    avg_csi = df_eval["csi_score"].mean()
    avg_ti  = df_eval["ti_score"].mean()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Runs", f"{total:,}")
    c2.metric("SAFE",  f"{safe:,}",   delta=f"{rate:.1f}%")
    c3.metric("UNSAFE", f"{unsafe:,}")
    c4.metric("Avg PEI", f"{avg_pei:.3f}")
    c5.metric("Avg IRS", f"{avg_irs:.3f}")

    st.markdown("<br>", unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 2])

    with col_l:
        st.markdown("##### Verdict Distribution")
        fig_pie = px.pie(
            pd.DataFrame({"Verdict": ["SAFE","UNSAFE"], "Count": [safe, unsafe]}),
            names="Verdict", values="Count",
            color="Verdict",
            color_discrete_map={"SAFE": "#4ade80", "UNSAFE": "#f87171"},
            hole=0.5,
        )
        fig_pie.update_layout(**plotly_layout())
        st.plotly_chart(fig_pie, width="stretch")

    with col_r:
        st.markdown("##### Average Metric Scores vs Tier 2 Targets")
        m_df = pd.DataFrame({
            "Metric":  ["PEI", "IRS", "FRR", "CSI"],
            "Score":   [round(avg_pei,3), round(avg_irs,3), round(avg_frr,3), round(avg_csi,3)],
            "Target":  [0.80, 0.75, 0.85, 0.80],
        })
        fig_m = go.Figure()
        fig_m.add_trace(go.Bar(
            x=m_df["Metric"], y=m_df["Score"],
            name="Current Avg",
            marker_color=["#3b82f6","#8b5cf6","#10b981","#f59e0b"],
            text=m_df["Score"], textposition="outside",
        ))
        fig_m.add_trace(go.Scatter(
            x=m_df["Metric"], y=m_df["Target"],
            mode="lines+markers", name="Tier 2 Threshold",
            line=dict(color="#f97316", dash="dash", width=1.5),
        ))
        fig_m.update_layout(**plotly_layout(range=[0, 1.1]))
        st.plotly_chart(fig_m, width="stretch")

    st.caption(f"⏱ Avg Traceability Index (TI): **{avg_ti:.2f} / 5.0** — Tier 2 requires ≥ 4.0")

    # ── SECTION 2: RELIABILITY TRENDS ──────────────────────────────────
    st.markdown("---")
    st.markdown("## 📈 Reliability Trends")
    st.caption("Last 100 runs · chronological order")

    df_t = df_eval.head(100).sort_values("created_at").reset_index(drop=True)
    df_t["run_index"] = range(1, len(df_t) + 1)

    tab1, tab2, tab3 = st.tabs(["PEI & IRS", "FRR", "Verdict Timeline"])

    with tab1:
        f1 = go.Figure()
        f1.add_trace(go.Scatter(
            x=df_t["run_index"], y=df_t["pei_score"],
            name="PEI", mode="lines", line=dict(color="#3b82f6", width=2),
            fill="tozeroy", fillcolor="rgba(59,130,246,0.07)",
        ))
        f1.add_trace(go.Scatter(
            x=df_t["run_index"], y=df_t["irs_score"],
            name="IRS", mode="lines", line=dict(color="#8b5cf6", width=2),
            fill="tozeroy", fillcolor="rgba(139,92,246,0.07)",
        ))
        f1.add_hline(y=0.80, line_dash="dot", line_color="#f97316",
                     annotation_text="PEI Tier 2", annotation_position="top right")
        f1.add_hline(y=0.75, line_dash="dot", line_color="#f97316",
                     annotation_text="IRS Tier 2", annotation_position="bottom right")
        f1.update_layout(**plotly_layout(range=[0, 1.05]))
        st.plotly_chart(f1, width="stretch")

    with tab2:
        f2 = go.Figure()
        f2.add_trace(go.Scatter(
            x=df_t["run_index"], y=df_t["frr_score"],
            name="FRR", mode="lines+markers",
            line=dict(color="#10b981", width=2), marker=dict(size=4),
        ))
        f2.add_hline(y=0.85, line_dash="dot", line_color="#f97316",
                     annotation_text="FRR Tier 2")
        f2.update_layout(**plotly_layout(range=[0, 1.05]))
        st.plotly_chart(f2, width="stretch")

    with tab3:
        f3 = go.Figure()
        for v, color in [("SAFE","#4ade80"), ("UNSAFE","#f87171")]:
            mask = df_t["verdict"] == v
            f3.add_trace(go.Scatter(
                x=df_t.loc[mask, "run_index"],
                y=[1] * int(mask.sum()),
                mode="markers", name=v,
                marker=dict(color=color, size=12),
            ))
        f3.update_layout(**plotly_layout(), yaxis_visible=False, height=180)
        st.plotly_chart(f3, width="stretch")

    # ── SECTION 3: EDM MEMORY MONITOR ──────────────────────────────────
    st.markdown("---")
    st.markdown("## 🧠 EDM Memory Monitor")
    st.caption("Recent successful trajectories in Evaluation-Driven Memory")

    if df_memory.empty:
        st.info("EDM is empty — no successful runs indexed yet.", icon="📭")
    else:
        latest = df_memory["created_at"].max().strftime("%Y-%m-%d %H:%M UTC")
        st.markdown(f"**{len(df_memory)} memories** · Latest: {latest}")

        df_show = df_memory.copy()
        if "created_at" in df_show.columns:
            df_show["created_at"] = df_show["created_at"].dt.strftime("%Y-%m-%d %H:%M")
        for col in df_show.select_dtypes(include="object").columns:
            df_show[col] = df_show[col].astype(str).str[:80] + "…"

        col_cfg = {
            col: st.column_config.ProgressColumn(
                col.replace("_score","").upper(),
                min_value=0, max_value=1, format="%.3f"
            )
            for col in df_show.columns if col.endswith("_score")
        }
        st.dataframe(df_show, use_container_width=True, hide_index=True, column_config=col_cfg)

    st.markdown("---")
    st.markdown(
        "<p style='color:#334155;font-size:12px;text-align:center;'>"
        "HB-Eval v2.2.0 · "
        "<a href='https://github.com/hb-evalSystem/HB-System' style='color:#475569;'>GitHub</a>"
        "</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
