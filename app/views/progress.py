"""Progress — ML pipeline execution tracker for the AirQ Zambia framework.

Renders the six-stage research pipeline (ingestion → preprocessing →
imbalance/SMOTE-Tomek → training → evaluation → SHAP explainability) as a
vertical rail. Every stage state is a pure function of the signals the
backend actually exposes, so the page tells the truth about what is on
disk — nothing is fabricated.
"""

import pandas as pd
import streamlit as st

from style_assets import (
    _block,
    banner,
    foot_note,
    hero,
    ico,
    kpi_grid,
    panel_close,
    panel_open,
    section_label,
    status_list,
)
from state import (
    build_pipeline_stages,
    fetch_api_status,
    fetch_comparison_data,
    fetch_evaluation_metrics,
    fetch_imbalance_analysis,
    fetch_processed_csv,
    fetch_raw_csv,
    fetch_shap_summary,
    fetch_system_metrics,
    get_model_names,
    pipeline_summary,
)

STATE_LABEL = {
    "completed": "Completed",
    "partial": "Partial",
    "pending": "Pending",
    "offline": "Backend offline",
}

STATE_COLORS = {
    "completed": "#16a34a",
    "partial": "#f59e0b",
    "pending": "#64748b",
    "offline": "#dc2626",
}


def _pct(value, default="—"):
    """Format a 0-1 fraction as a percentage string, or ``default`` when bad."""
    try:
        if value is None:
            return default
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return default


def _uptime(seconds):
    """Human-readable uptime (``3d 4h``, ``5h 12m``, ``42m``) from seconds."""
    try:
        seconds = float(seconds or 0)
        days, rem = divmod(int(seconds), 86400)
        hours, rem = divmod(rem, 3600)
        minutes, _ = divmod(rem, 60)
        if days:
            return f"{days}d {hours}h"
        if hours:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    except (TypeError, ValueError):
        return "—"


def _overview_html(state, completed, total, pct):
    """HTML for the pipeline-overview header card for a given aggregate state."""
    color = STATE_COLORS[state]
    label = STATE_LABEL[state]
    title = {
        "completed": "Full research pipeline is live",
        "partial": "Some stages have run",
        "pending": "No pipeline run recorded yet",
        "offline": "Backend API unreachable",
    }[state]
    sub = {
        "completed": "All six stages reported completed by the backend — the tuned "
                     "hybrid SVM and its evidence artifacts are ready.",
        "partial": "The backend reports mixed signals. Use the refresh control or run "
                   "the remaining stages via the API to progress further.",
        "pending": "Start the pipeline on the backend (POST /api/pipeline/execute) "
                   "to populate the stages below.",
        "offline": "Start FastAPI on localhost:8000 to inspect real backend progress. "
                   "Until then the rail reflects the unreachable state.",
    }[state]
    fill_style = (
        "linear-gradient(90deg, #006a3d 0%, #22c55e 100%)"
        if state == "completed" else color
    )
    return (
        "<div class='pipe-overview'>"
        "<div class='pipe-ov-left'>"
        f"<div class='pipe-ov-label'>ML pipeline execution status</div>"
        f"<div class='pipe-ov-title'>{title}</div>"
        f"<div class='pipe-ov-sub'>{sub}</div>"
        "</div>"
        "<div class='pipe-ov-meter'>"
        f"<div class='pipe-ov-big'>{pct:.0f}% <small>{completed}/{total} stages</small></div>"
        "<div class='overall-bar'>"
        f"<div class='overall-fill' style='width:{pct:.1f}%;background:{fill_style};'></div>"
        "</div>"
        "<div class='overall-scale'>"
        f"<span>{label}</span><span>Backend status: "
        f"{'operational' if state != 'offline' else 'offline'}</span></div>"
        "</div>"
        "</div>"
    )


def _minority_recall_lift(comparison):
    """Return a (label, value) pair for the minority-class recall story."""
    optimized = (comparison or {}).get("optimized_metrics") or {}
    baseline = (comparison or {}).get("baseline_metrics") or {}
    for cls in ("Very Unhealthy", "Unhealthy"):
        opt_per = (optimized.get("per_class_metrics") or {}).get(cls) or {}
        base_per = (baseline.get("per_class_metrics") or {}).get(cls) or {}
        if opt_per or base_per:
            opt_rec = float(opt_per.get("recall") or 0)
            base_rec = float(base_per.get("recall") or 0)
            if opt_rec > 0:
                return (
                    f"{cls} recall",
                    f"{_pct(opt_rec)}"
                    + (f" · +{_pct(opt_rec - base_rec)}" if base_rec else ""),
                )
    return None


