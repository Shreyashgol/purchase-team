# SAP B1 Purchase Order Agent

Multi-agent orchestration system for SAP Business One Purchase Orders using FastAPI, Ollama (llama3.1:8b), and LangGraph.

## Overview

This system enables users to create, update, cancel, close, and fetch purchase orders using natural language queries. It also supports OCR-based document reading and bulk purchase-order uploads from CSV/XLSX files. It follows the same architecture as the Sales Order Agent but with purchase order-specific logic.


### 1. **Schema**
- **Entity**: Purchase Orders (`/PurchaseOrders`) 
- **Business Partner Type**: Vendors (CardType = 'S') 
- **Tables**: OPOR (header) and POR1 (line items) 

### 2. **Endpoints**
- Main endpoint: `POST /purchase-orders/parse-and-execute`
- SAP endpoints: `/PurchaseOrders`, `/PurchaseOrders({DocEntry})/Cancel`, `/PurchaseOrders({DocEntry})/Close`

### 3. **Core Logic Differences**

#### Create Operation
- Validates **vendors** (not customers) via SQL
- Includes **unitPrice** and **taxCode** in line items
- Example: "Create a purchase order for vendor V001 with 10 units of ITEM123 at $50 per unit with tax code T1"

#### Cancel Operation
- Supports cancel by **mobile number** (queries OPOR.U_MobileNumber)
- Example: "Cancel purchase order for mobile number +1234567890"

#### Fetch Operation (TODO)
- Text-to-SQL conversion for natural language queries
- Queries OPOR and POR1 tables
- Returns natural language responses with charts and suggestions
- Example: "Show me all open purchase orders for vendor V001"

## Project Structure

```
Purchase Order/
├── app/
│   ├── main.py                      # FastAPI entrypoint
│   ├── config.py                    # Configuration (SAP, JWT, Ollama, SQL)
│   ├── routers/
│   │   ├── auth.py                  # Authentication endpoints
│   │   └── purchase_orders.py       # Purchase order endpoints
│   ├── services/
│   │   ├── sap_client.py            # SAP Service Layer client (PO methods)
│   │   ├── po_intent_parser.py      # LLM parsing for purchase orders
│   │   ├── intent_parser.py         # Original sales order parser
│   │   ├── text_to_sql.py           # TODO: Text-to-SQL conversion
│   │   ├── sql_executor.py          # TODO: SQL query execution
│   │   ├── response_generator.py    # TODO: NL response generation
│   │   └── validator.py             # Pydantic validation
│   ├── models/
│   │   ├── intent.py                # Sales order intent schema
│   │   └── po_intent.py             # Purchase order intent schema
│   └── utils/
│       ├── jwt_auth.py              # JWT authentication
│       └── error_handler.py         # Error translation
├── streamlit_app.py                 # Streamlit UI for PO operations
├── requirements.txt                 # Python dependencies
└── .kiro/specs/purchase-order-agent/
    ├── requirements.md              # Requirements document
    └── .config.kiro                 # Spec configuration
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (or use defaults in config.py)
export SAP_BASE_URL="https://your-sap-server:50000/b1s/v1"
export SAP_USERNAME="your_username"
export SAP_PASSWORD="your_password"
export SAP_COMPANYDB="your_company_db"
```

## Running the Application

