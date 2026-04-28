import json

import requests
import streamlit as st


st.set_page_config(
    page_title="SAP B1 AP Invoice Assistant",
    page_icon="🧾",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0e1311;
    color: #e5f3eb;
}
#MainMenu, footer, header { visibility: hidden; }
.top-banner {
    background: linear-gradient(135deg, #13211d 0%, #0b1613 100%);
    border: 1px solid #1f3a31;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 24px;
}
.top-banner h1 {
    font-family: 'IBM Plex Mono', monospace;
    color: #5eead4;
    margin: 0 0 6px 0;
}
.top-banner p {
    color: #86a89a;
    margin: 0;
}
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #5eead4;
    margin-bottom: 6px;
    display: block;
}
.divider { border: none; border-top: 1px solid #1f312b; margin: 20px 0; }
</style>
""",
    unsafe_allow_html=True,
)

if "token" not in st.session_state:
    st.session_state.token = None
if "invoice_action" not in st.session_state:
    st.session_state.invoice_action = "create"

ACTION_META = {
    "create": {
        "label": "Create AP Invoice",
        "endpoint": "/ap-invoices/parse-and-execute",
        "example": "Create an AP invoice for vendor V001 with 2 units of ITEM123 at 150 each with tax code T1",
    },
    "fetch": {
        "label": "Fetch AP Invoice",
        "endpoint": "/ap-invoices/parse-and-execute",
        "example": "Show me the latest 5 AP invoices for vendor V001",
    },
}

st.markdown(
    """
<div class="top-banner">
    <h1>🧾 SAP B1 AP Invoice Assistant</h1>
    <p>Schema-driven AP invoice creation with CardCode and DocumentLines, plus Text-to-SQL fetch.</p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown('<span class="section-label">⚙ API Configuration</span>', unsafe_allow_html=True)
base_url = st.text_input("Base URL", value="http://127.0.0.1:8003")

st.markdown('<span class="section-label">🔐 Authentication</span>', unsafe_allow_html=True)
username = st.text_input("Username", value="user1")
password = st.text_input("Password", type="password", placeholder="Enter password")
if st.button("Login", use_container_width=True):
    try:
        response = requests.post(f"{base_url}/login", params={"username": username, "password": password}, timeout=10)
        if response.status_code == 200:
            st.session_state.token = response.json()["access_token"]
            st.success("Authenticated.")
        else:
            st.error(response.text)
    except Exception as exc:
        st.error(f"Connection error: {exc}")

st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<span class="section-label">⚡ Select Action</span>', unsafe_allow_html=True)
create_col, fetch_col = st.columns(2)
with create_col:
    if st.button("Create Agent", use_container_width=True, type="primary" if st.session_state.invoice_action == "create" else "secondary"):
        st.session_state.invoice_action = "create"
        st.rerun()
with fetch_col:
    if st.button("Fetch Agent", use_container_width=True, type="primary" if st.session_state.invoice_action == "fetch" else "secondary"):
        st.session_state.invoice_action = "fetch"
        st.rerun()

action = st.session_state.invoice_action
meta = ACTION_META[action]
prompt = st.text_area("Prompt", value=meta["example"], height=120)
show_raw = st.checkbox("Show JSON", value=False)
submit = st.button(meta["label"], use_container_width=True, disabled=not st.session_state.token)

if submit:
    if not prompt.strip():
        st.warning("Enter a prompt first.")
    else:
        try:
            response = requests.post(
                f"{base_url}{meta['endpoint']}",
                json={"prompt": prompt.strip()},
                headers={"Authorization": f"Bearer {st.session_state.token}", "Content-Type": "application/json"},
                timeout=120,
            )
            body = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"detail": response.text}
            if response.status_code == 200:
                st.success(body.get("message", "Request completed."))
                if body.get("docEntry") is not None:
                    st.metric("DocEntry", body["docEntry"])
                if body.get("data"):
                    st.json(body["data"])
            else:
                st.error(body.get("detail", f"Request failed with HTTP {response.status_code}"))

            if show_raw:
                st.code(json.dumps(body, indent=2), language="json")
        except Exception as exc:
            st.error(f"Error: {exc}")
