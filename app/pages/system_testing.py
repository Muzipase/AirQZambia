import subprocess
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]

st.set_page_config(page_title='System Testing', page_icon='🧪', layout='wide')

st.title('System Testing & Validation')
st.markdown(
    'Run environment health checks, unit/integration tests, and app validation from a single interface.'
)

st.markdown(
    'This page is designed for system testing: validate dependencies, compile your code, run unit tests, and verify the Streamlit application pipeline.'
)


@st.cache_data
def get_runtime_info():
    return {
        'python_executable': sys.executable,
        'python_version': sys.version.split('\n')[0],
        'working_directory': str(ROOT),
    }


def get_dependency_versions():
    packages = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'scikit-learn': 'sklearn',
        'streamlit': 'streamlit',
        'plotly': 'plotly',
        'matplotlib': 'matplotlib',
        'pytest': 'pytest',
        'optuna': 'optuna',
        'shap': 'shap',
        'imbalanced-learn': 'imblearn',
    }
    versions = {}
    for distro, module in packages.items():
        try:
            __import__(module)
            import importlib.metadata as metadata
            versions[distro] = metadata.version(distro)
        except Exception:
            versions[distro] = None
    return versions


def run_command(command, timeout=120):
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            shell=False,
            timeout=timeout,
        )
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired as exc:
        return 1, f'Command timed out after {timeout} seconds:\n{exc}'
    except FileNotFoundError as exc:
        return 1, f'Command not found: {exc}'


st.sidebar.header('Quick Actions')
if st.sidebar.button('Run Environment Check'):
    st.session_state.run_check = 'env'
if st.sidebar.button('Run Code Validation'):
    st.session_state.run_check = 'validate'
if st.sidebar.button('Run Unit Tests'):
    st.session_state.run_check = 'pytest'
if st.sidebar.button('Run Functional Demo'):
    st.session_state.run_check = 'demo'
if st.sidebar.button('Run Streamlit Health Check'):
    st.session_state.run_check = 'pages'

if 'run_check' not in st.session_state:
    st.session_state.run_check = None

info = get_runtime_info()
st.subheader('Environment Overview')
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**Python executable:** `{info['python_executable']}`")
    st.markdown(f"**Python version:** {info['python_version']}")
    st.markdown(f"**Project root:** `{info['working_directory']}`")

with col2:
    st.markdown('**Dependency versions**')
    versions = get_dependency_versions()
    for dependency, version in versions.items():
        status = '✅' if version else '❌'
        st.markdown(f'- {status} **{dependency}**: {version or "missing"}')

st.markdown('---')

st.subheader('System Testing Controls')
st.write('Use the buttons in the sidebar to execute system validation flows.')

if st.session_state.run_check == 'env':
    st.info('Running environment dependency check...')
    st.success('Environment check complete. Review the dependency list above.')

if st.session_state.run_check == 'validate':
    with st.spinner('Compiling all source files for syntax validation...'):
        code = [
            sys.executable,
            '-m',
            'compileall',
            '-q',
            'src/',
            'app/',
            'tests/',
            'config/',
        ]
        rc, output = run_command(code)
    st.subheader('Code Validation Result')
    if rc == 0:
        st.success('✅ Code validation passed. All files compiled successfully.')
    else:
        st.error('❌ Code validation failed. Review the output below.')
    st.code(output)

if st.session_state.run_check == 'pytest':
    with st.spinner('Running unit tests... this may take a few minutes.'):
        command = [sys.executable, '-m', 'pytest', 'tests/', '-q', '--disable-warnings']
        rc, output = run_command(command, timeout=240)
    st.subheader('Unit Test Result')
    if rc == 0:
        st.success('✅ All unit tests passed.')
    else:
        st.error('❌ Unit tests failed or could not run.')
    st.code(output)

if st.session_state.run_check == 'demo':
    with st.spinner('Running the functional demo script...'):
        command = [sys.executable, 'demo_functional.py']
        rc, output = run_command(command, timeout=180)
    st.subheader('Functional Demo Result')
    if rc == 0:
        st.success('✅ Functional demo ran successfully.')
    else:
        st.error('❌ Functional demo failed or timed out.')
    st.code(output)

if st.session_state.run_check == 'pages':
    with st.spinner('Checking Streamlit page imports...'):
        pages = [
            'app/pages/dashboard.py',
            'app/pages/evaluation.py',
            'app/pages/predictions.py',
            'app/pages/shap_analysis.py',
            'app/pages/system_testing.py',
        ]
        results = []
        for page in pages:
            page_path = ROOT / page
            try:
                compile(page_path.read_text(encoding='utf-8'), str(page_path), 'exec')
                results.append((page, True, 'Compiled successfully'))
            except Exception as exc:
                results.append((page, False, str(exc)))
    st.subheader('Streamlit Page Health')
    for page, success, message in results:
        if success:
            st.success(f'✅ {page}: {message}')
        else:
            st.error(f'❌ {page}: {message}')

st.markdown('---')
st.subheader('System Testing Guidance')
st.markdown(
    '- **Environment Check**: verify required packages are installed.\n'
    '- **Code Validation**: compile all Python modules for syntax errors.\n'
    '- **Unit Tests**: run the test suite in `tests/`.\n'
    '- **Functional Demo**: execute the end-to-end demo script.\n'
    '- **Streamlit Health Check**: ensure page modules import cleanly.\n'
)
