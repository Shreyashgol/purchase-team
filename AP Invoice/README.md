# SAP B1 AP Invoice Agent

Separate FastAPI + Streamlit agent for SAP Business One AP invoices.

## Features

- Create AP invoices from natural-language prompts
- Fetch AP invoice details by invoice number / DocEntry
- JWT-protected API matching the Purchase Order app pattern
- SAP Service Layer integration through `/PurchaseInvoices`

## Project Structure

```text
AP Invoice/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── agents.py/
│   │   ├── create_agent.py
│   │   └── fetch_agent.py
│   ├── api/
│   │   ├── auth.py
│   │   └── ap_invoices.py
│   ├── crud/
│   │   └── ap_invoice_crud.py
│   ├── model/
│   │   └── ap_invoice_intent.py
│   ├── operations/
│   │   ├── error_handler.py
│   │   ├── intent_parser.py
│   │   ├── sap_client.py
│   │   └── utils.py
│   └── schema/
│       ├── ap_invoice.py
│       ├── auth.py
│       └── response.py
├── requirements.txt
└── streamlit_app.py
```

## Run

```bash
cd "/Users/shreyashgolhani/Desktop/sap /AP Invoice"
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8003 --reload
python -m streamlit run streamlit_app.py
```

## API Endpoints

- `POST /login`
- `POST /ap-invoices/parse-and-execute`

## Example Prompts

- `Create an AP invoice for vendor V001 with 2 units of ITEM123 at 150 each due 2026-05-05`
- `Fetch AP invoice 5001`
