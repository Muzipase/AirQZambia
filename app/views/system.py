"""Platform — environment health, validations and system testing behind a single console."""

import importlib.metadata
import subprocess
import sys
from pathlib import Path

import streamlit as st

from style_assets import (
    banner,
    foot_note,
    hero,
    kpi_grid,
    panel_close,
    panel_open,
    section_label,
    status_list,
)
from state import fetch_api_status, get_model_names

ROOT = Path(__file__).resolve().parents[2]

DEPENDENCIES = {
    "pandas": "pandas",
    "numpy": "numpy",
    "scikit-learn": "sklearn",
    "streamlit": "streamlit",
    "plotly": "plotly",
    "matplotlib": "matplotlib",
    "pytest": "pytest",
    "optuna": "optuna",
    "shap": "shap",
    "imbalanced-learn": "imblearn",
}

VIEW_FILES = [
    "app/views/overview.py",
    "app/views/predictions.py",
    "app/views/history.py",
    "app/views/evaluation.py",
    "app/views/explainability.py",
    "app/views/progress.py",
    "app/views/system.py",
]


def _get_dependency_versions():
    """Map of dependency name -> installed version (or None when missing)."""
    versions = {}
    for distro, module in DEPENDENCIES.items():
        try:
            __import__(module)
            versions[distro] = importlib.metadata.version(distro)
        except Exception:
            versions[distro] = None
    return versions


def _run_command(command, timeout=120):
    """Run a subprocess command synchronously, returning (returncode, combined stdout+stderr)."""
    try:
        result = subprocess.run(
            command, cwd=ROOT, capture_output=True, text=True, shell=False, timeout=timeout
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired as exc:
        return 1, f"Command timed out after {timeout} seconds:\n{exc}"
    except FileNotFoundError as exc:
        return 1, f"Command not found: {exc}"


def _report(title, ok, output):
    """Show a pass/fail spotlight card and an expander with the raw validation command output."""
    from style_assets import spotlight

    spotlight(
        "PASS" if ok else "FAIL",
        title,
        "Validation ran on the active interpreter against the project root."
        if ok else "Validation failed — review the command output below.",
        badge_text="Check completed" if ok else "Check failed",
        badge_style="background:#f0fdf4;color:#15803d;" if ok
        else "background:#fef2f2;color:#dc2626;",
    )
    with st.expander("Command output", expanded=not ok):
        st.code(output or "(no output)")


def render():
    """Render the System Health page: dependencies, codebase compilation, test suite and validation checks."""
    stats = fetch_api_status()
    model_names = get_model_names(stats)

    hero(
        "Platform Operations",
        "System Health & Validation Console",
        "Verify dependencies, compile the codebase, run the test suite and "
        "confirm every dashboard screen is healthy before public use.",
        chips=[
            ("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", "good"),
            ("Backend", "Online" if stats else "Offline", "good" if stats else "bad"),
            ("Models", f"{len(model_names)} loaded" if model_names else "None",
             "good" if model_names else "bad"),
        ],
        breadcrumb=True,
    )

    versions = _get_dependency_versions()
    ok_count = sum(1 for v in versions.values() if v)

    kpi_grid(
        [
            ("Python", f"{sys.version_info.major}.{sys.version_info.minor}", "interpreter", "ok", "cpu"),
            ("Project root", ROOT.name, "workspace folder", "ok", "layers"),
            ("Dependencies", f"{ok_count}/{len(versions)}", "installed & importable",
             "ok" if ok_count == len(versions) else "warn", "database"),
            ("Backend", "Online" if stats else "Offline", "FastAPI @ :8000",
             "ok" if stats else "warn", "activity"),
        ]
    )

    section_label("Runtime status")
    status_list(
        [
            ("Backend API", "Online" if stats else "Offline", "good" if stats else "bad"),
            ("Model registry", ", ".join(model_names) if model_names else "Empty",
             "good" if model_names else "warn"),
            ("Data pool", "Available" if (stats or {}).get("data", {}).get("raw_data") else "N/A",
             "good" if (stats or {}).get("data", {}).get("raw_data") else "warn"),
            ("Dependencies", f"{ok_count}/{len(versions)} OK", "good" if ok_count == len(versions) else "warn"),
        ]
    )

    panel_open(
        "Environment",
        "cpu",
        "Runtime identity and installed dependency versions.",
    )
    c_l, c_r = st.columns(2)
    with c_l:
        st.markdown(
            f"**Python executable:** `<code>{sys.executable}</code>`<br/>"
            f"**Python version:** {sys.version.splitlines()[0]}<br/>"
            f"**Project root:** `<code>{ROOT}</code>`",
            unsafe_allow_html=True,
        )
    with c_r:
        for distro, version in versions.items():
            if version:
                st.markdown(f"**{distro}** — `{version}`")
            else:
                st.markdown(f"**{distro}** — *missing*")
    panel_close()

    panel_open(
        "System testing controls",
        "wrench",
        "Run validation flows below. Long-running tests execute against the active interpreter.",
    )
    c_env, c_code, c_test, c_probe = st.columns(4)
    with c_env:
        run_env = st.button("Check environment", key="sys_env")
    with c_code:
        run_code = st.button("Validate code", key="sys_code")
    with c_test:
        run_test = st.button("Run unit tests", key="sys_tests")
    with c_probe:
        run_probe = st.button("Probe pages", key="sys_pages")

    if run_env:
        st.subheader("Environment summary")
        missing = [d for d, v in versions.items() if not v]
        if not missing:
            banner("info", "All core dependencies are installed and importable.")
        else:
            banner("err", "Missing dependencies: " + ", ".join(f"`{m}`" for m in missing))

    if run_code:
        with st.spinner("Compiling the codebase for syntax errors..."):
            rc, output = _run_command(
                [sys.executable, "-m", "compileall", "-q", "src/", "app/", "tests/", "config/"]
            )
        _report("Code validation", rc == 0, output)

    if run_test:
        with st.spinner("Running the unit test suite — this can take a few minutes..."):
            rc, output = _run_command(
                [sys.executable, "-m", "pytest", "tests/", "-q", "--disable-warnings"],
                timeout=300,
            )
        _report("Unit tests", rc == 0, output)

    if run_probe:
        with st.spinner("Checking dashboard screens compile cleanly..."):
            results = []
            for rel in VIEW_FILES:
                path = ROOT / rel
                try:
                    compile(path.read_text(encoding="utf-8"), str(path), "exec")
                    results.append((rel, True))
                except Exception as exc:
                    results.append((rel, False, str(exc)))
            status_list(
                [
                    (f"{'ok' if ok else 'fail'} · {rel}", "OK" if ok else "FAIL",
                     "good" if ok else "bad")
                    for rel, ok, *_ in results
                ]
            )
    panel_close()

    foot_note(
        "Run 'Check environment' and 'Validate code' before each deployment.",
        "Unit tests execute the suite in tests/ using the active interpreter.",
        "Status indicators reflect real runtime checks — no simulated health data.",
    )