"""
Convert PDF to text for testing purposes
"""

import fitz  # PyMuPDF

def extract_pdf_text():
    """Extract text from PDF and save as text file"""
    
    pdf_path = "cv.pdf"
    txt_path = "cv_extracted.txt"
    
    try:
        doc = fitz.open(pdf_path)
        
        text_content = []
        for page_num, page in enumerate(doc):
            print(f"Processing page {page_num + 1}...")
            text = page.get_text("text")
            text_content.append(text)
            print(f"Page {page_num + 1} text length: {len(text)}")
        
        full_text = "\n\n".join(text_content)
        
        # Save to text file
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        doc.close()
        
        print(f"SUCCESS: Text extracted and saved to {txt_path}")
        print(f"Total text length: {len(full_text)} characters")
        print(f"First 1000 characters:")
        print(full_text[:1000])
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_pdf_text()