def _artifact_manifest(stages):
    """Table of expected artifacts and whether the backend has produced them."""
    rows = []
    for s in stages:
        state = s["state"]
        rows.append({
            "Artifact": f"Stage {s['num']} · {s['title']}",
            "Status": STATE_LABEL[state],
            "Evidence": "; ".join(f"{k}: {v}" for k, v in s["chips"][:3]),
        })
    return pd.DataFrame(rows)


def _stage_detail(stage):
    """Render the collapsible working-records section for a single stage."""
    key = stage["key"]
    state = stage["state"]
    if state == "offline":
        st.caption("No signal — backend unreachable for this stage.")
        return
    if state == "pending":
        st.caption("This stage has not produced an artifact on the backend yet.")
        return

    detail = stage.get("detail") or {}

    if key == "ingestion":
        raw = fetch_raw_csv()
        if raw is not None:
            st.markdown(
                f"**{len(raw):,}** raw records · **{raw.shape[1]}** columns "
                f"· schema from the last backend fetch."
            )
            if "city" in raw.columns:
                dist = raw["city"].value_counts().head(8)
                st.dataframe(
                    dist.rename_axis("City").reset_index(name="Records"),
                    width="stretch", hide_index=True,
                )
            csv = raw.head(100)
            with st.expander("Preview raw records", expanded=False):
                st.dataframe(csv, width="stretch", hide_index=True)

    elif key == "preprocessing":
        processed = fetch_processed_csv()
        if processed is not None:
            features = [c for c in processed.columns if c != "aqi_category"]
            st.markdown(
                f"**{len(processed):,}** processed records · **{len(features)}** "
                f"model features · label column `aqi_category`."
            )
            if processed.get("timestamp") is not None:
                st.caption(
                    f"Coverage: {processed['timestamp'].min()} → "
                    f"{processed['timestamp'].max()}"
                )
            with st.expander("Inspect feature columns", expanded=False):
                st.dataframe(
                    pd.DataFrame(
                        {
                            "Feature": features,
                            "Dtype": [str(processed[c].dtype) for c in features],
                            "Missing": [int(processed[c].isna().sum()) for c in features],
                        }
                    ),
                    width="stretch", hide_index=True,
                )

    elif key == "imbalance":
        imbalance = fetch_imbalance_analysis()
        dist = (imbalance or {}).get("class_distribution") or {}
        if dist:
            total = sum(int(v) for v in dist.values()) or 1
            dist_df = pd.DataFrame(
                [
                    {
                        "Air quality class": cls,
                        "Samples": int(n),
                        "Share": f"{n / total * 100:.1f}%",
                    }
                    for cls, n in dist.items()
                ]
            )
            st.markdown("**Class distribution** in the processed dataset:")
            st.dataframe(dist_df, width="stretch", hide_index=True)
            entropy = imbalance.get("entropy")
            gini = imbalance.get("gini_coefficient")
            entropy_txt = f"entropy {float(entropy):.3f}" if entropy is not None else "entropy —"
            gini_txt = f"gini {float(gini):.3f}" if gini is not None else "gini —"
            st.caption(f"{entropy_txt} · {gini_txt}")

    elif key == "training":
        models = (fetch_api_status() or {}).get("models") or {}
        trained = [k for k, v in models.items() if str(v).lower() == "trained"]
        st.markdown(
            f"Registry reports **{len(trained)}/2** models trained: "
            + (", ".join(trained) if trained else "none yet.")
            + " The optimized model trains on the SMOTE-Tomek-balanced split; "
              "the baseline on the raw imbalanced split."
        )
        comparison = fetch_comparison_data()
        optimized = (comparison or {}).get("optimized_metrics") or {}
        if optimized.get("accuracy") is not None:
            st.markdown(
                f"Optimized SVM accuracy on the held-out test set: "
                f"**{float(optimized['accuracy']) * 100:.1f}%**."
            )

    elif key == "evaluation":
        metrics = fetch_evaluation_metrics()
        payload = {}
        if isinstance(metrics, dict):
            payload = metrics.get("metrics") if isinstance(metrics.get("metrics"), dict) else metrics
        if payload:
            keys = [k for k in ("accuracy", "precision", "recall", "f1_score", "roc_auc")
                    if payload.get(k) is not None]
            ev_df = pd.DataFrame(
                [
                    {
                        "Metric": k.replace("_", " ").title(),
                        "Value": f"{float(payload[k]) * 100:.2f}%"
                        if payload[k] <= 1 else f"{payload[k]:.3f}",
                    }
                    for k in keys
                ]
            )
            st.dataframe(ev_df, width="stretch", hide_index=True)
        per_class = payload.get("per_class_metrics") or {}
        if per_class:
            with st.expander("Per-class reliability", expanded=False):
                rows = [
                    {
                        "Air quality class": cls,
                        "Precision": _pct(v.get("precision")),
                        "Recall": _pct(v.get("recall")),
                        "F1": _pct(v.get("f1_score")),
                        "Support": int(v.get("support") or 0),
                    }
                    for cls, v in per_class.items()
                ]
                st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    elif key == "explainability":
        st.markdown(
            "A cached SHAP summary is available — the explainability view renders "
            "the global feature-importance chart straight from it."
        )


