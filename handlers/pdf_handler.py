# handlers/pdf_handler.py

import fitz  # PyMuPDF
from PIL import Image
from typing import Optional

class PDFHandler:
    """Handles PDF operations like text and image extraction."""

    def __init__(self, filepath: str):
        """
        Initializes the handler with a path to a PDF file.
        
        Args:
            filepath: The path to the PDF file.
        """
        try:
            self.doc = fitz.open(filepath)
        except Exception as e:
            print(f"Error opening PDF {filepath}: {e}")
            raise
        print(f"PDF '{filepath}' loaded successfully with {len(self.doc)} pages.")

    def extract_full_text(self) -> str:
        """Extracts concatenated text from all pages of the PDF."""
        full_text = ""
        for page in self.doc:
            full_text += page.get_text() + "\n"
        print("Text extraction from PDF complete.")
        return full_text

    def get_pages_as_images(self) -> list[Image.Image]:
        """Converts each page of the PDF into a PIL Image."""
        images = []
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
        print("Converted all PDF pages to images.")
        return images

    @staticmethod
    def convert_image_to_pdf(image_path: str, output_pdf_path: str) -> None:
        """
        Converts a single image file to a single-page PDF.
        
        Args:
            image_path: Path to the input image.
            output_pdf_path: Path to save the output PDF.
        """
        try:
            image = Image.open(image_path)
            # Ensure image is in a format that can be saved as PDF
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            image.save(output_pdf_path, "PDF", resolution=100.0)
            print(f"Image '{image_path}' converted to PDF '{output_pdf_path}'.")
        except Exception as e:
            print(f"Failed to convert image to PDF: {e}")
            raise