### Start FastAPI Backend
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```

### Start Streamlit UI
```bash
python -m streamlit run streamlit_app.py
```

## New Upload Workflows

### OCR Reading - Upload Document
- Streamlit section: `OCR Reading - Upload Document`
- Backend endpoint: `POST /purchase-orders/ocr-read`
- Supported file types: `pdf`, `png`, `jpg`, `jpeg`, `tif`, `tiff`, `heic`, `txt`, `csv`, `json`, `md`

### Excel Upload - Bulk Purchase Order
- Streamlit section: `Excel Upload - Bulk Purchase Order`
- Backend endpoint: `POST /purchase-orders/bulk-upload`
- Supported file types: `csv`, `xlsx`
- Recommended columns:
  - `order_id`
  - `card_code`
  - `doc_date`
  - `doc_due_date`
  - `tax_date`
  - `item_code`
  - `quantity`
  - `unit_price`
  - `tax_code`

## Sibling Agent

AP invoice work now lives in a separate root-level folder:

```text
/Users/shreyashgolhani/Desktop/sap /AP Invoice
```

That app contains dedicated `create` and `fetch` subagents for AP invoice operations.

## Shared PostgreSQL Pattern

The repository now uses one shared PostgreSQL runtime pattern for current and future agents:

- shared DB helper package: `/Users/shreyashgolhani/Desktop/sap /shared/db`
- common connection env support: `SAP_AGENTS_DATABASE_URL`
- fallback support still works for `DATABASE_CONNECTION_STRING` and `DATABASE_URL`

Each agent keeps its own tables, but all agents can use the same PostgreSQL database instance.

## API Examples

### 1. Login
```bash
curl -X POST "http://127.0.0.1:8002/login?username=user1&password=pass123456"
```

### 2. Create Purchase Order
```bash
curl -X POST "http://127.0.0.1:8002/purchase-orders/parse-and-execute" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Create a purchase order for vendor V001 with 10 units of ITEM123 at $50 per unit with tax code T1 dated 2026-04-23 due 2026-04-30"
  }'
```

### 3. Cancel Purchase Order
```bash
curl -X POST "http://127.0.0.1:8002/purchase-orders/parse-and-execute" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Cancel purchase order 12345"
  }'
```

### 4. Close Purchase Order
```bash
curl -X POST "http://127.0.0.1:8002/purchase-orders/parse-and-execute" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Close purchase order 12345"
  }'
```

## SAP Purchase Order Schema

### Header Fields (OPOR)
- **DocEntry**: Internal ID
- **DocNum**: PO Number (user-facing)
- **DocDate**: Order Date
- **DocDueDate**: Expected Delivery Date
- **DocStatus**: Open / Closed
- **CANCELED**: Cancellation flag
- **CardCode**: Vendor Code
- **CardName**: Vendor Name
- **DocTotal**: Total Amount
- **VatSum**: Tax Amount
- **DiscSum**: Discount Amount

### Line Item Fields (POR1)
- **ItemCode**: Item/Product Code
- **ItemDescription**: Item Name
- **Quantity**: Order Quantity
- **Price**: Unit Price
- **TaxCode**: Tax Code
- **LineTotal**: Line Total Amount

## TODO: Fetch Agent Implementation

The Fetch Agent will include:

1. **Text-to-SQL Service** (`app/services/text_to_sql.py`)
   - Convert natural language to SQL queries
   - Target OPOR and POR1 tables
   - Example: "Show open POs for vendor V001" → `SELECT * FROM OPOR WHERE CardCode='V001' AND DocStatus='O'`

2. **SQL Executor** (`app/services/sql_executor.py`)
   - Execute read-only SQL queries
   - Validate queries (no INSERT/UPDATE/DELETE)
   - 30-second timeout

3. **Response Generator** (`app/services/response_generator.py`)
   - Convert SQL results to natural language
   - Generate chart specifications (bar, line, pie)
   - Provide actionable suggestions

### Example Fetch Response
```json
{
  "status": "success",
  "message": "You have 3 open purchase orders for vendor V001 with a total value of $10,000.",
  "data": {
    "rows": [
      {"DocNum": "PO-001", "DocTotal": 5000, "DocDueDate": "2026-04-25"},
      {"DocNum": "PO-002", "DocTotal": 3000, "DocDueDate": "2026-04-28"},
      {"DocNum": "PO-003", "DocTotal": 2000, "DocDueDate": "2026-05-01"}
    ],
    "chart": {
      "type": "bar",
      "title": "Purchase Orders by Amount",
      "xAxis": ["PO-001", "PO-002", "PO-003"],
      "yAxis": [5000, 3000, 2000]
    },
    "suggestions": [
      "Would you like to see the line items for any of these orders?",
      "Consider reviewing PO-001 as it's due soon (Apr 25)"
    ]
  }
}
```

## Technologies

- **FastAPI**: REST API framework
- **Ollama (llama3.1:8b)**: Local LLM for intent parsing and NL generation
- **LangGraph**: Multi-agent orchestration (TODO)
- **SAP Service Layer**: SAP Business One REST API
- **Streamlit**: Web UI
- **Pydantic**: Data validation
- **JWT**: Authentication

## License

Internal use only.
