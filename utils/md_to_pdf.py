"""
Markdown to PDF Converter

This script:
- Reads a Markdown (.md) file
- Converts it to HTML using the `markdown` library
- Applies basic inline CSS styling
- Generates a PDF using xhtml2pdf (pisa)

Useful for exporting documentation, reports, or guides
into clean, styled PDF format.
"""

import markdown          # Converts Markdown text to HTML
from xhtml2pdf import pisa  # Converts HTML content to PDF
import os                # Handles file system operations


def convert_md_to_pdf(source_md, output_pdf):
    """
    Convert a Markdown file into a styled PDF.

    Parameters:
    - source_md (str): Path to the source Markdown file
    - output_pdf (str): Path where the generated PDF will be saved

    Returns:
    - bool: True if conversion succeeds, False otherwise
    """

    # ---------------------------------------------------------
    # STEP 1: Read Markdown File
    # ---------------------------------------------------------
    with open(source_md, 'r', encoding='utf-8') as f:
        text = f.read()

    # ---------------------------------------------------------
    # STEP 2: Convert Markdown to HTML
    # Extensions:
    # - 'extra' enables additional Markdown features (tables, etc.)
    # - 'codehilite' adds syntax highlighting support
    # ---------------------------------------------------------
    html_content = markdown.markdown(text, extensions=['extra', 'codehilite'])

    # ---------------------------------------------------------
    # STEP 3: Wrap HTML with Basic CSS Styling
    # This improves typography and visual presentation in PDF.
    # ---------------------------------------------------------
    styled_html = f"""
    <html>
    <head>
    <style>
        body {{ font-family: Helvetica, Arial, sans-serif; font-size: 12pt; line-height: 1.5; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #2c3e50; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 20px; border-bottom: 1px solid #ddd; }}
        h3 {{ color: #16a085; margin-top: 15px; }}
        code {{ background-color: #f8f9fa; padding: 2px 5px; border-radius: 3px; font-family: Courier; }}
        pre {{ background-color: #f8f9fa; padding: 10px; border-radius: 5px; border: 1px solid #ddd; }}
        blockquote {{ border-left: 4px solid #3498db; padding-left: 10px; color: #555; }}
    </style>
    </head>
    <body>
    {html_content}
    </body>
    </html>
    """

    # ---------------------------------------------------------
    # STEP 4: Convert Styled HTML to PDF
    # xhtml2pdf (pisa) handles rendering HTML → PDF
    # ---------------------------------------------------------
    with open(output_pdf, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(styled_html, dest=pdf_file)

    # ---------------------------------------------------------
    # STEP 5: Error Handling & Status Reporting
    # ---------------------------------------------------------
    if pisa_status.err:
        print(f"Error converting to PDF: {pisa_status.err}")
        return False
    
    print(f"PDF successfully created at: {output_pdf}")
    return True


# ---------------------------------------------------------
# SCRIPT ENTRY POINT
# Allows the script to be run directly
# ---------------------------------------------------------
if __name__ == "__main__":

    # Source Markdown file path
    # (Currently pointing to a specific artifact location)
    source_path = r"C:\Users\kaust\.gemini\antigravity\brain\3d8b571a-c2d1-4fd6-8d07-ff54a8f5f641\interview_guide.md"

    # Output PDF path
    # (Destination where the generated PDF will be saved)
    output_path = r"d:\FInalYear-Krunal\ODF\Interview_Guide.pdf"
    
    # Verify source file exists before attempting conversion
    if os.path.exists(source_path):
        convert_md_to_pdf(source_path, output_path)
    else:
        print(f"Source file not found: {source_path}")