def translate_sap_error(error_text: str) -> str:
    if "Business Partner not found" in error_text:
        return "Vendor not found in SAP. Please provide a valid CardCode."
    if "Item not found" in error_text:
        return "Item not found in SAP. Please provide a valid ItemCode."
    if "AP Invoice not found" in error_text:
        return "AP Invoice not found in SAP. Please verify the DocEntry."
    return f"SAP Error: {error_text}"
