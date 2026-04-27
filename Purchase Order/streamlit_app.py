import streamlit as st
import requests
import json
import re
import base64

st.set_page_config(
    page_title="SAP B1 Purchase Order Assistant",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
    background-color: #0d0f14;
    color: #e2e8f0;
}
#MainMenu, footer, header { visibility: hidden; }

.top-banner {
    background: linear-gradient(135deg, #1a1f2e 0%, #0f1623 100%);
    border: 1px solid #2a3550;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.top-banner::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 140px; height: 140px;
    background: radial-gradient(circle, rgba(56,189,248,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.top-banner h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.6rem; font-weight: 600; color: #38bdf8;
    margin: 0 0 6px 0; letter-spacing: -0.5px;
}
.top-banner p { color: #64748b; font-size: 0.88rem; margin: 0; font-weight: 300; }

.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase;
    color: #38bdf8; margin-bottom: 6px; display: block;
}

.badge-ok   { background:#134e26; color:#4ade80; border:1px solid #166534;
              padding:4px 12px; border-radius:20px; font-size:0.75rem;
              font-family:'IBM Plex Mono',monospace; display:inline-block; }
.badge-warn { background:#3b2a0a; color:#fbbf24; border:1px solid #92400e;
              padding:4px 12px; border-radius:20px; font-size:0.75rem;
              font-family:'IBM Plex Mono',monospace; display:inline-block; }

/* Chat bubbles */
.chat-wrap { display:flex; flex-direction:column; gap:14px; margin:8px 0; }

.bubble-user {
    align-self: flex-end;
    background: #1e3a5f; border: 1px solid #2a5080;
    border-radius: 14px 14px 3px 14px;
    padding: 12px 16px; max-width: 82%;
    font-size: 0.88rem; color: #e2e8f0; line-height: 1.55;
    white-space: pre-wrap;
}
.bubble-user .bubble-meta {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
    color: #38bdf8; margin-bottom: 5px; letter-spacing: 1px;
}

.bubble-bot {
    align-self: flex-start;
    background: #131929; border: 1px solid #1e2e45;
    border-radius: 14px 14px 14px 3px;
    padding: 12px 16px; max-width: 88%;
    font-size: 0.88rem; color: #cbd5e1; line-height: 1.6;
}
.bubble-bot .bubble-meta {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
    color: #64748b; margin-bottom: 5px; letter-spacing: 1px;
}
.bubble-bot.success   { border-left: 3px solid #4ade80; }
.bubble-bot.cancelled { border-left: 3px solid #f87171; }
.bubble-bot.closed    { border-left: 3px solid #fbbf24; }
.bubble-bot.error     { border-left: 3px solid #ef4444; }

.divider { border:none; border-top:1px solid #1e2940; margin:20px 0; }

textarea, input[type="text"], input[type="password"] {
    background-color: #131929 !important;
    border: 1px solid #2a3a55 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
textarea:focus, input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 2px rgba(56,189,248,0.15) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in {"token": None, "chat_history": [], "prompt_input": "", "selected_action": "create"}.items():
    if k not in st.session_state:
        st.session_state[k] = v

BULK_TEMPLATE_CSV = """order_id,card_code,doc_date,doc_due_date,tax_date,item_code,quantity,unit_price,tax_code
PO-BULK-001,V001,2026-04-27,2026-05-02,2026-05-02,ITEM123,10,50,T1
PO-BULK-001,V001,2026-04-27,2026-05-02,2026-05-02,ITEM456,5,35,T1
PO-BULK-002,V001,2026-04-28,2026-05-03,2026-05-03,ITEM123,3,50,T2
"""


def encode_uploaded_file(uploaded_file) -> str:
    return base64.b64encode(uploaded_file.getvalue()).decode("ascii")

ACTION_META = {
    "create": {"icon": "➕", "label": "Create Purchase Order",  "color": "#38bdf8",
               "example": "Create a purchase order for vendor V001 with 10 units of ITEM123 at $50 per unit with tax code T1 dated 2026-04-23 due 2026-04-30"},
    "cancel": {"icon": "🚫", "label": "Cancel Purchase Order",  "color": "#f87171",
               "example": "Cancel purchase order 12345"},
    "close":  {"icon": "🔒", "label": "Close Purchase Order",   "color": "#fbbf24",
               "example": "Close purchase order 12345"},
}

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-banner">
    <h1>🛒 SAP B1 Purchase Order Assistant</h1>
    <p>Create · Cancel · Close · OCR Read · Bulk Upload for SAP Business One purchase orders</p>
</div>
""", unsafe_allow_html=True)

# ── Auth ───────────────────────────────────────────────────────────────────────
st.markdown('<span class="section-label">⚙ API Configuration</span>', unsafe_allow_html=True)
base_url = st.text_input("Base URL", value="http://127.0.0.1:8002", key="base_url")

st.markdown('<span class="section-label" style="margin-top:14px;display:block;">🔐 Authentication</span>', unsafe_allow_html=True)
col_u, col_p, col_btn = st.columns([2, 2, 1])
with col_u:
    username = st.text_input("Username", value="user1")
with col_p:
    password = st.text_input("Password", type="password", placeholder="Enter password")
with col_btn:
    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
    if st.button("🔑 Login", key="btn_login", use_container_width=True):
        try:
            r = requests.post(f"{base_url}/login",
                              params={"username": username, "password": password}, timeout=10)
            if r.status_code == 200:
                st.session_state.token = r.json().get("access_token")
                st.success("✅ Authenticated!")
            else:
                st.session_state.token = None
                st.error(f"❌ Login failed {r.status_code}: {r.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")

if st.session_state.token:
    st.markdown('<span class="badge-ok">● TOKEN ACTIVE</span>', unsafe_allow_html=True)
    with st.expander("View Token"):
        st.code(st.session_state.token, language=None)
else:
    st.markdown('<span class="badge-warn">● NOT AUTHENTICATED</span>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Action Selector ────────────────────────────────────────────────────────────
st.markdown('<span class="section-label">⚡ Select Action</span>', unsafe_allow_html=True)

col_c, col_x, col_cl, col_rst = st.columns([2, 2, 2, 1])
with col_c:
    if st.button("➕ Create PO", key="btn_action_create", use_container_width=True,
                 type="primary" if st.session_state.selected_action == "create" else "secondary"):
        st.session_state.selected_action = "create"
        st.session_state.prompt_input = ACTION_META["create"]["example"]
        st.rerun()
with col_x:
    if st.button("🚫 Cancel PO", key="btn_action_cancel", use_container_width=True,
                 type="primary" if st.session_state.selected_action == "cancel" else "secondary"):
        st.session_state.selected_action = "cancel"
        st.session_state.prompt_input = ACTION_META["cancel"]["example"]
        st.rerun()
with col_cl:
    if st.button("🔒 Close PO", key="btn_action_close", use_container_width=True,
                 type="primary" if st.session_state.selected_action == "close" else "secondary"):
        st.session_state.selected_action = "close"
        st.session_state.prompt_input = ACTION_META["close"]["example"]
        st.rerun()
with col_rst:
    if st.button("🔄 Reset", key="btn_reset", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.prompt_input = ""
        st.rerun()

action = st.session_state.selected_action
ameta  = ACTION_META[action]
st.markdown(
    f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.72rem;'
    f'color:{ameta["color"]};margin:4px 0 12px 0;">'
    f'▶ Active: {ameta["icon"]} {ameta["label"]}</div>',
    unsafe_allow_html=True,
)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Conversation ───────────────────────────────────────────────────────────────
st.markdown('<span class="section-label">💬 Conversation</span>', unsafe_allow_html=True)

if not st.session_state.chat_history:
    st.markdown("""
    <div style="text-align:center;padding:32px 0;color:#2a3a55;
         font-family:'IBM Plex Mono',monospace;font-size:0.8rem;">
      Select an action above and enter your prompt below
    </div>""", unsafe_allow_html=True)
else:
    st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="bubble-user">
              <div class="bubble-meta">YOU</div>
              {msg["text"]}
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="bubble-bot {msg.get('type','')}">
              <div class="bubble-meta">SAP ASSISTANT</div>
              {msg["text"]}
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
prompt = st.text_area(
    label="prompt",
    value=st.session_state.prompt_input,
    height=90,
    placeholder=ameta["example"],
    key="prompt_area",
    label_visibility="collapsed",
)

st.markdown(f"""
<div style="background:#0f1a2a;border:1px solid #1e3a5f;border-radius:8px;
     padding:10px 14px;margin:8px 0;font-size:0.75rem;color:#64748b;
     font-family:'IBM Plex Mono',monospace;">
  POST <span style="color:#38bdf8">/purchase-orders/parse-and-execute</span>
  &nbsp;·&nbsp; action=<span style="color:{ameta['color']}">{action}</span>
  &nbsp;·&nbsp; Ollama llama3.1:8b → SAP B1
</div>""", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    submit = st.button(f"{ameta['icon']} {ameta['label']}", key="btn_submit", use_container_width=True,
                       type="primary", disabled=(not st.session_state.token))
with col2:
    show_raw = st.checkbox("Show JSON", value=False)

if not st.session_state.token:
    st.caption("⚠️ Login above to enable purchase order actions.")

# ── Submit ─────────────────────────────────────────────────────────────────────
if submit:
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        st.session_state.chat_history.append({"role": "user", "text": prompt.strip()})
        st.session_state.prompt_input = ""

        with st.spinner(f"Processing via Ollama → SAP B1..."):
            try:
                resp = requests.post(
                    f"{base_url}/purchase-orders/parse-and-execute",
                    json={"prompt": prompt.strip()},
                    headers={"Authorization": f"Bearer {st.session_state.token}",
                             "Content-Type": "application/json"},
                    timeout=120,
                )
                body = resp.json() if resp.headers.get("content-type","").startswith("application/json") else {"detail": resp.text}
                api_status = body.get("status", "error")
                doc_entry  = body.get("docEntry", "—")

                if api_status == "created":
                    bot_text = (
                        f'<strong style="color:#4ade80">✅ Purchase Order Created</strong><br><br>'
                        f'<span style="color:#94a3b8;font-family:\'IBM Plex Mono\',monospace;font-size:0.78rem;">SAP DocEntry</span><br>'
                        f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:2rem;font-weight:700;color:#4ade80;">{doc_entry}</span>'
                    )
                    st.session_state.chat_history.append({"role": "bot", "text": bot_text, "type": "success"})

                elif api_status == "cancelled":
                    bot_text = (
                        f'<strong style="color:#f87171">🚫 Purchase Order Cancelled</strong><br><br>'
                        f'<span style="color:#94a3b8;font-family:\'IBM Plex Mono\',monospace;font-size:0.78rem;">DocEntry</span><br>'
                        f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:2rem;font-weight:700;color:#f87171;">{doc_entry}</span><br>'
                        f'<span style="color:#64748b;font-size:0.78rem;">{body.get("message","")}</span>'
                    )
                    st.session_state.chat_history.append({"role": "bot", "text": bot_text, "type": "cancelled"})

                elif api_status == "closed":
                    bot_text = (
                        f'<strong style="color:#fbbf24">🔒 Purchase Order Closed</strong><br><br>'
                        f'<span style="color:#94a3b8;font-family:\'IBM Plex Mono\',monospace;font-size:0.78rem;">DocEntry</span><br>'
                        f'<span style="font-family:\'IBM Plex Mono\',monospace;font-size:2rem;font-weight:700;color:#fbbf24;">{doc_entry}</span><br>'
                        f'<span style="color:#64748b;font-size:0.78rem;">{body.get("message","")}</span>'
                    )
                    st.session_state.chat_history.append({"role": "bot", "text": bot_text, "type": "closed"})

                else:
                    detail = body.get("detail", str(body))
                    bot_text = (
                        f'<strong style="color:#ef4444">❌ Error (HTTP {resp.status_code})</strong><br>'
                        f'<span style="color:#f87171;">{detail}</span>'
                    )
                    st.session_state.chat_history.append({"role": "bot", "text": bot_text, "type": "error"})

                if show_raw:
                    st.session_state.chat_history.append({
                        "role": "bot",
                        "text": f'<pre style="font-size:0.72rem;color:#64748b;overflow-x:auto;">{json.dumps(body, indent=2)}</pre>',
                        "type": "",
                    })

            except requests.exceptions.ConnectionError:
                st.session_state.chat_history.append({
                    "role": "bot",
                    "text": f'<strong style="color:#ef4444">❌ Connection Error</strong><br>Cannot connect to <code>{base_url}</code>',
                    "type": "error",
                })
            except Exception as e:
                st.session_state.chat_history.append({
                    "role": "bot",
                    "text": f'<strong style="color:#ef4444">❌ Error</strong><br>{str(e)}',
                    "type": "error",
                })

        st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<span class="section-label">📄 OCR Reading - Upload Document</span>', unsafe_allow_html=True)
ocr_file = st.file_uploader(
    "Upload a document for OCR",
    type=["pdf", "png", "jpg", "jpeg", "tif", "tiff", "heic", "txt", "csv", "json", "md"],
    key="ocr_file_uploader",
)
ocr_col1, ocr_col2 = st.columns([1, 4])
with ocr_col1:
    run_ocr = st.button("Read Document", use_container_width=True, disabled=(not st.session_state.token))
with ocr_col2:
    st.caption("Supported: PDF, images, and text-based files. PDF/image OCR uses native macOS Vision.")

if run_ocr:
    if not ocr_file:
        st.warning("Upload a document first.")
    else:
        with st.spinner("Reading document..."):
            try:
                resp = requests.post(
                    f"{base_url}/purchase-orders/ocr-read",
                    json={
                        "filename": ocr_file.name,
                        "content_base64": encode_uploaded_file(ocr_file),
                    },
                    headers={
                        "Authorization": f"Bearer {st.session_state.token}",
                        "Content-Type": "application/json",
                    },
                    timeout=180,
                )
                body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"detail": resp.text}
                if resp.status_code == 200:
                    extracted_text = body.get("data", {}).get("extractedText", "")
                    st.success(body.get("message", "Document read successfully."))
                    st.text_area("Extracted text", extracted_text, height=280)
                else:
                    st.error(body.get("detail", f"OCR request failed with HTTP {resp.status_code}"))
            except Exception as e:
                st.error(f"OCR error: {e}")

st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<span class="section-label">📊 Excel Upload - Bulk Purchase Order</span>', unsafe_allow_html=True)
st.download_button(
    "Download CSV Template",
    data=BULK_TEMPLATE_CSV,
    file_name="bulk_purchase_orders_template.csv",
    mime="text/csv",
    use_container_width=True,
)
bulk_file = st.file_uploader(
    "Upload CSV or XLSX",
    type=["csv", "xlsx"],
    key="bulk_po_uploader",
)
bulk_dry_run = st.checkbox("Preview only (do not create in SAP)", value=True, key="bulk_preview_only")
bulk_submit = st.button("Process Bulk Purchase Orders", use_container_width=True, disabled=(not st.session_state.token))

if bulk_submit:
    if not bulk_file:
        st.warning("Upload a CSV or XLSX file first.")
    else:
        with st.spinner("Validating bulk purchase orders..."):
            try:
                resp = requests.post(
                    f"{base_url}/purchase-orders/bulk-upload",
                    json={
                        "filename": bulk_file.name,
                        "content_base64": encode_uploaded_file(bulk_file),
                        "dryRun": bulk_dry_run,
                    },
                    headers={
                        "Authorization": f"Bearer {st.session_state.token}",
                        "Content-Type": "application/json",
                    },
                    timeout=240,
                )
                body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {"detail": resp.text}
                if resp.status_code == 200:
                    data = body.get("data", {})
                    st.success(body.get("message", "Bulk upload completed."))
                    metric_cols = st.columns(3)
                    metric_cols[0].metric("Orders", data.get("totalOrders", 0))
                    if data.get("mode") == "preview":
                        metric_cols[1].metric("Lines", data.get("totalLines", 0))
                    else:
                        metric_cols[1].metric("Created", data.get("successfulOrders", 0))
                    metric_cols[2].metric("Mode", data.get("mode", "unknown"))
                    st.json(data)
                else:
                    st.error(body.get("detail", f"Bulk upload failed with HTTP {resp.status_code}"))
            except Exception as e:
                st.error(f"Bulk upload error: {e}")

st.markdown("""
<hr class="divider">
<div style="text-align:center;font-family:'IBM Plex Mono',monospace;font-size:0.68rem;color:#2a3a55;padding:8px 0;">
SAP B1 Purchase Order Agent · FastAPI + Groq · Create · Cancel · Close · OCR · Bulk Upload
</div>""", unsafe_allow_html=True)
