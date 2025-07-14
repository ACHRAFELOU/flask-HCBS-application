from PyPDF2 import PdfReader
from fpdf import FPDF
from googletrans import Translator

# Define paths
input_pdf_path = "C:/Users/a.elouerghi/Desktop/CMR-27/RFI2022_Zuzek.pdf"
output_pdf_path = "C:/Users/a.elouerghi/Desktop/CMR-27/RFI2022_Zuzek_translated.pdf"

# Initialize translator
translator = Translator()

# Read the original PDF
reader = PdfReader(input_pdf_path)

# Create a new PDF for the translated content
translated_pdf = FPDF()
translated_pdf.add_page()
translated_pdf.set_auto_page_break(auto=True, margin=15)

# Add a Unicode-compatible font
translated_pdf.add_font("DejaVu", fname="C:/Users/a.elouerghi/Desktop/dejavu-sans-ttf-2.36/dejavu-sans-ttf-2.36/ttf/DejaVuSans.ttf", uni=True)
translated_pdf.set_font("DejaVu", size=12)


# Process each page
for page in reader.pages:
    original_text = page.extract_text()
    if original_text.strip():  # Skip empty pages
        # Translate the text to French
        translated_text = translator.translate(original_text, src='en', dest='fr').text

        # Add the translated text to the PDF
        translated_pdf.multi_cell(0, 10, translated_text)

# Save the translated PDF
translated_pdf.output(output_pdf_path)

print(f"Translated PDF saved to: {output_pdf_path}")
