import markdown
from xhtml2pdf import pisa
import os

def convert_md_to_pdf(source_md, output_pdf):
    # Read Markdown
    with open(source_md, 'r', encoding='utf-8') as f:
        text = f.read()

    # Convert to HTML
    html_content = markdown.markdown(text, extensions=['extra', 'codehilite'])

    # Add some basic styling
    styled_html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            pre {{ background-color: #f4f4f4; padding: 10px; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Convert to PDF
    with open(output_pdf, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(styled_html, dest=pdf_file)
        
    if pisa_status.err:
        print(f"Error converting to PDF: {pisa_status.err}")
        return False
        
    print(f"PDF successfully created at: {output_pdf}")
    return True

if __name__ == "__main__":
    # Source is the artifact path
    source_path = r"C:\Users\kaust\.gemini\angravity\brain\3d8b571a-c2d1-4fd6-8d07-ff54a8f5f641\interview_guide.md"
    
    # Output to the project directory
    output_path = r"d:\FInalYear-Krunal\ODF\Interview_Guide.pdf"

    if os.path.exists(source_path):
        convert_md_to_pdf(source_path, output_path)
    else:
        print(f"Source file not found: {source_path}")
