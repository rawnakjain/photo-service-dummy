"""
Prompt templates for salon menu extraction using Gemini Flash.
"""

# This prompt is adapted from the image-to-text project's PROMPT constant
SALON_MENU_EXTRACTION_PROMPT = (
    "This image is a page from a salon or beauty parlour price menu. Extract every "
    "service and its price into the provided schema.\n"
    "\n"
    "Rules:\n"
    "- One entry per service as printed. Never invent, merge, or reorder services, and "
    "never translate the service names.\n"
    "- Use the menu's own section headings as category names, in capitals as printed. "
    "Bridal and package sections are categories too. A service is one row under a "
    "heading. But when one row or one entry offers numbered or named choices — "
    "'Option 1' / 'Option 2', or tiers like 'Sugar' / 'Cream' / 'Rica' — those choices "
    "are *variants of that one service*, not separate services.\n"
    "- A service with more than one price gets one variant per price. When the menu "
    "labels the prices (for example 'Threading' vs 'Wax', or wax tiers 'Sugar' / 'Cream' "
    "/ 'Rica'), put that label in the variant's label field. When the prices come from "
    "columns, use the column header as the label.\n"
    "- Put the price text exactly as printed into 'raw' (for example '150/-'), and the "
    "same price as a number into 'amount'.\n"
    "- If the menu says 'Onwards', 'Her Onwards' or similar, set is_starting_price to "
    "true: the figure is a floor, not a fixed price.\n"
    "- If a price is genuinely unreadable, set amount to null. Do not guess, and do not "
    "substitute a similar-looking price.\n"
    "- Set currency to the ISO code for the printed currency mark, not the mark itself "
    "(the rupee symbol is 'INR').\n"
    "- Include the salon's name and tagline only if they are printed on this page."
)

# Additional helper prompts if needed
SERVICE_NORMALIZATION_PROMPT = """
Normalize the following service name for better matching with standard service categories:
Remove extra whitespace, special characters, and convert to lowercase for comparison.
Return only the normalized name.
"""
