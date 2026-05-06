# SAP Purchase Supervisor Agent

Unified SAP Business One purchase-agent workspace with one FastAPI backend and one Streamlit Supervisor UI.

The old split folders have been consolidated into a single `app/` package. Purchase order, AP invoice, and purchase return agents now live as subfolders under `app/agents/`, while shared API, CRUD, DB, model, operations, and schema code stays in top-level package folders.

## Folder Structure

```text
sap/
├── .env.example
├── README.md
├── requirements.txt
├── streamlit_app.py
├── app/
│   ├── main.py
│   ├── config.py
│   ├── chat_response.py
│   ├── agents/
│   │   ├── supervisor/
│   │   ├── purchase_order/
│   │   ├── ap_invoice/
│   │   └── purchase_return/
│   ├── api/
│   │   ├── auth.py
│   │   ├── purchase_orders.py
│   │   ├── ap_invoices.py
│   │   └── purchase_returns.py
│   ├── crud/
│   │   ├── purchase_order_crud.py
│   │   ├── ap_invoice_crud.py
│   │   └── purchase_return_crud.py
│   ├── db/
│   │   ├── base.py
│   │   ├── purchase_order_db.py
│   │   ├── purchase_order_models.py
│   │   ├── ap_invoice_db.py
│   │   ├── ap_invoice_models.py
│   │   ├── purchase_return_db.py
│   │   └── purchase_return_models.py
│   ├── model/
│   ├── operations/
│   └── schema/
└── shared/
    ├── env.py
    └── db/
        └── runtime.py
```

## What Works

- One Streamlit Supervisor Agent UI that routes purchase order, AP invoice, and purchase return prompts.
- Supervisor routing for purchase order, AP invoice, and purchase return prompts.
- Purchase order create, update, fetch, close, cancel.
- AP invoice create, update, fetch, close, cancel, reopen.
- Purchase return create, update, fetch, close, cancel, reopen.
- Purchase order OCR document reading.
- Purchase order bulk CSV/XLSX upload.
- JWT login shared by all endpoints.
- Neon/Postgres database connection shared by all agents.

## Setup

Create and configure your environment:

```bash
cp .env.example .env
```

Install dependencies:

```bash
python3 -m venv myvenv
./myvenv/bin/python -m pip install -r requirements.txt
```

If `myvenv` already exists, just run the install command.

## Environment

Important `.env` values:

```bash
SAP_AGENTS_DATABASE_URL=postgresql://username:password@host:5432/sap_agents_db?sslmode=require
SAP_BASE_URL=http://localhost:50000/b1s/v1
SAP_USERNAME=manager
SAP_PASSWORD=password
SAP_COMPANYDB=SBODEMOUS
JWT_SECRET=change-me
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
SQL_QUERY_TIMEOUT=30
```

`SAP_AGENTS_DATABASE_URL` is the preferred Neon/Postgres variable. Legacy `DATABASE_CONNECTION_STRING` and `DATABASE_URL` still work through the shared runtime fallback.

## Start The Backend

From the repository root:

```bash
./myvenv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Check it:

```bash
curl http://127.0.0.1:8000/
```

## Start Streamlit

Open a second terminal from the repository root:

```bash
./myvenv/bin/python -m streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

Then open:

```text
http://127.0.0.1:8501
```

In the sidebar, keep the FastAPI URL as:

```text
http://127.0.0.1:8000
```

Default demo login:

```text
username: user1
password: pass123456
```

The UI intentionally exposes only the Supervisor Agent. Users should type every request into the supervisor chat; the supervisor then routes to the correct document agent internally.

## API Examples

Get a JWT token:

```bash
curl -X POST "http://127.0.0.1:8000/login?username=user1&password=pass123456"
```

Run a purchase order prompt:

```bash
TOKEN="paste-token-here"

curl -X POST "http://127.0.0.1:8000/purchase-orders/parse-and-execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Show me the latest 5 purchase orders"}'
```

Run an AP invoice prompt:

```bash
curl -X POST "http://127.0.0.1:8000/ap-invoices/parse-and-execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Show me the latest 5 AP invoices"}'
```

Run a purchase return prompt:

```bash
curl -X POST "http://127.0.0.1:8000/purchase-returns/parse-and-execute" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Show me the latest 5 purchase returns"}'
```

## Verification

Compile and import-check the consolidated app:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m compileall app streamlit_app.py

PYTHONDONTWRITEBYTECODE=1 ./myvenv/bin/python - <<'PY'
from app.main import app
from app.agents.supervisor.supervisor_agent import execute
print(app.title)
print(len(app.routes))
print(execute("show latest purchase orders").data["fetchAgent"]["documentType"])
PY
```

Expected output includes:

```text
SAP B1 Purchase Supervisor Agent
11
purchase_order
```

## Development Notes

- Keep new code inside the unified `app/` package.
- Add document-agent logic under `app/agents/<agent_name>/`.
- Add SAP endpoints under `app/api/`.
- Add repository/CRUD logic under `app/crud/`.
- Add Neon/Postgres database logic under `app/db/`.
- Add intent/data models under `app/model/`.
- Add shared and document-specific operations under `app/operations/`.
- Add request/response schemas under `app/schema/`.
- Keep secrets in `.env`; do not commit real credentials.
