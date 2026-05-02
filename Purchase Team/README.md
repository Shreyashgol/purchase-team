# Purchase Team Supervisor Flow


1. User sends a natural-language purchase-team request.
2. `supervisor_agent` routes the request to `fetch_agent`.
3. `fetch_agent` decides which document agent should handle it:
   - `purchase_order_agent`
   - `ap_invoice_agent`
   - `purchase_return_agent`
4. The selected document agent handles its own `create`, `fetch`, `update`, `close`, or `cancel` subagent.

