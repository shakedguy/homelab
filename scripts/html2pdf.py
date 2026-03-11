#!/usr/bin/python3

from pyhtml2pdf import converter
import sys
from pathlib import Path




def main(html_file_path: str, pdf_file_path: str) -> None:
    
    html_file_path = Path(html_file_path).resolve()
    if not html_file_path.is_file():
        print(f"Error: The file '{html_file_path}' does not exist.")
        sys.exit(1)

    try:
        
        if not pdf_file_path:
            pdf_file_path = str(html_file_path).replace(".html", ".pdf")
        
        
        converter.convert(f"file:///{str(html_file_path)}", pdf_file_path)
        print(f"Successfully converted '{html_file_path}' to '{pdf_file_path}'.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Usage: python script.py <html_file_path> <pdf_file_path>")
        sys.exit(1)

    
    html_file_path = sys.argv[1]
    pdf_file_path = sys.argv[2] if len(sys.argv) == 3 else None

 
    main(html_file_path, pdf_file_path)