def _clear_caches():
    """Evict every data fetch cached on this page so refresh re-probes the API."""
    for fn in (
        fetch_api_status, fetch_evaluation_metrics, fetch_comparison_data,
        fetch_shap_summary, fetch_raw_csv, fetch_processed_csv,
        fetch_imbalance_analysis, fetch_system_metrics,
    ):
        try:
            fn.clear()
        except Exception:
            pass


def render():
    """Main entry point: render the pipeline-progress page."""
    stats = fetch_api_status()
    model_names = get_model_names(stats)
    online = bool(stats)

    hero(
        "Oversight · ML Pipeline Progress",
        "ML Pipeline Execution & Progress",
        "End-to-end visibility into the six research stages behind the hybrid "
        "framework — which artifacts exist, what each produced, and what remains.",
        chips=[
            ("Backend", "Online" if online else "Offline",
             "good" if online else "bad"),
            ("Models", ", ".join(model_names[:2]) if model_names else "No model loaded",
             "good" if model_names else "bad"),
            ("Pipeline", "idle" if online else "unreachable", "good" if online else "bad"),
        ],
        breadcrumb=True,
    )

    if not online:
        banner(
            "warn",
            "Backend API is not reachable — the rail below shows the unreachable "
            "state. Start <b>localhost:8000</b> to inspect real pipeline progress.",
        )

    raw = fetch_raw_csv()
    processed = fetch_processed_csv()
    imbalance = fetch_imbalance_analysis()
    metrics = fetch_evaluation_metrics()
    comparison = fetch_comparison_data() or {}
    system = fetch_system_metrics()
    has_shap = fetch_shap_summary() is not None

    stages = build_pipeline_stages(
        status=stats, raw=raw, processed=processed, imbalance=imbalance,
        metrics=metrics, has_shap=bool(has_shap),
    )
    ov_state, completed, total, pct = pipeline_summary(stages)

    c_overview, c_refresh = st.columns([5, 1])
    with c_overview:
        st.markdown(_overview_html(ov_state, completed, total, pct),
                    unsafe_allow_html=True)
    with c_refresh:
        st.markdown(
            "<div style='height:100%;display:flex;flex-direction:column;"
            "justify-content:flex-end;gap:6px;'>"
            f"<div style='font-size:.7rem;color:var(--text-muted);font-weight:700;'>"
            f"{ico('activity', 13)} live probe</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("Refresh pipeline status", key="pipe_refresh", use_container_width=True):
            _clear_caches()
            st.rerun()
    st.caption(
        "Stage states reflect backend artifacts right now. Larger record counts and "
        "metrics age on 2-minute cache windows; use Refresh to re-probe immediately."
    )

    # ---- KPI overview ------------------------------------------------------
    raw_rows = len(raw) if raw is not None else 0
    metrics_payload = {}
    if isinstance(metrics, dict):
        metrics_payload = metrics.get("metrics") if isinstance(metrics.get("metrics"), dict) else metrics
    optimized_acc = metrics_payload.get("accuracy")
    minority_pair = _minority_recall_lift(comparison) or ("Minority recall", "—")

    kpi_grid(
        [
            ("Pipeline", f"{completed}/{total} stages", "backend-reported", "ok", "layers"),
            ("Dataset", f"{raw_rows:,}" if raw_rows else "—", "raw records", "ok", "database"),
            ("Accuracy", _pct(optimized_acc), "optimized SVM", "ok", "target"),
            (minority_pair[0], minority_pair[1], "vs baseline", "ok", "scale"),
            ("Backend uptime", _uptime(system.get("uptime")), "FastAPI @ :8000", "ok", "activity"),
        ]
    )

    # ---- Stage rail --------------------------------------------------------
    section_label("Pipeline stages", "six research stages in execution order")

    def _stage_rail():
        """Render the vertical pipeline-stage rail with status markers, KPIs and state chips."""
        rows = ["<div class='pipe-rail'>"]
        for i, s in enumerate(stages):
            is_last = i == len(stages) - 1
            track = "" if is_last else "<div class='pipe-track'></div>"
            chips = "".join(
                f"<span class='pipe-kpi'>{label}: <b>{value}</b></span>"
                for label, value in s["chips"]
            )
            rows.append(
                "<div class='pipe-stage'>"
                "<div class='pipe-col'>"
                f"<div class='pipe-marker {s['state']}'>{ico(s['icon'], 20)}</div>"
                + track
                + "</div>"
                "<div class='pipe-body'>"
                "<div class='pipe-head'>"
                "<div>"
                f"<div class='pipe-eyebrow'>Step {s['num']} of {len(stages)}</div>"
                f"<div class='pipe-title'>{s['title']}</div>"
                "</div>"
                f"<span class='pipe-chip {s['state']}'>"
                f"{STATE_LABEL.get(s['state'], s['state'])}</span>"
                "</div>"
                f"<div class='pipe-desc'>{s['desc']}</div>"
                "<div class='pipe-kpis'>"
                + chips
                + "</div>"
                "</div>"
                "</div>"
            )
        rows.append("</div>")
        return " ".join(rows)

    st.markdown(_block(_stage_rail()), unsafe_allow_html=True)

    # ---- Working records / stage details -----------------------------------
    section_label("Stage details & outputs", "collapsible evidence per stage")
    panel_open(
        "Working records",
        "database",
        "Expand any stage to inspect the exact artifacts its state was built from.",
    )
    any_detail = any(s["state"] in ("completed", "partial") for s in stages)
    if not any_detail:
        banner(
            "info",
            "No completed stages to inspect yet. Once the backend has produced "
            "artifacts, the details for each stage appear here.",
        )
    for s in stages:
        with st.expander(
            f"Step {s['num']} — {s['title']}"
            f"  ·  {STATE_LABEL.get(s['state'], s['state'])}",
            expanded=(s["state"] == "completed" and s["num"] in (1, 4)),
        ):
            _stage_detail(s)
    panel_close()

    # ---- Artifact manifest -------------------------------------------------
    section_label("Artifact manifest", "what the pipeline has produced on disk")
    status_list(
        [
            ("Raw telemetry", "Available" if raw is not None else "Missing",
             "good" if raw is not None else ("warn" if online else "bad")),
            ("Processed dataset", "Available" if processed is not None else "Missing",
             "good" if processed is not None else ("warn" if online else "bad")),
            ("Imbalance analysis", "Available" if imbalance else "Missing",
             "good" if imbalance else ("warn" if online else "bad")),
            ("Models", ", ".join(model_names) if model_names else "None",
             "good" if model_names else ("warn" if online else "bad")),
            ("Metrics & comparison", "Available" if metrics_payload else "Missing",
             "good" if metrics_payload else ("warn" if online else "bad")),
            ("SHAP summary", "Cached" if has_shap else "Not generated",
             "good" if has_shap else ("warn" if online else "bad")),
        ]
    )
    manifest = _artifact_manifest(stages)
    st.dataframe(manifest, width="stretch", hide_index=True)

    foot_note(
        "All states are derived from live backend signals — none are simulated.",
        "Run POST /api/pipeline/execute to re-run every stage from fresh telemetry.",
        "SMOTE-Tomek + Bayesian-Optimized SVM · Urban Zambia",
    )